//go:build windows

package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/lxn/walk"
	. "github.com/lxn/walk/declarative"
)

type queueModel struct {
	walk.TableModelBase
	items []*QueueItem
}

func (model *queueModel) RowCount() int { return len(model.items) }

func (model *queueModel) Value(row, column int) interface{} {
	if row < 0 || row >= len(model.items) {
		return ""
	}
	item := model.items[row]
	switch column {
	case 0:
		return item.Name
	case 1:
		return item.RecordingAt.Format("2006-01-02 15:04:05")
	case 2:
		return item.DateSource
	case 3:
		return formatSize(item.Size)
	case 4:
		if item.Error != "" {
			return item.Status + "：" + item.Error
		}
		return item.Status
	default:
		return ""
	}
}

func formatSize(size int64) string {
	const mb = 1024 * 1024
	if size >= mb {
		return fmt.Sprintf("%.1f MB", float64(size)/mb)
	}
	return fmt.Sprintf("%.1f KB", float64(size)/1024)
}

var (
	mainWindow       *walk.MainWindow
	apiURLInput      *walk.LineEdit
	supabaseInput    *walk.LineEdit
	supabaseKeyInput *walk.LineEdit
	topicInput       *walk.LineEdit
	tableView        *walk.TableView
	progressBar      *walk.ProgressBar
	statusLabel      *walk.Label
	logBox           *walk.TextEdit
	selectButton     *walk.PushButton
	uploadButton     *walk.PushButton
	clearButton      *walk.PushButton
	cancelButton     *walk.PushButton
	model            = &queueModel{}
	configPath       string
	cancelUpload     context.CancelFunc
)

func applicationDirectory() string {
	executable, err := os.Executable()
	if err == nil {
		return filepath.Dir(executable)
	}
	directory, _ := os.Getwd()
	return directory
}

func appendLog(message string) {
	if mainWindow == nil || logBox == nil {
		return
	}
	mainWindow.Synchronize(func() {
		logBox.AppendText(fmt.Sprintf("[%s] %s\r\n", time.Now().Format("15:04:05"), message))
	})
}

func configFromForm() (AppConfig, error) {
	topicID, err := strconv.Atoi(strings.TrimSpace(topicInput.Text()))
	if err != nil {
		return AppConfig{}, fmt.Errorf("Telegram Topic ID 格式錯誤")
	}
	config := AppConfig{
		APIURL: strings.TrimSpace(apiURLInput.Text()), SupabaseURL: strings.TrimSpace(supabaseInput.Text()),
		SupabaseKey: strings.TrimSpace(supabaseKeyInput.Text()), TopicID: topicID,
	}
	if err := validateConfig(config); err != nil {
		return AppConfig{}, err
	}
	return config, nil
}

func persistFormConfig(showMessage bool) (AppConfig, bool) {
	config, err := configFromForm()
	if err != nil {
		walk.MsgBox(mainWindow, "設定不完整", err.Error(), walk.MsgBoxIconWarning)
		return AppConfig{}, false
	}
	if err := saveConfig(configPath, config); err != nil {
		walk.MsgBox(mainWindow, "儲存失敗", err.Error(), walk.MsgBoxIconError)
		return AppConfig{}, false
	}
	if showMessage {
		appendLog("💾 設定已儲存在程式旁的 " + configName)
	}
	return config, true
}

func setBusy(busy bool) {
	selectButton.SetEnabled(!busy)
	uploadButton.SetEnabled(!busy && len(model.items) > 0)
	clearButton.SetEnabled(!busy && len(model.items) > 0)
	cancelButton.SetEnabled(busy)
}

func refreshQueue() {
	model.PublishRowsReset()
	uploadButton.SetEnabled(len(model.items) > 0)
	clearButton.SetEnabled(len(model.items) > 0)
	statusLabel.SetText(fmt.Sprintf("已選取 %d 個檔案，分布於 %d 個日期", len(model.items), countDates(model.items)))
}

func countDates(items []*QueueItem) int {
	dates := map[string]struct{}{}
	for _, item := range items {
		dates[recordingDate(item)] = struct{}{}
	}
	return len(dates)
}

func selectFiles() {
	dialog := new(walk.FileDialog)
	dialog.Title = "選擇 SHJHS 錄音證據（可多選）"
	dialog.Filter = "錄音檔 (*.mp3;*.wav;*.m4a;*.aac;*.ogg;*.flac;*.amr;*.wma;*.3gp;*.3gpp)|*.mp3;*.wav;*.m4a;*.aac;*.ogg;*.flac;*.amr;*.wma;*.3gp;*.3gpp|所有檔案 (*.*)|*.*"
	ok, err := dialog.ShowOpenMultiple(mainWindow)
	if err != nil {
		walk.MsgBox(mainWindow, "選取失敗", err.Error(), walk.MsgBoxIconError)
		return
	}
	if !ok || len(dialog.FilePaths) == 0 {
		return
	}
	existing := map[string]bool{}
	for _, item := range model.items {
		existing[strings.ToLower(item.Path)] = true
	}
	added := 0
	for _, path := range dialog.FilePaths {
		if existing[strings.ToLower(path)] {
			continue
		}
		item, itemErr := makeQueueItem(path)
		if itemErr != nil {
			appendLog("❌ 無法加入 " + filepath.Base(path) + "：" + itemErr.Error())
			continue
		}
		model.items = append(model.items, item)
		existing[strings.ToLower(path)] = true
		added++
	}
	sortQueue(model.items)
	refreshQueue()
	appendLog(fmt.Sprintf("📂 新增 %d 個檔案；已依錄音日期排序。", added))
	for _, item := range model.items {
		appendLog(fmt.Sprintf("  %s → %s（%s）", item.Name, recordingDate(item), item.DateSource))
	}
}

func clearQueue() {
	model.items = nil
	progressBar.SetValue(0)
	refreshQueue()
	statusLabel.SetText("尚未選取檔案")
	appendLog("🧹 已清除上傳清單。")
}

func beginUpload() {
	config, ok := persistFormConfig(false)
	if !ok || len(model.items) == 0 {
		return
	}
	ctx, cancel := context.WithCancel(context.Background())
	cancelUpload = cancel
	setBusy(true)
	progressBar.SetValue(0)
	appendLog(fmt.Sprintf("🚀 開始處理 %d 個檔案。", len(model.items)))

	go func() {
		defer func() {
			mainWindow.Synchronize(func() {
				setBusy(false)
				cancelUpload = nil
			})
		}()
		client := &APIClient{Config: config}
		completed, failed := 0, 0
		for index, item := range model.items {
			if ctx.Err() != nil {
				appendLog("⏹️ 已取消後續上傳。")
				break
			}
			if item.Status == "完成" || item.Status == "已存在，略過" {
				completed++
				continue
			}
			item.Error = ""
			appendLog(fmt.Sprintf("⏳ [%d/%d] %s → %s", index+1, len(model.items), item.Name, recordingDate(item)))
			mainWindow.Synchronize(func() {
				model.PublishRowsChanged(index, index)
				statusLabel.SetText(fmt.Sprintf("處理中 %d/%d：%s", index+1, len(model.items), item.Name))
			})
			err := client.processItem(ctx, item, func(read, total int64) {
				percentage := 0
				if total > 0 {
					percentage = int(float64(read) / float64(total) * 100)
				}
				mainWindow.Synchronize(func() { progressBar.SetValue(percentage) })
			})
			if err != nil {
				item.Status = "失敗，可重試"
				item.Error = err.Error()
				failed++
				appendLog("❌ " + item.Name + "：" + err.Error())
			} else {
				completed++
				if item.Status == "已存在，略過" {
					appendLog("⏭️ 已有相同 SHA-256，略過：" + item.Name)
				} else {
					appendLog(fmt.Sprintf("✅ 已歸檔至 %s：%s", recordingDate(item), item.Name))
				}
			}
			mainWindow.Synchronize(func() {
				model.PublishRowsChanged(index, index)
				progressBar.SetValue(100)
			})
		}
		mainWindow.Synchronize(func() {
			statusLabel.SetText(fmt.Sprintf("完成 %d，失敗 %d；失敗項目可再次按上傳重試", completed, failed))
		})
		appendLog(fmt.Sprintf("🏁 作業結束：完成／略過 %d，失敗 %d。", completed, failed))
	}()
}

func loadInitialConfig() AppConfig {
	directory := applicationDirectory()
	configPath = filepath.Join(directory, configName)
	config, err := loadConfig(configPath)
	if err != nil {
		config = AppConfig{APIURL: defaultAPIURL}
	}
	if config.SupabaseURL == "" || config.SupabaseKey == "" {
		_ = loadLegacyConfig(filepath.Join(directory, "config.json"), &config)
	}
	return config
}

func main() {
	config := loadInitialConfig()
	err := MainWindow{
		AssignTo: &mainWindow,
		Title:    "SHJHS 輔導錄音自動歸檔工具",
		MinSize:  Size{Width: 980, Height: 720},
		Layout:   VBox{Margins: Margins{Left: 12, Top: 12, Right: 12, Bottom: 12}},
		Children: []Widget{
			Label{Text: "SHJHS 輔導紀錄中心｜錄音證據批次上傳", Font: Font{PointSize: 15, Bold: true}},
			Label{Text: "日期判斷：優先採檔名日期；否則取 Windows 建立／修改時間中較早者。每個檔案會自動寫入網站對應日期。"},
			GroupBox{
				Title: "連線設定（只儲存在本機）", Layout: Grid{Columns: 4},
				Children: []Widget{
					Label{Text: "SHJHS Render API"}, LineEdit{AssignTo: &apiURLInput, Text: config.APIURL, ColumnSpan: 3},
					Label{Text: "Supabase URL"}, LineEdit{AssignTo: &supabaseInput, Text: config.SupabaseURL, ColumnSpan: 3},
					Label{Text: "Supabase Key"}, LineEdit{AssignTo: &supabaseKeyInput, Text: config.SupabaseKey, PasswordMode: true, ColumnSpan: 3},
					Label{Text: "Telegram Topic ID"}, LineEdit{AssignTo: &topicInput, Text: func() string {
						if config.TopicID > 0 {
							return strconv.Itoa(config.TopicID)
						}
						return ""
					}()},
					PushButton{Text: "💾 儲存設定", OnClicked: func() { persistFormConfig(true) }, ColumnSpan: 2},
				},
			},
			Composite{Layout: HBox{}, Children: []Widget{
				PushButton{AssignTo: &selectButton, Text: "📂 選取多個錄音檔", OnClicked: selectFiles},
				PushButton{AssignTo: &clearButton, Text: "清除清單", Enabled: false, OnClicked: clearQueue},
				HSpacer{},
				PushButton{AssignTo: &uploadButton, Text: "🚀 自動分日期並全部上傳", Enabled: false, OnClicked: beginUpload},
				PushButton{AssignTo: &cancelButton, Text: "停止", Enabled: false, OnClicked: func() {
					if cancelUpload != nil {
						cancelUpload()
					}
				}},
			}},
			Label{AssignTo: &statusLabel, Text: "尚未選取檔案"},
			TableView{
				AssignTo: &tableView, Model: model, AlternatingRowBG: true, LastColumnStretched: true,
				Columns: []TableViewColumn{
					{Title: "檔名", Width: 260}, {Title: "判定日期時間", Width: 145}, {Title: "日期來源", Width: 120},
					{Title: "大小", Width: 85}, {Title: "狀態／錯誤", Width: 280},
				},
			},
			Label{Text: "目前檔案進度"}, ProgressBar{AssignTo: &progressBar, MinValue: 0, MaxValue: 100},
			TextEdit{AssignTo: &logBox, ReadOnly: true, VScroll: true, MinSize: Size{Height: 150}},
		},
	}.Create()
	if err != nil {
		log.Fatal(err)
	}
	appendLog("✅ 工具已啟動。設定檔與憑證不會寫入 EXE 或 Git。")
	if config.SupabaseURL != "" && config.SupabaseKey != "" && config.TopicID == 0 {
		appendLog("ℹ️ 已從舊 config.json 匯入 Supabase 設定；請補填 Telegram Topic ID。")
	}
	mainWindow.Run()
}

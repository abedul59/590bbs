package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"
)

const (
	defaultAPIURL = "https://five90bbs-telegram-shjhs-api.onrender.com"
	configName    = "shjhs_uploader_config.json"
)

type AppConfig struct {
	APIURL      string `json:"api_url"`
	SupabaseURL string `json:"supabase_url"`
	SupabaseKey string `json:"supabase_key"`
	TopicID     int    `json:"topic_id"`
}

type QueueItem struct {
	Path         string
	Name         string
	Size         int64
	RecordingAt  time.Time
	DateSource   string
	Hash         string
	Status       string
	Error        string
	MessageID    int64
	TelegramURL  string
	RemoteHash   string
	UploadedName string
}

type UploadResult struct {
	Success      bool   `json:"success"`
	TelegramLink string `json:"telegram_link"`
	MessageID    int64  `json:"message_id"`
	FileHash     string `json:"file_hash"`
	Detail       string `json:"detail"`
}

type EvidenceRecord struct {
	LogDate     string `json:"log_date"`
	Title       string `json:"title"`
	FileName    string `json:"file_name"`
	TelegramURL string `json:"telegram_url"`
	MessageID   int64  `json:"message_id"`
	FileHash    string `json:"file_hash"`
}

var filenameDatePatterns = []*regexp.Regexp{
	regexp.MustCompile(`(?i)(20\d{2})[-_.年]?(0[1-9]|1[0-2])[-_.月]?(0[1-9]|[12]\d|3[01])(?:日)?[T _.-]?([01]\d|2[0-3])?[:_.-]?([0-5]\d)?[:_.-]?([0-5]\d)?`),
	regexp.MustCompile(`(?i)(20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(?:[_T.-]?([01]\d|2[0-3])([0-5]\d)([0-5]\d)?)?`),
}

func parseFilenameDate(name string, location *time.Location) (time.Time, bool) {
	base := strings.TrimSuffix(filepath.Base(name), filepath.Ext(name))
	for _, pattern := range filenameDatePatterns {
		match := pattern.FindStringSubmatch(base)
		if len(match) == 0 {
			continue
		}
		year, _ := strconv.Atoi(match[1])
		month, _ := strconv.Atoi(match[2])
		day, _ := strconv.Atoi(match[3])
		hour, minute, second := 12, 0, 0
		if len(match) > 4 && match[4] != "" {
			hour, _ = strconv.Atoi(match[4])
		}
		if len(match) > 5 && match[5] != "" {
			minute, _ = strconv.Atoi(match[5])
		}
		if len(match) > 6 && match[6] != "" {
			second, _ = strconv.Atoi(match[6])
		}
		parsed := time.Date(year, time.Month(month), day, hour, minute, second, 0, location)
		if parsed.Year() == year && int(parsed.Month()) == month && parsed.Day() == day {
			return parsed, true
		}
	}
	return time.Time{}, false
}

func detectRecordingTime(path string) (time.Time, string, error) {
	if parsed, ok := parseFilenameDate(filepath.Base(path), time.Local); ok {
		return parsed, "檔名日期", nil
	}
	info, err := os.Stat(path)
	if err != nil {
		return time.Time{}, "", err
	}
	modified := info.ModTime().In(time.Local)
	if created, ok := platformCreationTime(path); ok && !created.IsZero() {
		created = created.In(time.Local)
		// Copying a recording often makes CreationTime newer while preserving the
		// original LastWriteTime. The earlier timestamp is normally the recording.
		if created.Before(modified) {
			return created, "Windows 建立時間（較早）", nil
		}
		return modified, "檔案修改時間（較早）", nil
	}
	return modified, "檔案修改時間", nil
}

func makeQueueItem(path string) (*QueueItem, error) {
	info, err := os.Stat(path)
	if err != nil {
		return nil, err
	}
	if info.IsDir() {
		return nil, errors.New("不支援資料夾")
	}
	recordedAt, source, err := detectRecordingTime(path)
	if err != nil {
		return nil, err
	}
	return &QueueItem{
		Path:        path,
		Name:        filepath.Base(path),
		Size:        info.Size(),
		RecordingAt: recordedAt,
		DateSource:  source,
		Status:      "等待上傳",
	}, nil
}

func sortQueue(items []*QueueItem) {
	sort.SliceStable(items, func(i, j int) bool {
		if items[i].RecordingAt.Equal(items[j].RecordingAt) {
			return strings.ToLower(items[i].Name) < strings.ToLower(items[j].Name)
		}
		return items[i].RecordingAt.Before(items[j].RecordingAt)
	})
}

func recordingDate(item *QueueItem) string {
	return item.RecordingAt.Format("2006-01-02")
}

func uploadFileName(item *QueueItem) string {
	clean := strings.NewReplacer("/", "_", `\`, "_", ":", "-").Replace(item.Name)
	return fmt.Sprintf("%s_%s_%s", item.RecordingAt.Format("2006-01-02"), item.RecordingAt.Format("150405"), clean)
}

func sha256File(path string) (string, error) {
	file, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer file.Close()
	hash := sha256.New()
	if _, err := io.Copy(hash, file); err != nil {
		return "", err
	}
	return hex.EncodeToString(hash.Sum(nil)), nil
}

func normalizeBaseURL(raw string) (string, error) {
	raw = strings.TrimSpace(raw)
	parsed, err := url.Parse(raw)
	localHTTP := parsed.Scheme == "http" && (parsed.Hostname() == "127.0.0.1" || parsed.Hostname() == "localhost")
	if err != nil || (parsed.Scheme != "https" && !localHTTP) || parsed.Host == "" {
		return "", errors.New("網址必須是有效的 https:// 網址")
	}
	return strings.TrimRight(raw, "/"), nil
}

func validateConfig(config AppConfig) error {
	if _, err := normalizeBaseURL(config.APIURL); err != nil {
		return fmt.Errorf("Render API：%w", err)
	}
	if _, err := normalizeBaseURL(config.SupabaseURL); err != nil {
		return fmt.Errorf("Supabase URL：%w", err)
	}
	if strings.TrimSpace(config.SupabaseKey) == "" {
		return errors.New("Supabase Key 不能空白")
	}
	if config.TopicID <= 0 {
		return errors.New("Telegram Topic ID 必須大於 0")
	}
	return nil
}

func saveConfig(path string, config AppConfig) error {
	data, err := json.MarshalIndent(config, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, data, 0600)
}

func loadConfig(path string) (AppConfig, error) {
	config := AppConfig{APIURL: defaultAPIURL}
	data, err := os.ReadFile(path)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return config, nil
		}
		return config, err
	}
	if err := json.Unmarshal(data, &config); err != nil {
		return config, err
	}
	if strings.TrimSpace(config.APIURL) == "" {
		config.APIURL = defaultAPIURL
	}
	return config, nil
}

func loadLegacyConfig(path string, config *AppConfig) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	var legacy struct {
		SupabaseURL string `json:"supabase_url"`
		SupabaseKey string `json:"supabase_key"`
	}
	if err := json.Unmarshal(data, &legacy); err != nil {
		return err
	}
	if config.SupabaseURL == "" {
		config.SupabaseURL = legacy.SupabaseURL
	}
	if config.SupabaseKey == "" {
		config.SupabaseKey = legacy.SupabaseKey
	}
	return nil
}

type APIClient struct {
	Config     AppConfig
	HTTPClient *http.Client
}

func (client *APIClient) httpClient() *http.Client {
	if client.HTTPClient != nil {
		return client.HTTPClient
	}
	return &http.Client{Timeout: 2 * time.Hour}
}

func (client *APIClient) evidenceByHash(ctx context.Context, hash string) (bool, error) {
	base, err := normalizeBaseURL(client.Config.SupabaseURL)
	if err != nil {
		return false, err
	}
	query := url.Values{}
	query.Set("file_hash", "eq."+hash)
	query.Set("select", "id")
	query.Set("limit", "1")
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, base+"/rest/v1/evidence_logs?"+query.Encode(), nil)
	if err != nil {
		return false, err
	}
	client.addSupabaseHeaders(req)
	response, err := client.httpClient().Do(req)
	if err != nil {
		return false, err
	}
	defer response.Body.Close()
	if response.StatusCode >= 300 {
		body, _ := io.ReadAll(io.LimitReader(response.Body, 2048))
		return false, fmt.Errorf("Supabase 去重查詢失敗（HTTP %d）：%s", response.StatusCode, strings.TrimSpace(string(body)))
	}
	var rows []map[string]any
	if err := json.NewDecoder(response.Body).Decode(&rows); err != nil {
		return false, err
	}
	return len(rows) > 0, nil
}

func (client *APIClient) insertEvidence(ctx context.Context, record EvidenceRecord) error {
	base, err := normalizeBaseURL(client.Config.SupabaseURL)
	if err != nil {
		return err
	}
	payload, err := json.Marshal(record)
	if err != nil {
		return err
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, base+"/rest/v1/evidence_logs", bytes.NewReader(payload))
	if err != nil {
		return err
	}
	client.addSupabaseHeaders(req)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Prefer", "return=minimal")
	response, err := client.httpClient().Do(req)
	if err != nil {
		return err
	}
	defer response.Body.Close()
	if response.StatusCode >= 300 {
		body, _ := io.ReadAll(io.LimitReader(response.Body, 4096))
		return fmt.Errorf("Supabase 寫入失敗（HTTP %d）：%s", response.StatusCode, strings.TrimSpace(string(body)))
	}
	return nil
}

func (client *APIClient) addSupabaseHeaders(req *http.Request) {
	req.Header.Set("apikey", client.Config.SupabaseKey)
	req.Header.Set("Authorization", "Bearer "+client.Config.SupabaseKey)
}

type progressReader struct {
	reader   io.Reader
	total    int64
	read     int64
	callback func(int64, int64)
}

func (reader *progressReader) Read(buffer []byte) (int, error) {
	count, err := reader.reader.Read(buffer)
	reader.read += int64(count)
	if reader.callback != nil {
		reader.callback(reader.read, reader.total)
	}
	return count, err
}

func (client *APIClient) uploadEvidence(ctx context.Context, item *QueueItem, progress func(int64, int64)) (UploadResult, error) {
	apiURL, err := normalizeBaseURL(client.Config.APIURL)
	if err != nil {
		return UploadResult{}, err
	}
	file, err := os.Open(item.Path)
	if err != nil {
		return UploadResult{}, err
	}
	defer file.Close()

	pipeReader, pipeWriter := io.Pipe()
	multipartWriter := multipart.NewWriter(pipeWriter)
	item.UploadedName = uploadFileName(item)
	go func() {
		defer pipeWriter.Close()
		part, createErr := multipartWriter.CreateFormFile("file", item.UploadedName)
		if createErr != nil {
			_ = pipeWriter.CloseWithError(createErr)
			return
		}
		wrapped := &progressReader{reader: file, total: item.Size, callback: progress}
		if _, copyErr := io.Copy(part, wrapped); copyErr != nil {
			_ = pipeWriter.CloseWithError(copyErr)
			return
		}
		if writeErr := multipartWriter.WriteField("topic_id", strconv.Itoa(client.Config.TopicID)); writeErr != nil {
			_ = pipeWriter.CloseWithError(writeErr)
			return
		}
		if closeErr := multipartWriter.Close(); closeErr != nil {
			_ = pipeWriter.CloseWithError(closeErr)
		}
	}()

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, apiURL+"/upload/", pipeReader)
	if err != nil {
		return UploadResult{}, err
	}
	req.Header.Set("Content-Type", multipartWriter.FormDataContentType())
	response, err := client.httpClient().Do(req)
	if err != nil {
		return UploadResult{}, err
	}
	defer response.Body.Close()
	var result UploadResult
	if err := json.NewDecoder(io.LimitReader(response.Body, 1<<20)).Decode(&result); err != nil {
		return result, fmt.Errorf("Render API 回應無法解析（HTTP %d）：%w", response.StatusCode, err)
	}
	if response.StatusCode >= 300 || !result.Success {
		if result.Detail == "" {
			result.Detail = fmt.Sprintf("HTTP %d", response.StatusCode)
		}
		return result, errors.New(result.Detail)
	}
	if result.MessageID <= 0 || result.TelegramLink == "" {
		return result, errors.New("Render API 未回傳 Telegram 訊息編號或連結")
	}
	return result, nil
}

func (client *APIClient) processItem(ctx context.Context, item *QueueItem, progress func(int64, int64)) error {
	if item.Hash == "" {
		item.Status = "計算 SHA-256"
		hash, err := sha256File(item.Path)
		if err != nil {
			return err
		}
		item.Hash = hash
	}

	if item.MessageID == 0 {
		item.Status = "檢查重複"
		duplicate, err := client.evidenceByHash(ctx, item.Hash)
		if err != nil {
			return err
		}
		if duplicate {
			item.Status = "已存在，略過"
			return nil
		}

		item.Status = "上傳 Telegram"
		result, err := client.uploadEvidence(ctx, item, progress)
		if err != nil {
			return err
		}
		if result.FileHash != "" && !strings.EqualFold(result.FileHash, item.Hash) {
			return fmt.Errorf("遠端 SHA-256 與本機不一致（遠端 %s）", result.FileHash)
		}
		item.MessageID = result.MessageID
		item.TelegramURL = result.TelegramLink
		item.RemoteHash = result.FileHash
	}

	item.Status = "寫入日期索引"
	title := strings.TrimSuffix(item.UploadedName, filepath.Ext(item.UploadedName))
	record := EvidenceRecord{
		LogDate: recordingDate(item), Title: title, FileName: item.UploadedName,
		TelegramURL: item.TelegramURL, MessageID: item.MessageID, FileHash: item.Hash,
	}
	if err := client.insertEvidence(ctx, record); err != nil {
		return err
	}
	item.Status = "完成"
	item.Error = ""
	return nil
}

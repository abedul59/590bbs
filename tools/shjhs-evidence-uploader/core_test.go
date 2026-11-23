package main

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"
	"time"
)

func TestParseFilenameDate(t *testing.T) {
	tests := []struct {
		name string
		want string
	}{
		{"REC_20261123_083045.m4a", "2026-11-23 08:30:45"},
		{"2026-11-22 14.05 meeting.mp3", "2026-11-22 14:05:00"},
		{"錄音_2026年11月21日.wav", "2026-11-21 12:00:00"},
	}
	for _, test := range tests {
		got, ok := parseFilenameDate(test.name, time.Local)
		if !ok {
			t.Fatalf("expected %q to contain a date", test.name)
		}
		if formatted := got.Format("2006-01-02 15:04:05"); formatted != test.want {
			t.Fatalf("%q: got %s, want %s", test.name, formatted, test.want)
		}
	}
	if _, ok := parseFilenameDate("recording_without_date.mp3", time.Local); ok {
		t.Fatal("unexpected date match")
	}
}

func TestDetectRecordingTimeFallsBackToModificationTime(t *testing.T) {
	path := filepath.Join(t.TempDir(), "recording.m4a")
	if err := os.WriteFile(path, []byte("audio"), 0600); err != nil {
		t.Fatal(err)
	}
	want := time.Date(2025, 7, 3, 9, 8, 7, 0, time.Local)
	if err := os.Chtimes(path, want, want); err != nil {
		t.Fatal(err)
	}
	got, source, err := detectRecordingTime(path)
	if err != nil {
		t.Fatal(err)
	}
	// Windows exposes a creation timestamp for the temporary file. Since the
	// test moves LastWriteTime into the past, the detector correctly labels it
	// as the earlier timestamp; Unix has no creation time and uses the shorter
	// fallback label. The detected instant is the behaviour that matters here.
	if (source != "檔案修改時間" && source != "檔案修改時間（較早）") || !got.Equal(want) {
		t.Fatalf("got %s (%s), want %s", got, source, want)
	}
}

func TestUploadFileName(t *testing.T) {
	item := &QueueItem{Name: `voice:note.m4a`, RecordingAt: time.Date(2026, 11, 23, 8, 30, 45, 0, time.Local)}
	if got, want := uploadFileName(item), "2026-11-23_083045_voice-note.m4a"; got != want {
		t.Fatalf("got %q, want %q", got, want)
	}
}

func TestProcessItemUploadsAndIndexesDetectedDate(t *testing.T) {
	var inserted EvidenceRecord
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		switch {
		case request.Method == http.MethodGet && request.URL.Path == "/rest/v1/evidence_logs":
			writer.Header().Set("Content-Type", "application/json")
			_, _ = writer.Write([]byte("[]"))
		case request.Method == http.MethodPost && request.URL.Path == "/upload/":
			if err := request.ParseMultipartForm(1 << 20); err != nil {
				http.Error(writer, err.Error(), http.StatusBadRequest)
				return
			}
			file, header, err := request.FormFile("file")
			if err != nil {
				http.Error(writer, err.Error(), http.StatusBadRequest)
				return
			}
			defer file.Close()
			_, _ = io.Copy(io.Discard, file)
			if header.Filename != "2026-11-20_071500_REC_20261120_071500.m4a" || request.FormValue("topic_id") != "45" {
				http.Error(writer, "unexpected upload metadata", http.StatusBadRequest)
				return
			}
			writer.Header().Set("Content-Type", "application/json")
			_, _ = writer.Write([]byte(`{"success":true,"telegram_link":"https://t.me/c/1/99","message_id":99}`))
		case request.Method == http.MethodPost && request.URL.Path == "/rest/v1/evidence_logs":
			if err := json.NewDecoder(request.Body).Decode(&inserted); err != nil {
				http.Error(writer, err.Error(), http.StatusBadRequest)
				return
			}
			writer.WriteHeader(http.StatusCreated)
		default:
			http.NotFound(writer, request)
		}
	}))
	defer server.Close()

	path := filepath.Join(t.TempDir(), "REC_20261120_071500.m4a")
	if err := os.WriteFile(path, []byte("fake audio content"), 0600); err != nil {
		t.Fatal(err)
	}
	item, err := makeQueueItem(path)
	if err != nil {
		t.Fatal(err)
	}
	client := &APIClient{Config: AppConfig{APIURL: server.URL, SupabaseURL: server.URL, SupabaseKey: "test", TopicID: 45}, HTTPClient: server.Client()}
	if err := client.processItem(context.Background(), item, nil); err != nil {
		t.Fatal(err)
	}
	if item.Status != "完成" {
		t.Fatalf("unexpected status: %s", item.Status)
	}
	if inserted.LogDate != "2026-11-20" || inserted.MessageID != 99 || inserted.FileHash == "" {
		t.Fatalf("unexpected evidence row: %+v", inserted)
	}
}

func TestProcessItemSkipsDuplicateHash(t *testing.T) {
	uploadCalled := false
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.Method == http.MethodGet && request.URL.Path == "/rest/v1/evidence_logs" {
			writer.Header().Set("Content-Type", "application/json")
			_, _ = writer.Write([]byte(`[{"id":"existing"}]`))
			return
		}
		uploadCalled = true
		http.Error(writer, "unexpected", http.StatusInternalServerError)
	}))
	defer server.Close()

	path := filepath.Join(t.TempDir(), "20261119_recording.wav")
	if err := os.WriteFile(path, []byte("same content"), 0600); err != nil {
		t.Fatal(err)
	}
	item, err := makeQueueItem(path)
	if err != nil {
		t.Fatal(err)
	}
	client := &APIClient{Config: AppConfig{APIURL: server.URL, SupabaseURL: server.URL, SupabaseKey: "test", TopicID: 45}, HTTPClient: server.Client()}
	if err := client.processItem(context.Background(), item, nil); err != nil {
		t.Fatal(err)
	}
	if uploadCalled || item.Status != "已存在，略過" {
		t.Fatalf("duplicate was not skipped: called=%v status=%s", uploadCalled, item.Status)
	}
}

# services/inference_gateway/main.go

package main

import (
    "bytes"
    "context"
    "encoding/json"
    "io"
    "log"
    "net/http"
    "os"
    "time"
)

// Minimal inference gateway that accepts assistant chat requests and proxies to Ollama

var ollamaURL = "http://ollama.internal:11434/v1/generate"

func main() {
    http.HandleFunc("/v1/assistant/chat", handleChat)
    log.Println("Inference gateway starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}

type ChatRequest struct {
    SessionID  string                 `json:"session_id"`
    UserID     string                 `json:"user_id"`
    TenantID   string                 `json:"tenant_id"`
    Prompt     string                 `json:"prompt"`
    ContextHint map[string]interface{} `json:"context_hint"`
}

func handleChat(w http.ResponseWriter, r *http.Request) {
    var req ChatRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "bad request", http.StatusBadRequest)
        return
    }

    // For this stub, build a simple prompt and forward to Ollama
    prompt := "System: You are a sales assistant. Use the following user prompt:\n" + req.Prompt
    payload := map[string]interface{}{
        "model": "Qwen3.5-9B-DeepSeek",
        "prompt": prompt,
        "max_tokens": 512,
        "temperature": 0.0,
    }

    ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
    defer cancel()

    b, _ := json.Marshal(payload)
    httpReq, _ := http.NewRequestWithContext(ctx, "POST", ollamaURL, bytes.NewReader(b))
    httpReq.Header.Set("Content-Type", "application/json")
    httpReq.Header.Set("Authorization", "Bearer "+os.Getenv("OLLAMA_SVC_TOKEN"))

    resp, err := http.DefaultClient.Do(httpReq)
    if err != nil {
        http.Error(w, "failed to reach ollama", http.StatusBadGateway)
        return
    }
    defer resp.Body.Close()

    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(resp.StatusCode)
    io.Copy(w, resp.Body)
}

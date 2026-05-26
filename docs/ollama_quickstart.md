# Quickstart: Run local Ollama dev container

1. Install Docker Desktop.
2. Pull Ollama dev image (example): docker pull ollama/ollama:latest
3. Run Ollama with model path mounted pointing to Qwen3.5-9B-DeepSeek GGUF file.

Example:

docker run --gpus all -p 11434:11434 -v /models:/models ollama/ollama:latest ollama serve --model /models/Qwen3.5-9B-DeepSeek.gguf

Note: Adjust for Ollama runtime requirements and licensing.

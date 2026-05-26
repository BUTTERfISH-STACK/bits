module.exports = {
  apps: [
    {
      name: "inference-gateway",
      script: "./main.go",
      interpreter: "none",
      exec_mode: "fork",
      instances: 1,
      env: {
        OLLAMA_SVC_TOKEN: "",
      }
    }
  ]
}

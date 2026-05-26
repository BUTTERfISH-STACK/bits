# Vellon CV AI - Setup Instructions

1. Copy .env.example to .env and fill in values.
2. Install dependencies: npm install
3. Generate Prisma client: npm run prisma:generate
4. Run migrations: npm run prisma:migrate
5. Start dev server: npm run dev
6. Ensure Ollama is installed and running locally. Run: npm run pull-ollama-model

Ollama commands used:
- ollama pull qwen2.5:7b
- ollama daemon

Deployment:
- Set environment variables in Vercel dashboard
- Build and deploy

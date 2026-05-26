const basePrompt = `You are Vellon CV AI assistant. Rewrite the given CV content to be professional, concise, ATS-friendly, and tailored to the provided job description. Output a JSON object with keys: {"title":"...","summary":"...","sections": [{"heading":"...","content":"..."}], "atsKeywords": ["..."], "notes":"..." } Only output valid JSON.`

export function buildCVRewritePrompt(cvText: string, jobDesc: string, tone = 'professional') {
  return `${basePrompt}\n\nJob Description:\n${jobDesc}\n\nCV:\n${cvText}\n\nTone: ${tone}`
}

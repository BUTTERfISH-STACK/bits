import prisma from '../../lib/prisma'
import { v4 as uuidv4 } from 'uuid'

type Job = {
  id: string
  userId?: string
  type: 'rewrite' | 'ats' | 'cover'
  payload: any
  model?: string
  status: 'pending' | 'running' | 'failed' | 'completed'
  attempts: number
  result?: any
}

const MAX_CONCURRENCY = 2
let running = 0
const queue: Job[] = []

export function enqueue(job: Omit<Job, 'id' | 'status' | 'attempts'>) {
  const j: Job = { id: uuidv4(), status: 'pending', attempts: 0, ...job }
  queue.push(j)
  processQueue()
  return j.id
}

async function processQueue() {
  if (running >= MAX_CONCURRENCY) return
  const job = queue.shift()
  if (!job) return
  running++
  job.status = 'running'
  await prisma.cVVersion.create({ data: { cvId: job.payload.cvId || '', html: '', note: `job:${job.id}` } }).catch(()=>null)
  try {
    const res = await require('./ollamaClient').generate(job.payload.prompt, job.model)
    job.status = 'completed'
    job.result = res
    await prisma.cVVersion.create({ data: { cvId: job.payload.cvId || '', html: res.html || JSON.stringify(res), note: job.type } })
  } catch (e) {
    job.attempts += 1
    if (job.attempts < 3) {
      job.status = 'pending'
      queue.push(job)
    } else {
      job.status = 'failed'
    }
  }
  running--
  processQueue()
}

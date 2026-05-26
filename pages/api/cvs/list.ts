import { NextApiRequest, NextApiResponse } from 'next'
import prisma from '../../../lib/prisma'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') return res.status(405).end()
  const cvs = await prisma.cV.findMany({ take: 10, orderBy: { updatedAt: 'desc' } })
  res.json(cvs)
}

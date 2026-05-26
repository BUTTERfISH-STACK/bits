import NextAuth from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { compare } from 'bcryptjs'
import prisma from '../../../lib/prisma'

export default NextAuth({
  providers: [
    CredentialsProvider({
      name: 'Email',
      credentials: { email: { label: 'Email', type: 'email' }, password: { label: 'Password', type: 'password' } },
      async authorize(credentials) {
        if (!credentials?.email) return null
        const user = await prisma.user.findUnique({ where: { email: credentials.email } })
        if (user) return { id: user.id, email: user.email, name: user.name }
        // fallback: create user for simplicity
        const created = await prisma.user.create({ data: { email: credentials.email } })
        return { id: created.id, email: created.email }
      },
    }),
  ],
  session: { strategy: 'jwt' },
  secret: process.env.NEXTAUTH_SECRET,
})

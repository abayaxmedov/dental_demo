# dental_demo frontend — Next.js standalone (ADR-021).
# glibc (bookworm-slim), musl EMAS: next/image sharp binary'lari muammosiz ishlashi uchun.
FROM node:22-bookworm-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-bookworm-slim AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# --- Build vaqtida QOTADIGAN qiymatlar (next.config.ts izohiga qarang) ---
# NEXT_PUBLIC_* client bundle'ga inline bo'ladi; SITE_HTTPS/MEDIA_REWRITE_TARGET
# headers()/rewrites() ni belgilaydi. Bularni o'zgartirsangiz — QAYTA BUILD shart.
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_MEDIA_URL
ARG NEXT_PUBLIC_SITE_URL
ARG SITE_HTTPS=false
ARG MEDIA_REWRITE_TARGET
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_MEDIA_URL=$NEXT_PUBLIC_MEDIA_URL \
    NEXT_PUBLIC_SITE_URL=$NEXT_PUBLIC_SITE_URL \
    SITE_HTTPS=$SITE_HTTPS \
    MEDIA_REWRITE_TARGET=$MEDIA_REWRITE_TARGET \
    NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production
RUN npm run build

FROM node:22-bookworm-slim AS runner
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0
# Standalone chiqishi: server.js + minimal node_modules. static/ va public/ QO'LDA nusxalanadi.
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
# root emas — Next'ning o'zi yaratadigan `node` foydalanuvchisi.
USER node
EXPOSE 3000
CMD ["node", "server.js"]

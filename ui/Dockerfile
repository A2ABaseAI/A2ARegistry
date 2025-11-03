# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy SDK first (needed as dependency)
# SDK needs to be at ../sdk/typescript relative to ui directory
COPY sdk/typescript ./sdk/typescript

# Copy UI package files
COPY ui/package*.json ./
COPY ui/tsconfig.json ./
COPY ui/next.config.js ./
COPY ui/postcss.config.js ./
COPY ui/tailwind.config.js ./

# Copy UI source code (needed for build)
COPY ui/ ./ui/

# Create proper directory structure for SDK dependency
# package.json expects "../sdk/typescript" from ui directory
# So SDK should be at /app/sdk/typescript and ui at /app/ui
RUN mkdir -p ui

# Now install dependencies from ui directory
# The SDK path "../sdk/typescript" will resolve correctly from ui/
WORKDIR /app/ui
RUN npm ci --legacy-peer-deps || npm install --legacy-peer-deps
WORKDIR /app

# Build Next.js application (from ui directory)
WORKDIR /app/ui
RUN npm run build
WORKDIR /app

# Production stage
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy necessary files from builder
COPY --from=builder /app/ui/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/ui/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/ui/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]


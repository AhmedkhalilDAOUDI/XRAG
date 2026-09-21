# Local deployment rehearsal with persistent D1/R2 emulation. Production is Sites.
FROM node:22-bookworm-slim
WORKDIR /app
COPY package*.json ./
COPY scripts/install-ci.mjs scripts/install-ci.mjs
RUN npm ci --include=dev
COPY . .
RUN npm run build
EXPOSE 8787
USER node
CMD ["npm","run","start","--","--port","8787"]

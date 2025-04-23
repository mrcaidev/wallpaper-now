FROM oven/bun AS build
WORKDIR /code
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile
COPY . .
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV NODE_ENV=production
RUN bun run build

FROM oven/bun:alpine
WORKDIR /app
COPY --from=build /code/dist .
CMD ["bunx", "serve", "-s", "."]

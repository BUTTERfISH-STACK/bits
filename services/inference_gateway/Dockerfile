# services/inference_gateway/Dockerfile
FROM golang:1.20-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o inference-gateway ./main.go

FROM alpine:3.18
RUN apk add --no-cache ca-certificates
WORKDIR /app
COPY --from=builder /app/inference-gateway ./inference-gateway
COPY ecosystem.config.js ./
EXPOSE 8080
CMD ["./inference-gateway"]

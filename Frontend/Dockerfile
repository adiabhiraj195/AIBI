# Multi-stage build for AIBI_Copilot_Frontend (React + Vite)
# Optimized SPA with minimal runtime image

# Stage 1: Builder
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build arguments for Vite
ARG VITE_API_URL
ARG VITE_CSV_API_URL

# Set environment variables for build
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_CSV_API_URL=$VITE_CSV_API_URL

# Build the application
RUN npm run build

# Stage 2: Runtime
FROM nginx:alpine

# Copy built application from builder (Vite outDir = build)
COPY --from=builder /app/build /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Nginx runs in foreground by default in this image
CMD ["nginx", "-g", "daemon off;"]

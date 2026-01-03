# Stage 1: Build the React application
FROM node:18-alpine as builder

WORKDIR /app

# Force rebuild (removed the comment after identifying the solution)
COPY package.json ./
COPY package-lock.json ./

# Install build dependencies required for some npm packages
RUN apk add --no-cache build-base python3

RUN npm install --legacy-peer-deps

COPY . ./

RUN npm run build

# Stage 2: Serve the React application with Nginx
FROM nginx:stable-alpine as production

COPY --from=builder /app/build /usr/share/nginx/html

# Copy the custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

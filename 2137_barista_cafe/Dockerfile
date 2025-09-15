# Use official Nginx image as base
FROM nginx:alpine

# Set working directory
WORKDIR /usr/share/nginx/html

# Remove default nginx static assets
RUN rm -rf ./*

# Copy static website files to Nginx HTML directory
COPY . .

# Expose port 80
EXPOSE 80

# Start Nginx (default command already runs nginx -g 'daemon off;')
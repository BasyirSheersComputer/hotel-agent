# Build stage
FROM nginx:alpine

# Copy static files
COPY . /usr/share/nginx/html

# Copy custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy entrypoint script
COPY entrypoint.sh /docker-entrypoint.d/40-env-subst.sh
RUN chmod +x /docker-entrypoint.d/40-env-subst.sh

# Expose port
EXPOSE 8080

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]

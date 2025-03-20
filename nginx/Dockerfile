FROM nginx:1.23-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY entry.sh /entry.sh
COPY ../web/static /app/static
RUN chmod +x /entry.sh
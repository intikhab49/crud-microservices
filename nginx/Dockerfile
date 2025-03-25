FROM nginx:1.23-alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY entry.sh /entry.sh
RUN chmod +x /entry.sh

EXPOSE 80
CMD ["/entry.sh"]
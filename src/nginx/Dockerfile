FROM nginx:1.27.0

RUN mkdir -p /www/data
#GRAND FOLDER TO NGINX USER ?
COPY ./static /www/data

RUN rm /etc/nginx/conf.d/default.conf

RUN mkdir -p /etc/nginx/ssl
RUN chmod 644 /etc/nginx/ssl

RUN mkdir -p /etc/nginx/ssl/private
RUN chmod 640 /etc/nginx/ssl/private

RUN openssl req -newkey rsa:4096 \
            -x509 \
            -sha256 \
            -days 3650 \
            -nodes \
            -subj "/CN=localhost" \
            -out /etc/nginx/ssl/example.crt \
            -keyout /etc/nginx/ssl/private/example.key

COPY server.conf /etc/nginx/conf.d
COPY nginx.conf /etc/nginx/nginx.conf

RUN chown -R nginx:nginx /www/data
RUN chmod -R 755 /www/data

# Ensure that Nginx files and directories have 
# appropriate permissions to prevent unauthorized access
RUN chown -R nginx:nginx /etc/nginx
RUN chmod -R 750 /etc/nginx

#RUN chown -R nginx:nginx /var/cache/nginx
#RUN chown -R nginx:nginx /var/run

CMD ["nginx", "-g", "daemon off;"]

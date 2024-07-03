FROM nginx:1.27.0

RUN mkdir -p /www/data
#GRAND FOLDER TO NGINX USER ?
COPY ./html/pong.html /www/data/pong.html

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

COPY nginx.conf /etc/nginx/conf.d

CMD ["nginx", "-g", "daemon off;"]

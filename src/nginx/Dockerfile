FROM nginx:1.27.0

#COPY ./static /usr/share/nginx/html # [aguilmea] This should be enabled before deployment when we do not use the bind mount in the docker compose anymor
COPY templates /etc/nginx/templates

COPY ../common_files/ssl_certs/ssl_webpage.crt /etc/ssl/certs/ssl_webpage.crt
COPY ../common_files/ssl_certs/ssl_webpage.key /etc/ssl/certs/ssl_webpage.key

# TODO: [aguilmea] take look at necessary permissions
RUN chmod 777 /etc/ssl/certs/ssl_webpage.crt
RUN chmod 777 /etc/ssl/certs/ssl_webpage.key

CMD ["nginx", "-g", "daemon off;"]

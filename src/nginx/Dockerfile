FROM nginx:1.27.0

RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime && echo "Europe/Berlin" > /etc/timezone

#[aguilmea] This should be enabled before deployment when we do not use the bind mount in the docker compose anymor
COPY ./static /usr/share/nginx/html 
COPY templates /etc/nginx/templates
CMD ["nginx", "-g", "daemon off;"]

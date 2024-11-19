FROM nginx:1.27.0

#COPY ./static /usr/share/nginx/html # [aguilmea] This should be enabled before deployment when we do not use the bind mount in the docker compose anymor
COPY templates /etc/nginx/templates

CMD ["nginx", "-g", "daemon off;"]

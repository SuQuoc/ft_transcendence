FROM nginx:1.27.0

#COPY ./static /usr/share/nginx/html # [aguilmea] This should be enabled before deployment when we do not use the bind mount in the docker compose anymor

#to check:
#RUN rm /etc/nginx/conf.d/default.conf
COPY server.conf /etc/nginx/conf.d
COPY nginx.conf /etc/nginx/nginx.conf

CMD ["nginx", "-g", "daemon off;"]

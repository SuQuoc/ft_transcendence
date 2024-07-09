FROM postgres:16

WORKDIR /docker-entrypoint-initdb.d/
COPY ./init.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init.sh
RUN bash init.sh

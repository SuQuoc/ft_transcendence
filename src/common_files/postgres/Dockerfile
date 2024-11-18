FROM postgres:16

COPY ./db_init.sh /docker-entrypoint-initdb.d/init.sh

# TODO: [aguilmea]chmod might change with own USER for docker
RUN chmod 777 /docker-entrypoint-initdb.d

FROM postgres:16

# Set the container timezone to Europe/Berlin
RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime && echo "Europe/Berlin" > /etc/timezone
# Set timezone in postgresql.conf
RUN echo "log_timezone = 'Europe/Berlin'" >> /usr/share/postgresql/postgresql.conf.sample

COPY ./db_init.sh /docker-entrypoint-initdb.d/init.sh

RUN chmod 777 /docker-entrypoint-initdb.d

FROM postgres:17.2-bookworm

# Set the timezone to Europe/Berlin for the container and postgres database
RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime && echo "Europe/Berlin" > /etc/timezone && \
echo "log_timezone = 'Europe/Berlin'" >> /usr/share/postgresql/postgresql.conf.sample

COPY ./db_init.sh /docker-entrypoint-initdb.d/init.sh
USER postgres

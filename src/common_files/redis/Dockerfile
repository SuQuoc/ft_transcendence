# Use the official Redis image as the base image
FROM redis:alpine3.20

# Change the timezone to Europe/Berlin
RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime && echo "Europe/Berlin" > /etc/timezone

# Copy the script into the container
COPY ./generate-redis-conf.sh /usr/local/bin/generate-redis-conf.sh

# Make the script executable
RUN chmod +x /usr/local/bin/generate-redis-conf.sh

# Set the entrypoint to run the script (creates redis.conf)
ENTRYPOINT ["sh", "/usr/local/bin/generate-redis-conf.sh"]

# Passes args to ENTRYPOINT
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
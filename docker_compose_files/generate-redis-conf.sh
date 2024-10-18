# Check for required environment variables
if [ -z "$REDIS_ADMIN_USER" ] || [ -z "$REDIS_ADMIN_PASSWORD" ] || [ -z "$REDIS_USER" ] || [ -z "$REDIS_PASSWORD" ]; then
    echo "Error: One or more environment variables are not set."
    exit 1
fi


# Create the directory if it doesn't exist
mkdir -p /usr/local/etc/redis

# Create the Redis configuration file
cat <<EOF > /usr/local/etc/redis/redis.conf
# Redis Configuration
user default off
user $REDIS_ADMIN_USER on >$REDIS_ADMIN_PASSWORD +@all
user $REDIS_USER on >$REDIS_PASSWORD +@read ~* -@write
EOF

# Start Redis server
exec redis-server /usr/local/etc/redis/redis.conf
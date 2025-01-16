
# Check for required environment variables
echo "IN SCRIPT"
if [ -z "$REDIS_ADMIN_USER" ] || [ -z "$REDIS_ADMIN_PASSWORD" ] || [ -z "$REDIS_USER" ] || [ -z "$REDIS_PASSWORD" ]; then
    echo "Error: One or more environment variables are not set."
    exit 1
fi


# Create the directory if it doesn't exist
mkdir -p /usr/local/etc/redis
echo "CREATED DIR"


# Create the Redis configuration file
cat <<EOF > /usr/local/etc/redis/redis.conf
# Redis Configuration
user default off
user $REDIS_ADMIN_USER on >$REDIS_ADMIN_PASSWORD +@all
user $REDIS_USER on >$REDIS_PASSWORD ~* +@read +@write +@connection +@pubsub +@scripting +@transaction
EOF

# Execute CMD from Dockerfile "since no args are passed to the script - CMD "
exec "$@"

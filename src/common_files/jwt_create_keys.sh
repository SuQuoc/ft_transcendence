#!/bin/bash

OUTPUT_DIR=src/common_files/jwt_keys

if [ -d "${DIR}" ]; then
    printf "jwt_create_keys.sh: ${RED}a directory with keys already exists\n${DEFAULT}"
    exit 1
fi

mkdir -p $OUTPUT_DIR

openssl genpkey -algorithm RSA -out "$OUTPUT_DIR/private_key.pem" -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in "$OUTPUT_DIR/private_key.pem" -out "$OUTPUT_DIR/public_key.pem"

echo "Private key: $OUTPUT_DIR/private_key.pem"
echo "Public key: $OUTPUT_DIR/public_key.pem"

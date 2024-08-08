#!/bin/bash

OUTPUT_DIR="./src/common_files"

openssl genpkey -algorithm RSA -out "$OUTPUT_DIR/private_key.pem" -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in "$OUTPUT_DIR/private_key.pem" -out "$OUTPUT_DIR/public_key.pem"

echo "Private key: $OUTPUT_DIR/private_key.pem"
echo "Public key: $OUTPUT_DIR/public_key.pem"

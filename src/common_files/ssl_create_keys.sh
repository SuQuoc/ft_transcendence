
DEFAULT="\e[0m"
RED="\e[31m"
GREY="\e[90m"
DIR=src/common_files/ssl_certs

mkdir -p $DIR

################### ROOT CERTIFICATES #####################

openssl ecparam -genkey -name prime256v1 -out "${DIR}/root-ca.key"

openssl req \
    -new -key "${DIR}/root-ca.key" \
    -out "${DIR}/root-ca.csr" -sha256 \
    -subj '/C=US/ST=CA/L=San Francisco/O=AAADocker/CN=Swarm Secret Example CA'

echo "[root_ca]
basicConstraints = critical,CA:TRUE,pathlen:1
keyUsage = critical, nonRepudiation, cRLSign, keyCertSign
subjectKeyIdentifier=hash" > "${DIR}/root-ca.cnf"

openssl x509 -req  -days 3650  -in "${DIR}/root-ca.csr" \
    -signkey "${DIR}/root-ca.key" -sha256 -out "${DIR}/root-ca.crt" \
    -extfile "${DIR}/root-ca.cnf" -extensions root_ca

################### LOCALHOSTS CERTIFICATES ###############

openssl ecparam -genkey -name prime256v1 -out "${DIR}/localhost.key"

openssl req -new -key "${DIR}/localhost.key" -out "${DIR}/localhost.csr" -sha256 \
    -subj '/C=FR/ST=IDF/L=Paris/O=42Network/CN=local'

echo "[server]
authorityKeyIdentifier=keyid,issuer
basicConstraints = critical,CA:FALSE
extendedKeyUsage=serverAuth
keyUsage = critical, digitalSignature, keyEncipherment
subjectAltName = DNS:localhost, IP:127.0.0.1
subjectKeyIdentifier=hash" > "${DIR}/localhost.cnf"

openssl x509 -req -days 750 -in "${DIR}/localhost.csr" -sha256 \
    -CA "${DIR}/root-ca.crt" -CAkey "${DIR}/root-ca.key"  -CAcreateserial \
    -out "${DIR}/localhost.crt" -extfile "${DIR}/localhost.cnf" -extensions server


################### PERMISSIONS ###########################

chmod 0400 \
"${DIR}/localhost.cnf" \
"${DIR}/localhost.csr" \
"${DIR}/root-ca.cnf" \
"${DIR}/root-ca.crt" \
"${DIR}/root-ca.csr" \
"${DIR}/root-ca.key" \

chmod 0444 \
"${DIR}/localhost.crt" \
"${DIR}/localhost.key"

DEFAULT="\e[0m"
RED="\e[31m"
DIR=src/common_files/ssl_certs

rm -rf $DIR

set -e  # for the subshell: exit the shell on error of subshell
(
    mkdir -p $DIR

    if [ ! -f docker_compose_files/.env ]; then
        printf "${RED}Error: srcs/.env file not found${DEFAULT}\n";
        exit 1;
    fi

    if ! grep -q "DOMAIN" docker_compose_files/.env; then
        DOMAIN="localhost"
    else
        DOMAIN=$(grep "DOMAIN" docker_compose_files/.env | cut -d '=' -f2)
    fi


    if [ "${DOMAIN}" = "localhost" ]; then
        IP="127.0.0.1"
    else
        IP="${DOMAIN}"
    fi

################### ROOT CERTIFICATES #####################

openssl ecparam -genkey -name prime256v1 -out "${DIR}/root-ca.key"

openssl req \
    -new -key "${DIR}/root-ca.key" \
    -out "${DIR}/root-ca.csr" -sha256 \
    -subj '/C=AT/ST=VIE/L=Vienna/O=ACrazyyyTeam/CN=Transcendence AG'

echo "[root_ca]
basicConstraints = critical,CA:TRUE,pathlen:1
keyUsage = critical, nonRepudiation, cRLSign, keyCertSign
subjectKeyIdentifier=hash" > "${DIR}/root-ca.cnf"

openssl x509 -req  -days 3650  -in "${DIR}/root-ca.csr" \
    -signkey "${DIR}/root-ca.key" -sha256 -out "${DIR}/root-ca.crt" \
    -extfile "${DIR}/root-ca.cnf" -extensions root_ca

################### WEBSITE CERTIFICATES ###############

openssl ecparam -genkey -name prime256v1 -out "${DIR}/ssl_webpage.key"

openssl req -new -key "${DIR}/ssl_webpage.key" -out "${DIR}/ssl_webpage.csr" -sha256 \
    -subj '/C=AT/ST=VIE/L=Vienna/O=42Team/CN=local'

echo "[server]
authorityKeyIdentifier=keyid,issuer
basicConstraints = critical,CA:FALSE
extendedKeyUsage=serverAuth
keyUsage = critical, digitalSignature, keyEncipherment
subjectAltName = DNS:${DOMAIN}, IP:${IP}
subjectKeyIdentifier=hash" > "${DIR}/ssl_webpage.cnf"

openssl x509 -req -days 750 -in "${DIR}/ssl_webpage.csr" -sha256 \
    -CA "${DIR}/root-ca.crt" -CAkey "${DIR}/root-ca.key"  -CAcreateserial \
    -out "${DIR}/ssl_webpage.crt" -extfile "${DIR}/ssl_webpage.cnf" -extensions server


################### PERMISSIONS ###########################

chmod 0400 \
"${DIR}/ssl_webpage.cnf" \
"${DIR}/ssl_webpage.csr" \
"${DIR}/root-ca.cnf" \
"${DIR}/root-ca.crt" \
"${DIR}/root-ca.csr" \
"${DIR}/root-ca.key"

chmod 0444 \
"${DIR}/ssl_webpage.crt" \
"${DIR}/ssl_webpage.key"

)
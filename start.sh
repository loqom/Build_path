#!/bin/sh

set -e

CERTIFI_BUNDLE="$(python -c 'import certifi; print(certifi.where())')"
AZURE_PROXY_CA="/etc/ssl/certs/adc-egress-proxy-ca.crt"
COMBINED_CA="/tmp/python-ca-bundle.crt"

if [ -f "$AZURE_PROXY_CA" ]; then
    cat "$CERTIFI_BUNDLE" "$AZURE_PROXY_CA" > "$COMBINED_CA"
    export SSL_CERT_FILE="$COMBINED_CA"
    export REQUESTS_CA_BUNDLE="$COMBINED_CA"
else
    export SSL_CERT_FILE="$CERTIFI_BUNDLE"
    export REQUESTS_CA_BUNDLE="$CERTIFI_BUNDLE"
fi

exec python main.py
# syntax = docker/dockerfile:1.0-experimental
FROM python:3-alpine

WORKDIR /app
COPY scale.py /app/scale.py
COPY requirements.txt /app/requirements.txt

RUN --mount=type=secret,id=pivnet_token \
 apk update \
 && apk add curl jq \
 && rm -rf /var/cache/apk/* \
 && ACCESS=$(curl -X POST https://network.pivotal.io/api/v2/authentication/access_tokens -d '{"refresh_token":"'$(cat /run/secrets/pivnet_token)'"}' | jq -r .access_token) \
 && curl -v -L -o /usr/local/bin/pks -X GET https://network.pivotal.io/api/v2/products/pivotal-container-service/releases/501833/product_files/528557/download -H "Authorization: Bearer $ACCESS"  \
 && chmod +x /usr/local/bin/pks \
 && pip install -r requirements.txt 


ENTRYPOINT [ "python", "scale.py" ]
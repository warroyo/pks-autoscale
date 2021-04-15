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
 && curl -v -L -o /usr/local/bin/tkgi -X GET https://network.pivotal.io/api/v2/products/pivotal-container-service/releases/863377/product_files/921855/download -H "Authorization: Bearer $ACCESS"  \
 && chmod +x /usr/local/bin/tkgi \
 && cp  /usr/local/bin/tkgi /usr/local/bin/pks \
 && pip install -r requirements.txt 


ENTRYPOINT [ "python", "scale.py" ]
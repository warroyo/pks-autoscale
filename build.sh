#!/bin/bash

DOCKER_BUILDKIT=1 docker build --progress plain --no-cache --secret id=pivnet_token,src=pivnet_token.txt -t pks-autoscale .
#!/bin/bash

set -ex

pks login -a $API --client-name $CLIENT --client-secret $CLIENT_SECRET -k

CURRENT_SIZE=$(pks cluster $CLUSTER --json | jq -c -r ".parameters.kubernetes_worker_instances"  )
NEW_SIZE=$((CURRENT_SIZE + 1))

echo "current cluster size is $CURRENT_SIZE nodes; increasing to $NEW_SIZE nodes"

#pks resize $CLUSTER -n $NEW_SIZE --wait --non-interactive




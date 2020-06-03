# AutoScaling Example for PKS

this is a script and accompanying docker image that can be run on a schedule to autoscale PKS clusters based on memory usage percentage. the script could be modified to scale based on anything you want. this simply queryies a promethues cluster and then runs scale commands based on thresholds and max and min workers. 

## Pre-reqs

* PKS cluster
* Jenkins(other ci tools can be used here as well) or k8s cluster for running on a schedule
* prometheus monitoring cluster(I am using Reliability View for PKS)
* Docker

## Create PKS Service Account

we will need a service account to authenticate to PKS. we will create this in UAA.

1. login to UAA and create an automated client by running the below commands
   
```
 uaac target <pks-api>:8443 --skip-ssl-validation

 uaac token client get admin -s <admin-secret>

 uaac client add automated-client \                                                                             
-s <secret> \
--authorized_grant_types client_credentials  \
--authorities pks.clusters.admin,pks.clusters.manage
```

## Obtaining Required Promethues info

when using reliability view you can get the prometheus info from opsman.

* prometheus server - reliability view tile -> status -> TSDB . prometheus will be on that IP on port `4449`
* prometheus client cert & key - reliability view tile -> credentials -> Tsdb Client Mtls. there will be two values in this entry. these will be used below in the `env.vars` file.

## Create the env vars file

in order to connect to PKS and prom we need an environment file .

1. create the file
`cp env.vars.template env.vars`

2. fill in each variable with the correct values, you can find descriptions for each var in the section below called "docker image usage"


# Running Continuosly

## on k8s

this example uses k8s cronjobs to run the autoscale script ona  schedule. we will be using a `cronjob` and a `secret`*

1. update the schedule in the `manifest.yml` to your liking 
2. update the image if you are hosting internally ona  registry
3. be sure that your env.vars file is update
4. create the secret from the `env.vars`
   ```
    kubectl create secret generic autoscale --from-env-file env.vars
   ```
5. apply the manifest to k8s

    ```
    kubectl apply -f manifest.yml
    ```





\* **we are using a standard k8s secret for simplicity in this example. In prod you should be using something more secure(Vault,sealec secrets, etc.)**

## a Jenkins job

we will create a jenkins job to schedule out script to be run. you can use any  CI to do this or even run it inside of a k8s cluster on a schedule.

**ensure that docker is installed on the jenkins worker.**

1. create a freestyle job
2. set the "Build Periodically" checkbox and add this schedule `*/10 * * * *` this will run every 10 min
3. fill out the env.vars file if you haven't already
4. create a secret in jenkins of the type "secret file" upload the env.vars file
5. in the job under "build environment" click "Use secret text(s) or file(s)" 
6. add a new binding of type "secret file" and select the newly added `env.vars` file and us `ENV_VARS` as the env variable name.
7. under the "build" section of the job add "execute shell" and add the below snippet.

```
#!/bin/bash
set -ex

docker run --rm --env-file=$ENV_VARS warroyo90/pks-autoscale:1.1.0
```

8. save the job

# Testing 

there is an example deployment here in the file `test.yml` you can modify the replicas # to increase memory usage. 

# extra info

## docker image usage

environment vars:

* `PKS_API` - no default, PKS api url
* `CLUSTER` - no default, PKS cluster name
* `CLIENT_SECRET` - no default, PKS client secret
* `CLIENT` - no default, PKS client name
* `PROM` - no default, prometheus server ex. https://prometheus.com:4449
* `MIN_WORKERS` - default `3` , number of workers that it should never go below
* `MAX_WORKERS` - default `10` , number of workers that it should never go above
* `UPPER_THRESHOLD` - default `70` , memory usage percent to scale up at
* `LOWER_THRESHOLD` - default `30` , memory usage percent to scale down at
* `PROM_CERT` - no default, the client cert needed for prom auth. 
* `PROM_KEY` - no default, the client key needed for prom auth
* `PROM_QUERY` - no default, the query to use for getting memory info from prometheus

an example env vars file that is used below can be found in this repo. `env.vars`

**certs will need to be escaped with `\n` to make a single line. docker does not suppprt multiline in the `env-file`**

run:

`docker run -it --rm --env-file=env.vars warroyo90/pks-autoscale:1.1.0`

## Building the docker image

the dockerfile in this repo will create an image with PKS and Python. all of the dependencies needed to run the scipt. this is how you build it, you can also use a pre-built image at `warroyo90/pks-autoscale:1.1.0`

1. copy the pks token template

```
cp pivnet_token.template pivnet_token.txt
```

2. go to network.pivotal.io , sign in
3. in the top right go to the dropdown and "edit profile" click generate refresh token. 
4. paste the refresh token into the new file.
5. build the image

```
./build.sh
```
# AutoScaling Example for PKS


## Pre-reqs

* PKS cluster
* Jenkins(other ci tools can be used here as well)
* grafana/prometheus monitoring cluster(I am using Reliability View for PKS)


## Create PKS Service Account

we will need a service account to authenticate to PKS. we will create this in UAA.

1. login to UAA
    `

create a jenkins job 
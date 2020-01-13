import datetime
import time
import requests
import subprocess
import sys
import json
import os


pks_api =  os.getenv('PKS_API') #'api.pks.<your-domain>'
cluster =  os.getenv('CLUSTER') #cluster name
client_secret =  os.getenv('CLIENT_SECRET') #automated client secret
client = os.getenv('CLIENT') #automated client name
prometheus = os.getenv('PROM') #promethues server

min_workers = int(os.getenv('MIN_WORKERS',3))
max_workers = int(os.getenv('MAX_WORKERS',10))
upper_threshold = int(os.getenv('UPPER_THRESHOLD',70))
lower_threshold = int(os.getenv('LOWER_THRESHOLD',70))
#setup cert auth, if your prometheus uses basic auth you need to change this
cert_file = open('cert.pem', 'w')
cert_file.write(os.getenv('PROM_CERT').replace('\\n', '\n')) 
cert_file.close()
key_file = open('key.pem', 'w')
key_file.write(os.getenv('PROM_KEY').replace('\\n', '\n')) 
key_file.close()

cert_file_path = "cert.pem"
key_file_path = "key.pem"
cert = (cert_file_path, key_file_path)

#query promethues for memory consumption
response = requests.get(prometheus + '/api/v1/query',
  params={
    'query': 'sum (kubernetes_node_memory_working_set_bytes{ cluster_name=~"^cluster1"}) / sum (kubernetes_node_memory_available_bytes{ cluster_name=~"^cluster1"}) * 100'
}, cert=cert, verify=False)

#parse the results for the value
results = response.json()['data']['result']
memory_percent = int(float(results[0]['value'][1]))

#login to pks client
pks_login = subprocess.run(['pks', 'login', '-a' , pks_api ,'--client-name', client ,'--client-secret', client_secret , '-k'],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE,
                     check=True
                     )

#get current cluster worker count
pks_cluster = subprocess.run(['pks', 'cluster', cluster ,'--json'],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE,
                     check=True,
                     universal_newlines=True)

worker_json = json.loads(pks_cluster.stdout)

current_workers = int(worker_json['parameters']['kubernetes_worker_instances'])
scale_up_size = current_workers + 1
scale_down_size = current_workers - 1

if memory_percent >= upper_threshold and current_workers != max_workers:
    print("scaling up cluster memory greater than {upper_threshold} percent".format(upper_threshold=upper_threshold))
    pks_scale_up = subprocess.run(['pks', 'resize', cluster ,'-n',str(scale_up_size),'--non-interactive'],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE,
                     check=True,
                     universal_newlines=True)
    print(pks_scale_up.stdout)

elif memory_percent <= lower_threshold and current_workers != min_workers:
    print("scaling down cluster memory less than {lower_threshold} percent".format(lower_threshold=lower_threshold))
    pks_scale_down = subprocess.run(['pks', 'resize', cluster ,'-n',str(scale_down_size),'--non-interactive'],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE,
                     check=True,
                     universal_newlines=True)
    print(pks_scale_down.stdout)
else:
    print("not scaling up or down, current cluster size is {current_workers} and memory is {memory_percent} percent".format(memory_percent=str(memory_percent), current_workers=str(current_workers)) )

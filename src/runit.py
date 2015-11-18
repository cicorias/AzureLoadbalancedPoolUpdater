#!/usr/bin/python

# pip azure
from azure.mgmt.common import ( 
    SubscriptionCloudCredentials
)

from azure.mgmt.resource import (
    ProviderOperations,
    ResourceGroupListParameters,
    ResourceGroupOperations,
    ResourceManagementClient,
    ResourceIdentity,
    GenericResource
)

from azure.mgmt.network import (
    NetworkResourceProviderClient
)

from azure.mgmt.compute import (
    ComputeManagementClient
)

import requests, json, re

# globals
endpoint =  client_id = client_secret = None


def get_token_from_client_credentials(endpoint, client_id, client_secret):
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'resource': 'https://management.core.windows.net/',
    }
    response = requests.post(endpoint, data=payload).json()
    return response['access_token']

def list_resource_groups():
    result = resource_client.resource_groups.list(None)
    for group in result.resource_groups:
        print(group.name)
	
	
def load_config():
    with open('settings.private.json') as config_file:
        global config, subscription_id, client_id, client_secret, endpoint
        config = json.load(config_file)
        subscription_id = config['subscription_id']
        client_id = config['client_id']
        client_secret = config['client_secret']
        endpoint = config['endpoint']


def get_load_balancer(resource_group_name, load_balancer_name):
    # Get all LBs
    load_balancer_list = network_client.load_balancers.list(resource_group_name=resource_group_name)
    # for lb in lbs
    for load_balancer_item in load_balancer_list.load_balancers:
        if load_balancer_item.name == load_balancer_name:
            return load_balancer_item


def get_backend_pool(load_balancer_object, pool_name):
    for pool in load_balancer_object.backend_address_pools:
        if pool.name == pool_name:
            return pool

def get_vm(vmname):
    print vmname


# Startup
load_config()

# OAuth token needed
auth_token = get_token_from_client_credentials(endpoint, client_id, client_secret)

# now the Azure management credentials
creds = SubscriptionCloudCredentials(subscription_id, auth_token)

# now the specific compute, network resource type clients
compute_client = ComputeManagementClient(creds)
network_client = NetworkResourceProviderClient(creds)
resource_client = ResourceManagementClient(creds)

list_resource_groups()

resource_group = 'mshackilbfloat1'
load_balancer = get_load_balancer(resource_group, 'webload')
backend_pool = get_backend_pool(load_balancer, 'BackendPool1')


print 'ip config ids'
for ipconfig in backend_pool.backend_ip_configurations:
    print ipconfig.id





# this shit aint working....

toremove = ur'ipconfig0';
toaddFloat = ur'ilbfloat1'
toaddIp = ur'ipconfig1'

for ipconfig in backend_pool.backend_ip_configurations:
    findReqex = re.compile(toremove)
    idDecode = ipconfig.id  #.decode('utf-8')
    if findReqex.match(idDecode) is not None:
        idStr = ipconfig.id
        newId = findReqex.sub(toaddFloat, idStr.decode('utf-8'))
        newId = findReqex.sub(toaddIp, newId)
        print idStr
        print newId


#
# for thing in backend_pool

print 'done'


# Remaining approach:

# 1. Based upon the "VM" names provided for "master" and "replica"
# 2. Get the VM, then get it's NIC /networkProfile/networkInterfaces/id  (name)
#    using that 'name'
# 3. Then get its /Microsoft.Network/networkInterfaces -> property/ipConfigurations/
#      Then gat the "id" of that ipconfiguration which
# 4. Then "remove" for ID for replica, then "add" the master




#    result = resource_client.resource_groups.list(None)
#    for group in result.resource_groups:
#        print(group.name)
	

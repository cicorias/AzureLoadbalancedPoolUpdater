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
    NetworkResourceProviderClient,
)

import requests, json

global compute_client, network_client, resource_client
global subscription_id, client_id, client_secret, endpoint


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
        config = json.load(config_file)
        subscription_id = config.subscription_id
        client_id = config.client_id
        client_secret = config.client_secret
        endpoint = config.endpoint


# OAuth token needed
auth_token = get_token_from_client_credentials(endpoint, client_id, client_secret)

# now the Azure management credentials
creds = SubscriptionCloudCredentials(subscription_id, auth_token)

# now the specfic compute, network resource type clients
# compute_client = ComputeManagementClient(creds)
network_client = NetworkResourceProviderClient(creds)
resource_client = ResourceManagementClient(creds)

list_resource_groups()

def get_load_balancer(resource_group_name, load_balancer_name):
    # Get all LBs
    load_balancer_list = network_client.load_balancers.list(resource_group_name=resource_group_name)
    # for lb in lbs
    for load_balancer in load_balancer_list.load_balancers:
        if load_balancer.name == load_balancer_name:
            return load_balancer


def get_backend_pool(load_balancer, pool_name):
    for pool in load_balancer.backend_address_pools

resource_group = 'mshackilbfloat1'

load_balancer = get_load_balancer(resource_group, 'webload')

print 'done'


#    result = resource_client.resource_groups.list(None)
#    for group in result.resource_groups:
#        print(group.name)
	

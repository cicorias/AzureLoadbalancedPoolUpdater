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
    LoadBalancer,
    BackendAddressPool,
    ResourceId
)

from azure.mgmt.network.networkresourceprovider import (
    NetworkInterface

)

from azure.mgmt.compute import (
    ComputeManagementClient
)

import requests, json, re, os, logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

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

# Probably should just be a 'model' that handles this
def get_virtual_machine(resource_group_name, vm_name):
    """
    :param resource_group_name: str
    :param vm_name: str
    :return: azure.mgmt.compute.VirtualMachine
    """
    virtual_machine = compute_client.virtual_machines.get(resource_group_name, vm_name).virtual_machine
    logging.info('using virtual machine id: %s', virtual_machine.id)
    return virtual_machine


def get_network_interface_ip_configuration(resource_group_name, network_interface_name):
    network_interface = network_client.network_interfaces.get(resource_group_name, network_interface_name)
    for ipconfig in network_interface.network_interface.ip_configurations:
        return ipconfig

def get_virtual_machine_network_interface(resource_group_name, virtual_machine_name):
    virtual_machine = get_virtual_machine(resource_group_name, virtual_machine_name)
    for profile in virtual_machine.network_profile.network_interfaces:
        nic_uri = profile.reference_uri

    #network_interface = get_network_interface(resource_group_name)
    label = os.path.basename(os.path.normpath(nic_uri))
    logging.info('nic on vm to use is: %s', label)

    network_interface = get_network_interface_ip_configuration(resource_group_name, label)
    logging.info('nic id is: %s', network_interface.id)
    return network_interface


# Startup
load_config()

# OAuth token needed
auth_token = get_token_from_client_credentials(endpoint, client_id, client_secret)

# now the Azure management credentials
credentials = SubscriptionCloudCredentials(subscription_id, auth_token)

# now the specific compute, network resource type clients
compute_client = ComputeManagementClient(credentials)
network_client = NetworkResourceProviderClient(credentials)
resource_client = ResourceManagementClient(credentials)

resource_group = 'mshackilbfloat1'
virtual_machine_name = 'BackendVM1'
load_balancer_name = 'webload'
backend_pool_name = 'BackendPool1'

network_interface_to_be_master = get_virtual_machine_network_interface(resource_group, virtual_machine_name)

load_balancer = get_load_balancer(resource_group, load_balancer_name)
backend_pool = get_backend_pool(load_balancer, backend_pool_name)


parameters = {}
parameters['properties'] = {}


new_nic = NetworkInterface(id=network_interface_to_be_master.id, location=load_balancer.location)

new_nic.ip_configurations = []
#new_nic2 = NetworkInterfaceIpConfiguration(id=network_interface_to_be_master.id)

#new_nic2.load_balancer_backend_address_pools = [load_balancer]

#network_interface_to_be_master.load_balancer_backend_address_pools = [load_balancer.id]


result = network_client.network_interfaces.create_or_update(resource_group, load_balancer_name, new_nic)


print 'done'





# check if 1 and only in in the list

#  properties.backendaddresspools[].backendipconfigurstions[]
def old_way():
    new_settings = LoadBalancer()
    new_back_end = BackendAddressPool()

    new_settings.id = load_balancer.id
    new_settings.name = load_balancer.name
    #new_settings.etag = load_balancer.etag
    new_settings.location = load_balancer.location

    new_back_end.id = backend_pool.id
    new_back_end.name = backend_pool.name
    #new_back_end.etag = backend_pool.etag

    new_nic = ResourceId(id=network_interface_to_be_master.id)
    new_back_end.backend_ip_configurations = [new_nic] #backend_pool.backend_ip_configurations
    new_settings.backend_address_pools =  [new_back_end]
    #result = network_client.load_balancers.create_or_update(resource_group, load_balancer_name, new_settings)



# Remaining approach:
# 0. d parameters provided "backend pool name" & "vm" to be master
# 1. d Based upon the "VM" names provided for "master
# 2. d Get the VM, then get it's NIC /networkProfile/networkInterfaces/id  (name)
#    using that 'name'
# 3. d Then get its /Microsoft.Network/networkInterfaces -> property/ipConfigurations/
#      Then gat the "id" of that ipconfiguration which
# 4. Then "remove" all from the backend pool; then add in the VM/nic as master


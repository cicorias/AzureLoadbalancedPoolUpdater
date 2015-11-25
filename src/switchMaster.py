#!/usr/bin/python

# Setup..

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

from requests import Request, Session

import requests, json, re, os, logging, getopt, sys


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

def load_config():
    with open('settings.private.json') as config_file:
        global config, subscription_id, client_id, client_secret, endpoint
        config = json.load(config_file)
        subscription_id = config['subscription_id']
        client_id = config['client_id']
        client_secret = config['client_secret']
        endpoint = config['endpoint']

    with open('environment.json') as machine_file:
        global environment, number_of_machines
        environment = json.load(machine_file)
        number_of_machines = len(environment['vmnames'])
        logging.info('there are %s machines', number_of_machines)


def get_token_from_client_credentials(endpoint, client_id, client_secret):
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'resource': 'https://management.core.windows.net/',
    }
    #TODO add back in verify for non-fiddler
    #NOTE add Verify=False when going via a proxy with fake cert / fiddler
    response = requests.post(endpoint, data=payload).json()
    return response['access_token']

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
    return network_interface
    #for ipconfig in network_interface.network_interface.ip_configurations:
    #    return ipconfig

def get_virtual_machine_network_interface(resource_group_name, virtual_machine_name):
    virtual_machine = get_virtual_machine(resource_group_name, virtual_machine_name)
    for profile in virtual_machine.network_profile.network_interfaces:
        nic_uri = profile.reference_uri

    #network_interface = get_network_interface(resource_group_name)
    label = os.path.basename(os.path.normpath(nic_uri))
    logging.info('nic on vm to use is: %s', label)

    network_interface = get_network_interface_ip_configuration(resource_group_name, label)
    logging.info('nic id is: %s', network_interface.network_interface.id)
    return network_interface.network_interface

def get_master_vmname_from_arg(arg):
    if arg == '0':
        rv = { 
            'newMaster' : environment['vmnames'][0],
            'oldMaster' : environment['vmnames'][1] 
        }
    elif arg == '1':
        rv = { 
            'newMaster' : environment['vmnames'][1],
            'oldMaster' : environment['vmnames'][0] 
        }
    else:
        raise ValueError('Only accept 0 or 1 as New Master value')

    return rv

def build_request(vm_object, nic_object, load_balancer=None):
    """
    :param vm_object : azure.mgmt.compute.VirtualMachine
    :param nic_object : azure.mgmt.network.networkresourceprovider.NetworkInterface
    :param load_balancer : azure.mgmt.network.LoadBalancer
    :return: dict
    """
    if load_balancer == None:
        backend_pool = []
    else:
        backend_pool = [{ 'id' : load_balancer.load_balancer.backend_address_pools[0].id }]

    request = {
        'properties': {
            'virtualMachine' : {
                'id' : vm_object.virtual_machine.id
                },
            'ipConfigurations' : [{ #may have to build by hand
                'properties' : {
                    'loadBalancerBackendAddressPools' : backend_pool,
                    'subnet' : {
                        'id' :  nic_object.ip_configurations[0].subnet.id
                        }
                    },
                'name' : nic_object.ip_configurations[0].name,
                'id' : nic_object.ip_configurations[0].id
                 }]
            },
        'id' : nic_object.id,
        'name' : nic_object.name,
        'location' : vm_object.virtual_machine.location,
        'type' : 'Microsoft.Network/networkInterfaces'
        }


    return request

def send_loadbalancer_request(payload, resource_id, max_retries=20):
    endpoint = network_client.base_uri + resource_id + '?api-version=' + network_client.api_version

    header = { 'Authorization' : 'Bearer ' + auth_token }
    
    while (max_retries > 0):
        session = Session()
        request = Request('PUT', endpoint, json=payload, headers=header)
        prepared = session.prepare_request(request)

        logging.debug('raw body sent')
        logging.debug(prepared.body)

        response = session.send(prepared)
        if (response.status_code == 200):
            break
        elif (response.status_code == 429):
            max_retries = max_retries - 1
            logging.warn('retrying an HTTP send due to 429 retryable response')
            logging.warn('this will be try# %s', max_retries)
    
    return response


def main(argv):
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'n:r:')
    except getopt.GetoptError:
        logging.exception('invalid options - switchMaster -newmaster 0|1')

    # Startup
    load_config()

    for opt,arg in opts:
        if opt in ('-n'):
            new_master_arg = arg
            logging.info('newMaster will be %s', new_master_arg)            
            #now get the existing virtual machines
            vmnames = get_master_vmname_from_arg(new_master_arg)
        elif opt in ('-r'):
            max_retries = arg
            logging.info('max retries set to %s', max_retries)


    # OAuth token needed
    global auth_token
    auth_token = get_token_from_client_credentials(endpoint, client_id, client_secret)

    # now the Azure management credentials
    credentials = SubscriptionCloudCredentials(subscription_id, auth_token)

    # now the specific compute, network resource type clients
    global compute_client, network_client, resource_client
    compute_client = ComputeManagementClient(credentials)
    network_client = NetworkResourceProviderClient(credentials)
    resource_client = ResourceManagementClient(credentials)

    #TODO modify this to mach your specific settings
    resource_group = environment['resourceGroup']
    load_balancer_name = environment['loadBalancerName']
    
    subnet_name = environment['subnetName'];
    virtual_network_name = environment['virtualNetworkName'];

    #TODO - end - only the "above" should need to change.

    old_master_vm = compute_client.virtual_machines.get(resource_group, vmnames['oldMaster']['name'])
    new_master_vm = compute_client.virtual_machines.get(resource_group, vmnames['newMaster']['name'])

    #get the subnet we are in
    subnet = network_client.subnets.get(resource_group, virtual_network_name, subnet_name)

    #the load balancer
    load_balancer = network_client.load_balancers.get(resource_group, load_balancer_name)

    #get the 2 nic cards for the VM's in this subnet/loadbalncer config
    new_master_nic = get_virtual_machine_network_interface(resource_group, vmnames['newMaster']['name'])
    old_master_nic = get_virtual_machine_network_interface(resource_group, vmnames['oldMaster']['name'])


    old_master_request = build_request(old_master_vm, old_master_nic)
    new_master_request = build_request(new_master_vm, new_master_nic, load_balancer)


    send_loadbalancer_request(old_master_request, old_master_nic.id, max_retries)

    #make sure to add in the backendpool
    send_loadbalancer_request(new_master_request, new_master_nic.id, max_retries)


if __name__ == "__main__":
   main(sys.argv[1:])


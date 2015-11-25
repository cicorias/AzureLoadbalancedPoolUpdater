# Updating Azure Load Balancer Backend Pool

Provides and approach for updating Azure Load Balancer – adding and removing Virtual Machines from the Back End Pool

* Current example written in C#
* Visual Studio 2015
* Following direct NuGet package dependencies
* ADAL & Azure Management Libraries


```json
<package id="Microsoft.Azure.Common" 
	version="2.1.0" targetFramework="net46" />
<package id="Microsoft.Azure.Management.Compute" 
	version="11.0.0-prerelease" targetFramework="net46" />
<package id="Microsoft.Azure.Management.Network" 
	version="3.0.0-preview" targetFramework="net46" />
<package id="Microsoft.IdentityModel.Clients.ActiveDirectory" 
	version="2.19.208020213" targetFramework="net46" />
```

## Background and Purpose

An Load Balancer can have “Back End Pools” Of which there can be 0 or more Virtual Machines within

Note: the state of 0 machines is illogical but allowed

## Why does this matter?
### Basic Premise and Logic
Goal is to utilize the Load Balancer Service from Azure – avoid a custom solution
Some software, primarily Persistence / Database engines require a single master – and 0 or more Replica’s
No traffic can be permitted to Replica’s direct from Clients
Traffic Must go to the Master

## Direct Server Return / Floating IP
A future write-up will cover this
A HOWTO configure a Windows or Linux machine to support
Direct Server Return (DSR)
Provides a near “pass-through” of the packets as they appear to the Load Balancer to “1 and only 1” machine in a Back End Pool
Slight Performance
Some Software like Barracuda, etc. “desire” this capability
Some Persistence Engines could benefit
Utilized for SQL Server Always ON today
Not well documented for Non-SQL Server Configurations

## Setup and Configuration
### Create your Azure Active Directory Service Principal
There is a script `createAdApp.sh` that can help here that uses certificates, but best to review [Creating a Service Principal via Portal](https://azure.microsoft.com/en-us/documentation/articles/resource-group-create-service-principal-portal/)

This sample has been tested using a "ClientID" and "Secret" - that is generated from the Portal.


### Private Secrets Settings File
Modify/Create the file `settings.private.json` - this file should never be checked in or made public as it has secrets in it.

```json
{
  "subscription_id" : "<subscriptionid>",
  "client_id" : "< from Azure AD - client ID of an App created >",
  "client_secret" : "< client secret - good for 1 year, or 2 years >",
  "endpoint" : "https://login.microsoftonline.com/<tenantid>/oauth2/token"
}
```

In the above, replace the settings for
* subscription_id
* client_id
* endpoint

Review that article mentioned before on where to get these from the Portal
[Creating a Service Principal via Portal](https://azure.microsoft.com/en-us/documentation/articles/resource-group-create-service-principal-portal/)

### Environment Configuration File
The file `environment.json` should be updated with your environment settings.

Note that this example assumes that all resources are in the same Resource Group - they don't have to be, but that's how this sample is written.

```json
{
  "vmnames": [
    { "name": "BackendVM0" },
    { "name": "BackendVM1" }
  ],

  "resourceGroup": "mshackilbfloat1",
  "loadBalancerName": "webload",
  "subnetName": "backendSubnet",
  "virtualNetworkName" : "ilbfloat"
}
```

#### Virtual Machine Names
In the json array, ensure you have the 2 machines that are part of the Backend Pool. In the example above, the machines `BackendVM0` and `BackendVM1` are the machine
names as part of a Deployment.

#### Other settings
* Resource Group
* Load Balancer Name
* Subnet Name
* Virtual Network Name

##### Resource Group
This is the name of the resource group that the Network Interfaces are part of - these are "bound" to a Virtual Machine
and a Subnet (VNet)

##### Load Balancer Name
The name of the Load Balancer - this is assumed to be part of the same Resource Group as the Virtual Machines

##### Virtual Network Name
Name of the Virtual Network that the Subnet is part of.

##### Subnet Name
This is the name of the Subnet within the Virtual Network - again, assumed to be part of the same Resource Group

## Video Walkthrough
### Python Version
View on Office Mix [Azure Load Balancer Back End Updates via REST (Python Version)](https://mix.office.com/watch/f4cvoa3cnfoe)

View on YouTube [https://youtu.be/RtsxMuBnnO4](https://youtu.be/RtsxMuBnnO4)

### CSharp (C\#) Version
View on Office Mix [Azure Load Balancer Back End Updates via REST](https://mix.office.com/MyMixes/Details/1zm4c3lcw51o)

Or on YouTube [Azure Load Balancer Back End Updates via REST](https://youtu.be/ChOhpEpPHL8)

### Video in iframe..
<iframe width="1184" height="715" src="http://bit.ly/1MswxXq" frameborder="0"></iframe>


#### Via Mix
<iframe width="1184" height="715" src="https://mix.office.com/embed/1zm4c3lcw51o" frameborder="0"></iframe>


## Example ARM Template

The following was utilized for the ARM template, and also located here [https://github.com/cicorias/Cluster-Azure-Configurations](https://github.com/cicorias/Cluster-Azure-Configurations)

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "virtualNetworkName": {
      "type": "string",
      "minLength": 1,
      "metadata": {
        "description": "This is the name of the Virtual Network"
      }
    },
    "networkInterfaceName": {
      "type": "string",
      "minLength": 1,
      "metadata": {
        "description": "This is the prefix name of the Network interfaces"
      }
    },
    "loadBalancerName": {
      "type": "string",
      "minLength": 1,
      "metadata": {
        "description": "This is the name of the load balancer"
      }
    },
    "adminUsername": {
      "type": "string",
      "minLength": 1,
      "metadata": {
        "description": "Admin username"
      }
    },
    "adminPassword": {
      "type": "securestring",
      "metadata": {
        "description": "Admin password"
      }
    },
    "imagePublisher": {
      "type": "string",
      "minLength": 1,
      "defaultValue": "MicrosoftWindowsServer",
      "metadata": {
        "description": "Image Publisher"
      }
    },
    "vmNamePrefix": {
      "type": "string",
      "minLength": 1,
      "defaultValue": "BackendVM",
      "metadata": {
        "description": "Prefix to use for VM names"
      }
    },
    "imageOffer": {
      "type": "string",
      "minLength": 1,
      "defaultValue": "WindowsServer",
      "metadata": {
        "description": "Image Offer"
      }
    },
    "imageSKU": {
      "type": "string",
      "minLength": 1,
      "defaultValue": "2012-R2-Datacenter",
      "metadata": {
        "description": "Image SKU"
      }
    },
    "vmSize": {
      "type": "string",
      "minLength": 1,
      "defaultValue": "Standard_D1",
      "metadata": {
        "description": "This is the allowed list of VM sizes"
      }
    },
    "dnsNameForPublicIP": {
      "type": "string",
      "metadata": {
        "description": "Unique DNS name for Public IP"
      }
    },

    "publicIPAddressType": {
      "type": "string",
      "defaultValue": "Dynamic",
      "allowedValues": [
        "Dynamic",
        "Static"
      ],
      "metadata": {
        "description": "Type of public IP address"
      }

    },
    "JumpBoxName": {
      "type": "string",
      "minLength": 1
    },
    "JumpBoxWindowsOSVersion": {
      "type": "string",
      "defaultValue": "2012-R2-Datacenter",
      "allowedValues": [
        "2008-R2-SP1",
        "2012-Datacenter",
        "2012-R2-Datacenter",
        "Windows-Server-Technical-Preview"
      ]
    }
  },
  "variables": {
    "availabilitySetName": "AvSet",
    "vhdStorageType": "Standard_LRS",
    "subnetName": "backendSubnet",
    "addressPrefix": "10.0.0.0/16",
    "subnetPrefix": "10.0.2.0/24",
    "IlbPrivateIpAddress": "10.0.2.6",
    "vnetId": "[resourceId('Microsoft.Network/virtualNetworks', parameters('virtualNetworkName'))]",
    "subnetRef": "[concat(variables('vnetId'), '/subnets/',variables ('subnetName'))]",
    "numberOfInstances": 2,
    "lbId": "[resourceId('Microsoft.Network/loadBalancers', parameters('loadBalancerName'))]",
    "vhdStorageName": "[concat('vhdStorage', uniqueString(resourceGroup().id))]",
    "PublicIPName": "PublicIP",
    "JumpBoxImagePublisher": "MicrosoftWindowsServer",
    "JumpBoxImageOffer": "WindowsServer",
    "JumpBoxOSDiskName": "JumpBoxOSDisk",
    "JumpBoxVmSize": "Standard_D1",
    "JumpBoxVnetID": "[resourceId('Microsoft.Network/virtualNetworks', parameters('virtualNetworkName'))]",
    "JumpBoxSubnetRef": "[concat(variables('JumpBoxVnetID'), '/subnets/', variables('subnetName'))]",
    "JumpBoxStorageAccountContainerName": "vhds",
    "JumpBoxNicName": "[concat(parameters('JumpBoxName'), 'NetworkInterface')]"
  },
  "resources": [
    {
      "apiVersion": "2015-05-01-preview",
      "type": "Microsoft.Storage/storageAccounts",
      "name": "[variables('vhdStorageName')]",
      "location": "[resourceGroup().location]",
      "tags": {
        "displayName": "StorageAccount"
      },
      "properties": {
        "accountType": "[variables('vhdStorageType')]"
      }
    },
    {
      "apiVersion": "2015-05-01-preview",
      "type": "Microsoft.Compute/availabilitySets",
      "name": "[variables('availabilitySetName')]",
      "location": "[resourceGroup().location]",
      "tags": {
        "displayName": "AvailabilitySet"
      },
      "properties": {
        "platformFaultDomainCount": 2,
        "platformUpdateDomainCount": 2
      }
    },
    {
      "apiVersion": "2015-05-01-preview",
      "type": "Microsoft.Network/virtualNetworks",
      "name": "[parameters('virtualNetworkName')]",
      "location": "[resourceGroup().location]",
      "tags": {
        "displayName": "VirtualNetwork"
      },
      "properties": {
        "addressSpace": {
          "addressPrefixes": [
            "[variables('addressPrefix')]"
          ]
        },
        "subnets": [
          {
            "name": "[variables('subnetName')]",
            "properties": {
              "addressPrefix": "[variables('subnetPrefix')]"
            }
          }
        ]
      }
    },
    {
      "apiVersion": "2015-05-01-preview",
      "type": "Microsoft.Network/networkInterfaces",
      "name": "[concat(parameters('networkInterfaceName'), copyindex())]",
      "location": "[resourceGroup().location]",
      "tags": {
        "displayName": "NetworkInterface"
      },
      "copy": {
        "name": "nicLoop",
        "count": "[variables('numberOfInstances')]"
      },
      "dependsOn": [
        "[concat('Microsoft.Network/virtualNetworks/', parameters('virtualNetworkName'))]",
        "[concat('Microsoft.Network/loadBalancers/', parameters('loadBalancerName'))]"
      ],
      "properties": {
        "ipConfigurations": [
          {
            "name": "[concat('ipconfig', copyindex())]",
            "properties": {
              "privateIPAllocationMethod": "Static",
              "privateIPAddress": "[concat('10.0.2.', add(copyindex(),5))]",
              "subnet": {
                "id": "[variables('subnetRef')]"
              },
              "loadBalancerBackendAddressPools": [
                {
                  "id": "[concat(variables('lbId'), '/backendAddressPools/BackendPool1')]"
                }
              ]
            }
          }
        ]
      }
    },
    {
      "apiVersion": "2015-05-01-preview",
      "type": "Microsoft.Network/loadBalancers",
      "name": "[parameters('loadBalancerName')]",
      "location": "[resourceGroup().location]",
      "tags": {
        "displayName": "LoadBalancer"
      },
      "dependsOn": [
        "[variables('vnetId')]"
      ],
      "properties": {
        "frontendIPConfigurations": [
          {
            "properties": {
              "privateIPAllocationMethod": "Dynamic",
              "subnet": { "id": "[variables('subnetRef')]" }
            },
            "name": "LoadBalancerFrontend"
          }
        ],
        "backendAddressPools": [
          {
            "name": "BackendPool1"
          }
        ],
        "loadBalancingRules": [
          {
            "properties": {
              "frontendIPConfiguration": {
                "id": "[concat(resourceId('Microsoft.Network/loadBalancers', parameters('loadBalancerName')), '/frontendIpConfigurations/LoadBalancerFrontend')]"
              },
              "backendAddressPool": {
                "id": "[concat(resourceId('Microsoft.Network/loadBalancers', parameters('loadBalancerName')), '/backendAddressPools/BackendPool1')]"
              },
              "probe": {
                "id": "[concat(resourceId('Microsoft.Network/loadBalancers', parameters('loadBalancerName')), '/probes/lbprobe')]"
              },
              "protocol": "Tcp",
              "frontendPort": 80,
              "backendPort": 80,
              "idleTimeoutInMinutes": 4,
              "loadDistribution": "sourceIP",
              "enableFloatingIP": true
            },
            "name": "httptraffic"
          }
        ],
        "probes": [
          {
            "properties": {
              "protocol": "Tcp",
              "port": 80,
              "intervalInSeconds": 15,
              "numberOfProbes": 2
            },
            "name": "lbprobe"
          }
        ]
      }
    },
    {
      "apiVersion": "2015-05-01-preview",
      "type": "Microsoft.Compute/virtualMachines",
      "name": "[concat(parameters('vmNamePrefix'), copyindex())]",
      "copy": {
        "name": "virtualMachineLoop",
        "count": "[variables('numberOfInstances')]"
      },
      "location": "[resourceGroup().location]",
      "tags": {
        "displayName": "VirtualMachines"
      },
      "dependsOn": [
        "[concat('Microsoft.Storage/storageAccounts/', variables('vhdStorageName'))]",
        "[concat('Microsoft.Network/networkInterfaces/', parameters('networkInterfaceName'), copyindex())]",
        "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]"
      ],
      "properties": {
        "availabilitySet": {
          "id": "[resourceId('Microsoft.Compute/availabilitySets', variables('availabilitySetName'))]"
        },
        "hardwareProfile": {
          "vmSize": "[parameters('vmSize')]"
        },
        "osProfile": {
          "computerName": "[concat(parameters('vmNamePrefix'), copyIndex())]",
          "adminUsername": "[parameters('adminUsername')]",
          "adminPassword": "[parameters('adminPassword')]"
        },
        "storageProfile": {
          "imageReference": {
            "publisher": "[parameters('imagePublisher')]",
            "offer": "[parameters('imageOffer')]",
            "sku": "[parameters('imageSKU')]",
            "version": "latest"
          },
          "osDisk": {
            "name": "osdisk",
            "vhd": {
              "uri": "[concat('http://', variables('vhdStorageName'), '.blob.core.windows.net/vhds/','osdisk', copyindex(), '.vhd')]"
            },
            "caching": "ReadWrite",
            "createOption": "FromImage"
          }
        },
        "networkProfile": {
          "networkInterfaces": [
            {
              "id": "[resourceId('Microsoft.Network/networkInterfaces',concat(parameters('networkInterfaceName'),copyindex()))]"
            }
          ]
        }
      }
    },
    {
      "name": "[variables('PublicIPName')]",
      "type": "Microsoft.Network/publicIPAddresses",
      "location": "[resourceGroup().location]",
      "apiVersion": "2015-05-01-preview",
      "dependsOn": [ ],
      "tags": {
        "displayName": "PublicIP"
      },
      "properties": {
        "publicIPAllocationMethod": "Dynamic",
        "dnsSettings": {
          "domainNameLabel": "[parameters('dnsNameForPublicIP')]"
        }
      }
    },
    {
      "name": "[variables('JumpBoxNicName')]",
      "type": "Microsoft.Network/networkInterfaces",
      "location": "[resourceGroup().location]",
      "apiVersion": "2015-05-01-preview",
      "dependsOn": [
        "[concat('Microsoft.Network/virtualNetworks/', parameters('virtualNetworkName'))]"
      ],
      "tags": {
        "displayName": "JumpBoxNic"
      },
      "properties": {
        "ipConfigurations": [
          {
            "name": "ipconfig1",
            "properties": {
              "privateIPAllocationMethod": "Static",
              "privateIPAddress": "10.0.2.99",
              "subnet": {
                "id": "[variables('subnetRef')]"
              },
              "publicIPAddress": { "id": "[resourceId('Microsoft.Network/publicIPAddresses', variables('PublicIPName'))]" }
            }
          }
        ]
      }
    },
    {
      "name": "[parameters('JumpBoxName')]",
      "type": "Microsoft.Compute/virtualMachines",
      "location": "[resourceGroup().location]",
      "apiVersion": "2015-05-01-preview",
      "dependsOn": [
        "[concat('Microsoft.Storage/storageAccounts/', variables('vhdStorageName'))]",
        "[concat('Microsoft.Network/networkInterfaces/', variables('JumpBoxNicName'))]"
      ],
      "tags": {
        "displayName": "JumpBox"
      },
      "properties": {
        "hardwareProfile": {
          "vmSize": "[variables('JumpBoxVmSize')]"
        },
        "osProfile": {
          "computerName": "[parameters('JumpBoxName')]",
          "adminUsername": "[parameters('adminUserName')]",
          "adminPassword": "[parameters('adminPassword')]"
        },
        "storageProfile": {
          "imageReference": {
            "publisher": "[variables('JumpBoxImagePublisher')]",
            "offer": "[variables('JumpBoxImageOffer')]",
            "sku": "[parameters('JumpBoxWindowsOSVersion')]",
            "version": "latest"
          },
          "osDisk": {
            "name": "JumpBoxOSDisk",
            "vhd": {
              "uri": "[concat('http://', variables('vhdStorageName'), '.blob.core.windows.net/', variables('JumpBoxStorageAccountContainerName'), '/', variables('JumpBoxOSDiskName'), '.vhd')]"
            },
            "caching": "ReadWrite",
            "createOption": "FromImage"
          }
        },
        "networkProfile": {
          "networkInterfaces": [
            {
              "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('JumpBoxNicName'))]"
            }
          ]
        }
      }
    }
  ]
}
```

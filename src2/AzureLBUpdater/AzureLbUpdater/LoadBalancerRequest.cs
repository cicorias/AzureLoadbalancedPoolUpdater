using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AzureLbUpdater
{
    public class LoadBalancerRequest
    {
        public string Name { get; set; }
        public string Id { get; set; }
        public string Type { get; set; }
        public string Location { get; set; }

        public LoadBalancerProperties Properties { get; set; }

        public LoadBalancerRequest()
        {
            this.Properties = new LoadBalancerProperties();
        }

    }


    public class LoadBalancerProperties
    {
        public List<IpConfigurationRequest> IpConfigurations { get; set; }
        public VirtualMachineRequest VirtualMachine { get; set; }

        public LoadBalancerProperties()
        {
            this.VirtualMachine = new VirtualMachineRequest();
        }
    }

    public class IpConfigurationRequest
    {
        public string Name { get; set; }
        public string Id { get; set; }
        public IpConfigurationProperties Properties { get; set; }

        public IpConfigurationRequest()
        {
            this.Properties = new IpConfigurationProperties();
        }
    }


    public class IpConfigurationProperties
    {
        public SubnetRequest Subnet { get; set; }

        /// <summary>
        /// just a collection of resource ids
        /// </summary>
        public List<LoadBalancerBackendProperties> LoadBalancerBackendAddressPools { get; set; }

        public IpConfigurationProperties()
        {
            this.LoadBalancerBackendAddressPools = new List<LoadBalancerBackendProperties>();
        }
    }

    public class LoadBalancerBackendProperties
    {
        public string Id { get; set; }
    }

    public class SubnetRequest
    {
        public string Id { get; set; }
    }

    public class VirtualMachineRequest
    {
        public string Id { get; set; }
    }


}

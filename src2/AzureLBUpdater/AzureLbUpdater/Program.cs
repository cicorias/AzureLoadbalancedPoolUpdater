using Microsoft.Azure.Management.Network;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;


using System.Net.Http.Formatting;
using Microsoft.IdentityModel.Clients.ActiveDirectory;
using Microsoft.Azure.Management.Compute;
using Microsoft.Azure.Management.Network.Models;
using System.IO;
using Newtonsoft.Json.Serialization;
using Microsoft.Azure.Management.Compute.Models;

namespace AzureLbUpdater
{
    class Program
    {
        static NetworkManagementClient s_netclient;
        static ComputeManagementClient s_computeClient;

        static void Main(string[] args)
        {
            Initialize();

            var config = Config.Current;

            Console.WriteLine("getting auth token");
            string token = InitializeToken();
            Console.WriteLine("done getting auth token");

            var resourceGroupName = "mshackilbfloat1";
            var subnetName = "backendSubnet";
            var virtualNetworkName = "ilbfloat";
            var newMaster = args[0];// "BackendVM1";
            var oldMaster = args[1];// "BackendVM0";
            var loadBalancerName = "webload";
            var backendPoolName = "BackendPool1";

            Console.WriteLine("making {0} the new master and {1} removing", newMaster, oldMaster);

            var newMasterVm = s_computeClient.VirtualMachines.Get(resourceGroupName, newMaster);
            var oldMasterVM = s_computeClient.VirtualMachines.Get(resourceGroupName, oldMaster);

            var subnet = s_netclient.Subnets.Get(resourceGroupName, virtualNetworkName, subnetName);

            var loadBalancer = s_netclient.LoadBalancers.Get(resourceGroupName, loadBalancerName);

            var newMasterNic = GetNicForVm(resourceGroupName, newMaster);
            var oldMasterNic = GetNicForVm(resourceGroupName, oldMaster);

            LoadBalancerRequest parametersOldMaster = GetUpdateRequest(oldMasterVM, oldMasterNic);


            LoadBalancerRequest parametersNewMaster = GetUpdateRequest(newMasterVm, newMasterNic);

            parametersNewMaster.Properties.IpConfigurations[0].Properties.LoadBalancerBackendAddressPools.Add(
                new LoadBalancerBackendProperties
                {
                    Id = loadBalancer.BackendAddressPools[0].Id
                });


            Console.WriteLine("SENDING REST REQUESTS... (1 of 2)");
            // now we send...  NO error checking done here right now..
            UpdateNic(parametersOldMaster, oldMasterNic.Id, token);
            Console.WriteLine("SENDING REST REQUESTS... (2 of 2)");
            UpdateNic(parametersNewMaster, newMasterNic.Id, token);
            Console.WriteLine("SENDING REST REQUESTS... (DONE)");

            Console.WriteLine("done...");


        }

        private static LoadBalancerRequest GetUpdateRequest(VirtualMachine vm, NetworkInterface nic)
        {
            var parametersNewMaster = new LoadBalancerRequest();

            parametersNewMaster.Id = nic.Id;
            parametersNewMaster.Name = nic.Name;
            parametersNewMaster.Location = vm.Location;
            parametersNewMaster.Type = "Microsoft.Network/networkInterfaces";
            parametersNewMaster.Properties.VirtualMachine.Id = vm.Id;

            var ipconfiguration = new IpConfigurationRequest
            {
                Id = nic.IpConfigurations[0].Id,
                Name = nic.IpConfigurations[0].Name,
                Properties = new IpConfigurationProperties
                {
                    LoadBalancerBackendAddressPools = new List<LoadBalancerBackendProperties>(),
                    Subnet = new SubnetRequest
                    {
                        Id = nic.IpConfigurations[0].Subnet.Id
                    }
                }
            };

            parametersNewMaster.Properties.IpConfigurations = new List<IpConfigurationRequest>();
            parametersNewMaster.Properties.IpConfigurations.Add(ipconfiguration);
            return parametersNewMaster;
        }

        private static string InitializeToken()
        {
            var token = GetToken();

            var creds = new Microsoft.Rest.TokenCredentials(token);

            s_netclient = new NetworkManagementClient(creds) { SubscriptionId = Config.Current.subscription_id };
            s_computeClient = new ComputeManagementClient(creds) { SubscriptionId = Config.Current.subscription_id };
            return token;
        }

        private static void Initialize()
        {
            JsonConvert.DefaultSettings = () => new JsonSerializerSettings
            {
                Formatting = Formatting.Indented,
                ContractResolver = new CamelCasePropertyNamesContractResolver()
            };
        }

        static void UpdateNic(LoadBalancerRequest parameters, string resourceId, string token)
        {

            var retryMax = 5;

            var client = s_netclient.HttpClient;
            client.DefaultRequestHeaders.Authorization = 
                new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

            var uri = s_netclient.BaseUri + resourceId + "?api-version=" + s_netclient.ApiVersion;

            //var response = client.PutAsJsonAsync(uri, parameters).Result;

            var body = new StringContent(
                JsonConvert.SerializeObject(parameters),
                Encoding.UTF8,
                "application/json");


            HttpResponseMessage response = null;

            while (retryMax > 0)
            {
                response = client.PutAsync(
                    uri,
                    body).Result;

                if (response.IsSuccessStatusCode && ((int)response.StatusCode) != 429)
                    break;
                else
                {
                    --retryMax;
                    Console.WriteLine(" Retrying operation... ");
                }
            }

            dynamic content = JsonConvert.DeserializeObject(
                response.Content.ReadAsStringAsync()
                .Result);


            if (! response.IsSuccessStatusCode)
            {
                Console.WriteLine("errors occured");
                Console.WriteLine(content);
            }


        }


        static NetworkInterface GetNicForVm(string groupName, string vmName)
        {
            string nicName = null;
            var vm = s_computeClient.VirtualMachines.Get(groupName, vmName);
            foreach (var item in vm.NetworkProfile.NetworkInterfaces)
            {
                var nic = item;
                nicName = nic.Id.Substring(nic.Id.LastIndexOf('/') + 1);
                break;
            }

            var theNic = GetNic(groupName, nicName);

            return theNic;
        }

        static NetworkInterface GetNic(string groupName, string nicName)
        {
            var nic = s_netclient.NetworkInterfaces.Get(groupName, nicName);

            return nic;
        }


        static string GetToken()
        {

            var ac = new Microsoft.IdentityModel.Clients.ActiveDirectory.AuthenticationContext(Config.Current.endpoint);

            var result = ac.AcquireToken(
                "https://management.core.windows.net/", 
                new ClientCredential(Config.Current.client_id, Config.Current.client_secret));

            return result.AccessToken;
        }




        static string GetTokencrap()
        {
            using (var client = new HttpClient())
            {

                var data = "grant_type=client_credentials" +
                    "&client_id=" + Config.Current.client_id +
                    "&client_secret=" + Config.Current.client_secret +
                    "&resource=https://management.core.windows.net/";

                //var response = client.PostAsJsonAsync(Config.Current.endpoint, data).Result;

                var body = new StringContent(
                        data,
                        Encoding.UTF8,
                        "application/x-www-form-urlencoded");

                var response = client.PostAsync(
                    Config.Current.endpoint,
                    body).Result;

                if (response.IsSuccessStatusCode)
                {
                    dynamic content = JsonConvert.DeserializeObject(
                        response.Content.ReadAsStringAsync()
                        .Result);

                    // Access variables from the returned JSON object
                    var appHref = content.links.applications.href;

                    return content.access_token;
                }
                else
                {
                    dynamic content = JsonConvert.DeserializeObject(
                        response.Content.ReadAsStringAsync()
                        .Result);

                }

            }

            return null;
        }

    }

}

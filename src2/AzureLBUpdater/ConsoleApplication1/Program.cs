using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ConsoleApplication1
{
    class Program
    {
        static void Main(string[] args)
        {
            var infile = File.ReadAllText("remove.json");
            var obj = JsonConvert.DeserializeObject(infile);

            Console.ReadLine();



        }

        static void test1()
        {
            var ResourceDefinition = new
            {
                properties = new
                {
                    virtualMachine = new { id = "111" },
                    ipConfigurations = new
                    {
                        properties = new { loadBalancerBackendAddressPools = new List<string>(), },
                        id = "111",
                        name = "111"
                    }

                },
                id = "111",
                name = "111",
                location = "111"
            };

            var settings = new JsonSerializerSettings();

            settings.NullValueHandling = NullValueHandling.Ignore;

            var bb = JsonConvert.SerializeObject(ResourceDefinition, Formatting.Indented, settings);
            Console.Write(bb);

        }
    }
}

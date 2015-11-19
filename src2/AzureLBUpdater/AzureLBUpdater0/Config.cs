using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AzureLBUpdater
{
    internal class Config
    {
        public string subscription_id { get; set; }
        public string client_id { get; set; }
        public string client_secret { get; set; }
        public string endpoint { get; set; }

        static Config s_current;

        static Config()
        {
            var inFile = File.ReadAllText("settings.private.json");
            var config = Newtonsoft.Json.JsonConvert.DeserializeObject<Config>(inFile);
            s_current = config;
        }


        public static Config Current
        {
            get
            {
                return s_current;
            }
        }

    }
}



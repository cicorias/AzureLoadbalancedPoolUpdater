# Updating Azure Load Balancer Backend Pool

Provides and approach for updating Azure Load Balancer – adding and removing Virtual Machines from the Back End Pool

* Current example written in C#
* Visual Studio 29015
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


## Video Walkthrough
View on Office Mix [Azure Load Balancer Back End Updates via REST](https://mix.office.com/MyMixes/Details/1zm4c3lcw51o)

Or via below on Azure Media Services
<iframe width="1184" height="715" src="https://scicoria.blob.core.windows.net/asset-3998123a-0d00-80c4-9e47-f1e58fbdf628/Azure%20Load%20Balancer%20Back%20End%20Updates%20via%20REST.2.mp4?sv=2012-02-12&sr=c&si=fcb70cfa-239f-4f78-a250-e432f7dba49e&sig=O8Goihhzxm1rR2HDP8JqIYxF29OWEjK79qg5NUmeeqc%3D&st=2015-11-20T19%3A36%3A42Z&se=2115-10-27T19%3A36%3A42Z" frameborder="0" allowfullscreen></iframe>

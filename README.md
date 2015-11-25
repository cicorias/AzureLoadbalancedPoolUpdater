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


## Video Walkthrough
### Python Version

### CSharp (C\#) Version
View on Office Mix [Azure Load Balancer Back End Updates via REST](https://mix.office.com/MyMixes/Details/1zm4c3lcw51o)

Or on YouTube [Azure Load Balancer Back End Updates via REST](https://youtu.be/ChOhpEpPHL8)

### Video in iframe..
<iframe width="1184" height="715" src="http://bit.ly/1MswxXq" frameborder="0"></iframe>


#### Via Mix
<iframe width="1184" height="715" src="https://mix.office.com/embed/1zm4c3lcw51o" frameborder="0"></iframe>
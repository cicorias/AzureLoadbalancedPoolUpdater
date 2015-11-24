import json


class LoadBalancerRequest(object):
    """description of class"""
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        #self.id = kwargs.get('id')
        #self.location = kwargs.get('location')
        #self.type = kwargs.get('type')
        #self.properties = kwargs.get('properties')

    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    def getName(self):
        return self.__name

    def setName(self, value):
        self.__name = value

    name = property(getName, setName)
    #@property
    #def name(self):
    #    return self.name

    #@name.setter
    #def name(self, value):
    #    self.name = value

    #@property
    #def id(self):
    #    return self.id

    #@id.setter
    #def id(self, value):
    #    self.id = value

    #@property
    #def type(self):
    #    return self.type

    #@type.setter
    #def type(self, value):
    #    self.type = value

    #@property
    #def location(self):
    #    return self.location

    #@location.setter
    #def location(self, value):
    #    self.location = value

    #@property
    #def properties(self):
    #    return self.properties

    #@properties.setter
    #def properties(self, value):
    #    self.properties = value

class LoadBalancerProperties(object):
    """description of class"""
    def __init__(self, **kwargs):
        self.name = kwargs.get('name') #dummy

class IpConfigurationRequest(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')  #dummy



class IpConfigurationProperties(object):
    def __init__(self, **kwargs):
        return super(IpConfigurationProperties, self).__init__(**kwargs)


class LoadBalancerBackendProperties(object):
    def __init__(self, **kwargs):
        return super(LoadBalancerBackendProperties, self).__init__(**kwargs)


class SubnetRequest(object):
    def __init__(self, **kwargs):
        return super(SubnetRequest, self).__init__(**kwargs)



class VirtualMachineRequest(object):
    def __init__(self, **kwargs):
        return super(VirtualMachineRequest, self).__init__(**kwargs)




import zenAPI.zenApiLib
import argparse
from tools import yaml_print, get_properties


def get_servicezprop(process, indent):
    zprop_keys = sorted([k for k in process if k.startswith('z')])
    header = False
    for k in zprop_keys:
        prop = process[k]
        if not prop['isAcquired']:
            if not header:
                yaml_print(key='zProperties', indent=indent)
                header = True
            yaml_print(key=k, value=prop['localValue'], indent=indent+2)

def get_serviceinstances(routers, uid, indent):
    service_router = routers['Service']
    response = service_router.callMethod('query', uid=uid, sort='name', dir='ASC')
    # print(response)
    service_list = response['result']['services']
    # print('services: {}'.format(len(service_list)))
    service_list = [s for s in service_list if s['uid'].startswith('{}/serviceclasses/'.format(uid))]
    # service_list = sorted(service_list, key=lambda i: i['name'])
    fields = ['port', 'serviceKeys', 'sendString', 'expectRegex', 'monitoredStartModes']
    header = False

    for service in service_list:
        # print(service)
        if not header:
            yaml_print(key='service_class', indent=indent)
            header = True
        yaml_print(key=service['name'], indent=indent+2)
        p_desc = service.get('description', '')
        if p_desc:
            yaml_print(key='description', value=p_desc, indent=indent+4)
        response = service_router.callMethod('getInfo', uid=service['uid'])
        service_info = response['result']['data']
        get_servicezprop(service_info, indent=indent+4)
        for k in fields:
            v = service_info.get(k, '')
            if v:
                yaml_print(key=k, value=v, indent=indent+4)


def parse_ipservicetree(routers, tree):
    tree = sorted(tree, key=lambda i: i['uid'])
    for branch in tree:
        # print(branch)
        branch_path = '/' + branch['path']
        branch_leaf = branch['leaf']
        branch_uid = branch['uid']
        yaml_print(key=branch_path, indent=2)

        # Properties
        get_properties(routers, branch_uid, 4)
        # Instances
        get_serviceinstances(routers, branch_uid, 4)

        children = branch.get('children', [])
        parse_ipservicetree(routers, children)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List services definition')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    options = parser.parse_args()

    environ = options.environ

    service_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='ServiceRouter')
    properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')

    routers = {
        'Service': service_router,
        'Properties': properties_router,
    }

    print('Checking Zenoss')

    # "getOrganizerTree": ["/zport/dmd/Services/IpService"]
    # "getInstances": {uid: "/zport/dmd/Services/IpService", page: 1, start: 0, limit: 50, sort: "name", dir: "ASC"}
    # "query": {params: {}, uid: "/zport/dmd/Services/IpService", page: 1, start: 0, limit: 200, sort: "name",}
    # "getInfo": {uid: "/zport/dmd/Services/IpService"}
    # "getInstances": {uid: "/zport/dmd/Services/IpService/Privileged/serviceclasses/aci", page: 1, start: 0, limit: 50}
    # "getInfo": {uid: "/zport/dmd/Services/IpService/Privileged/serviceclasses/aci"}

    response = service_router.callMethod('getOrganizerTree', id='/zport/dmd/Services')
    result = response['result']
    yaml_print(key='service_organizers', indent=0)
    parse_ipservicetree(routers, result)



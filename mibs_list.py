import zenAPI.zenApiLib
import argparse
from tools import yaml_print


def get_mibinfo(routers, uid, indent):
    mib_fields = ['name', 'contact', 'language', 'description']

    mib_router = routers['Mib']
    response = mib_router.callMethod('getInfo', uid=uid)
    data = response['result']['data']
    yaml_print(key=data['id'], indent=indent)
    for k in mib_fields:
        v = data.get(k, '')
        if v:
            yaml_print(key=k, value=v, indent=indent + 2)

def get_miboids(routers, uid, indent):
    mib_router = routers['Mib']
    response = mib_router.callMethod('getOidMappings', uid=uid)
    if not response['result']['success']:
        return
    data = sorted(response['result']['data'], key=lambda i: i['name'])

    oid_fields = ['name', 'oid', 'access', 'nodetype', 'status', 'description']

    if data:
        yaml_print(key='oids', indent=indent)
    for oid in data:
        yaml_print(key=oid['id'], indent=indent+2)
        for k in oid_fields:
            v = oid.get(k, '')
            if v:
                yaml_print(key=k, value=v, indent=indent + 4)


def parse_mibtree(routers, tree, indent):
    # tree = sorted(tree, key=lambda i: i['uid'])
    mib_router = routers['Mib']
    # print(len(tree))

    organizers = sorted([i for i in tree if not i['leaf']], key=lambda i: i['path'])
    mibs = sorted([i for i in tree if i['leaf']], key=lambda i: i['path'])


    if mibs:
        yaml_print(key='mibs', indent=indent + 2)
    for mib in mibs:
        mib_uid = mib['uid']
        get_mibinfo(routers, mib_uid, indent=indent + 4)
        get_miboids(routers, mib_uid, indent=indent + 4)

    for organizer in organizers:
        yaml_print(key=organizer['path'], indent=indent)
        organizer_uid = organizer['uid']

        children = organizer.get('children', [])
        if not children:
            response = mib_router.callMethod('getOrganizerTree', id=organizer_uid)
            children = response['result'][0]['children']
        if children:
            parse_mibtree(routers, children, indent)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage Manufacturers')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    options = parser.parse_args()
    environ = options.environ

    # Routers
    mib_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='MibRouter')
    properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')

    routers = {
        'Mib': mib_router,
        'Properties': properties_router,
    }

    # "getOrganizerTree": "/zport/dmd/Mibs"
    # "getInfo": [{uid: "/zport/dmd/Mibs/mibs/ACLMGMT-MIB", useFieldSets: false}]
    # "getOidMappings": [{uid: "/zport/dmd/Mibs/mibs/ACLMGMT-MIB", page: 1, start: 0, limit: 50, sort: "name", dir: "ASC"}]


    response = mib_router.callMethod('getOrganizerTree', id='/zport/dmd/Mibs')
    # print(response)
    tree = response['result']
    yaml_print(key='mibs_organizers')
    parse_mibtree(routers, tree, indent=2)

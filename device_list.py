import zenAPI.zenApiLib
import argparse
import re
from tools import yaml_print


def print_properties(routers, uid, indent):
    properties_router = routers['Properties']
    response = properties_router.callMethod('query', uid=uid, constraints={'idPrefix': 'c'})
    data = sorted(response['result']['data'], key=lambda i: i['id'])
    header = False
    for prop in data:
        if prop['islocal']:
            if not header:
                yaml_print(key='cProperties', indent=indent)
                header = True
            v = prop.get('valueAsString', '')
            if v:
                yaml_print(key=prop['id'], value=prop['valueAsString'], indent=indent+2)
    response = properties_router.callMethod('query', uid=uid, constraints={'idPrefix': 'z'})
    data = sorted(response['result']['data'], key=lambda i: i['id'])
    header = False
    for prop in data:
        if prop['islocal'] and prop['id'] not in ['zSnmpEngineId']:
            if not header:
                yaml_print(key='zProperties', indent=indent)
                header = True
            # print(prop)
            v = prop.get('valueAsString', '')
            if v:
                yaml_print(key=prop['id'], value=prop['valueAsString'], indent=indent+2)


def print_groups(routers):
    device_router = routers['Device']
    response = device_router.callMethod('getGroups', uid='/zport/dmd/Devices')
    groups = sorted(response['result']['groups'], key=lambda i: i['name'])
    header = False
    for group in groups:
        if not header:
            yaml_print(key='groups', indent=0)
            header = True
        g_uid = '/zport/dmd/Groups{}'.format(group['name'])
        response = device_router.callMethod('getInfo', uid=g_uid)
        data = response['result']['data']
        yaml_print(key=data['name'], indent=2)
        yaml_print(key='name', value=data['id'], indent=4)
        desc = data['description']
        if desc:
            yaml_print(key='description', value=desc, indent=4)

def print_systems(routers):
    device_router = routers['Device']
    response = device_router.callMethod('getSystems', uid='/zport/dmd/Devices')
    groups = sorted(response['result']['systems'], key=lambda i: i['name'])
    header = False
    for group in groups:
        if not header:
            yaml_print(key='systems', indent=0)
            header = True
        g_uid = '/zport/dmd/Systems{}'.format(group['name'])
        response = device_router.callMethod('getInfo', uid=g_uid)
        data = response['result']['data']
        yaml_print(key=data['name'], indent=2)
        yaml_print(key='name', value=data['id'], indent=4)
        desc = data['description']
        if desc:
            yaml_print(key='description', value=desc, indent=4)


def print_locations(routers):
    device_router = routers['Device']
    response = device_router.callMethod('getLocations', uid='/zport/dmd/Devices')
    groups = sorted(response['result']['locations'], key=lambda i: i['name'])
    header = False
    for group in groups:
        if not header:
            yaml_print(key='locations', indent=0)
            header = True
        g_uid = '/zport/dmd/Locations{}'.format(group['name'])
        response = device_router.callMethod('getInfo', uid=g_uid)
        data = response['result']['data']
        yaml_print(key=data['name'], indent=2)
        yaml_print(key='name', value=data['id'], indent=4)
        desc = data['description']
        if desc:
            yaml_print(key='description', value=desc, indent=4)

def print_dcdevices(routers, uid, indent):
    device_router = routers['Device']

    # Location, Priority, ProdState, tag
    # Systems, Groups, Locations, Comments

    device_fields = ['name', 'collector', 'ipAddressString', 'productionState', 'priority', 'comments',
                     'systems', 'groups', 'location']

    dc_devices = []
    for page in device_router.pagingMethodCall('getDevices', uid=uid, keys=['uid'], sort='name', dir='ASC'):
        # print(page)
        page_devices = page['result']['devices']
        for d in page_devices:
            if d['uid'].startswith('{}/devices/'.format(uid)):
                dc_devices.append(d['uid'])
        # print(len(devices))
    header = False
    dc_device_count = 0
    for device in dc_devices:
        if not header:
            yaml_print(key='devices', indent=indent)
            header = True
        dc_device_count += 1
        response = device_router.callMethod('getInfo', uid=device)
        data = response['result']['data']
        yaml_print(key=data['id'], indent=indent+2)
        print_properties(routers, device, indent+4)
        for k in device_fields:
            if k in ['systems', 'groups']:
                v = [g['path'] for g in data[k]]
            elif k in ['location']:
                if data[k]:
                    v = data[k]['name']
                else:
                    v = None
            else:
                v = data[k]
            if v:
                yaml_print(key=k, value=v, indent=indent + 4)

        # Templates
        response = device_router.callMethod('getTemplates', id=device)
        result = response['result']
        # print(result)
        d_templates = []
        for t in result:
            r = re.match('^(.*) \(.*\)', t['text'])
            if r:
                d_templates.append(r.group(1))
        if d_templates:
            d_templates.sort()
            yaml_print(key='templates', value=d_templates, indent=indent + 4)
    return dc_device_count


def print_alldevices(routers):
    device_router = routers['Device']
    response = device_router.callMethod('getDeviceClasses', uid='/zport/dmd/Devices')
    device_classes = sorted(response['result']['deviceClasses'], key=lambda i: i['name'])
    yaml_print(key='device_classes', indent=0)
    device_count = 0
    for device_class in device_classes:
        dc_name = device_class['name']
        if not dc_name:
            continue
        yaml_print(key=dc_name, indent=2)
        dc_uid = '/zport/dmd/Devices{}'.format(device_class['name'])
        response = device_router.callMethod('getInfo', uid=dc_uid, keys=['name'])
        data = response['result']['data']
        yaml_print(key='name', value=data['name'], indent=4)
        print_properties(routers, dc_uid, indent=4)
        device_count += print_dcdevices(routers, dc_uid, indent=4)

    print('# Device count: {}'.format(device_count))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List devices')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    options = parser.parse_args()
    environ = options.environ

    device_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='DeviceRouter')
    properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')

    routers = {
        'Device': device_router,
        'Properties': properties_router,
    }

    print_groups(routers)
    print_systems(routers)
    print_locations(routers)

    print_alldevices(routers)



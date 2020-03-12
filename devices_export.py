import zenAPI.zenApiLib
import argparse
import re
import yaml
import sys
from tqdm import tqdm

def get_properties(routers, uid):
    properties_router = routers['Properties']
    # TODO: take into account the type of the values (string, int...)
    # TODO: for cProperties, also export the type, label and description
    # cProperties
    response = properties_router.callMethod('query', uid=uid, constraints={'idPrefix': 'c'})
    data = sorted(response['result']['data'], key=lambda i: i['id'])
    prop_data = {}
    for prop in data:
        if prop['islocal']:
            if prop['type'] == 'date':
                v = prop.get('valueAsString', '')
            elif prop['type'] == 'string' or prop['type'] is None:
                v = prop.get('value', '')
                prop['type'] = 'string'
            elif prop['type'] == 'int':
                v = prop.get('value', None)
            else:
                print(prop)
                exit()
            if v:
                if 'cProperties' not in prop_data:
                    prop_data['cProperties'] = {}
                prop_data['cProperties'][prop['id']] = {}
                prop_data['cProperties'][prop['id']]['value'] = v
                prop_data['cProperties'][prop['id']]['type'] = prop.get('type', 'string')
    # zProperties
    response = properties_router.callMethod('query', uid=uid, constraints={'idPrefix': 'z'})
    data = sorted(response['result']['data'], key=lambda i: i['id'])
    for prop in data:
        if prop['islocal'] and prop['uid'] == uid and prop['id'] not in ['zSnmpEngineId']:
            # print(prop)
            if prop['type'] == 'boolean':
                v = bool(prop['value'])
            elif prop['type'] == 'int':
                if prop['value'] is None:
                    v = None
                else:
                    v = int(prop['value'])
            elif prop['type'] == 'float':
                v = float(prop['value'])
            elif prop['type'] in ['password', 'instancecredentials', 'multilinecredentials']:
                v = None
            elif prop['type'] == 'string':
                v = str(prop['value'])
            elif prop['type'] == 'lines':
                v = prop['value']           # List
            else:
                print(prop)
                exit()
            # v = prop.get('valueAsString', '')
            # What if v is boolean False ?
            # TODO: next condition to enhance
            if not v is None:
                if 'zProperties' not in prop_data:
                    prop_data['zProperties'] = {}
                prop_data['zProperties'][prop['id']] = v
    return prop_data


def get_groups(routers, output, full_data):
    device_router = routers['Device']
    response = device_router.callMethod('getGroups', uid='/zport/dmd/Devices')
    groups = sorted(response['result']['groups'], key=lambda i: i['name'])
    groups_data = {'groups': {}}
    for group in tqdm(groups, desc='Groups         ', ascii=True):
        g_uid = '/zport/dmd/Groups{}'.format(group['name'])
        response = device_router.callMethod('getInfo', uid=g_uid)
        data = response['result']['data']
        group_name = data['name']
        groups_data['groups'][group_name] = {}
        groups_data['groups'][group_name]['name'] = data['id']
        desc = data.get('description', '')
        if desc:
            groups_data['groups'][group_name]['description'] = desc
    full_data.update(groups_data)
    yaml.safe_dump(full_data, file(output, 'w'), encoding='utf-8', allow_unicode=True)
    return


def get_systems(routers, output, full_data):
    device_router = routers['Device']
    response = device_router.callMethod('getSystems', uid='/zport/dmd/Devices')
    systems = sorted(response['result']['systems'], key=lambda i: i['name'])
    systems_data = {'systems': {}}
    for system in tqdm(systems,desc='Systems        ', ascii=True):
        g_uid = '/zport/dmd/Systems{}'.format(system['name'])
        response = device_router.callMethod('getInfo', uid=g_uid)
        data = response['result']['data']
        system_name = data['name']
        systems_data['systems'][system_name] = {}
        systems_data['systems'][system_name]['name'] = data['id']
        desc = data.get('description', '')
        if desc:
            systems_data['systems'][system_name]['description'] = desc
    full_data.update(systems_data)
    yaml.safe_dump(full_data, file(output, 'w'), encoding='utf-8', allow_unicode=True)
    return


def get_locations(routers, output, full_data):
    device_router = routers['Device']
    response = device_router.callMethod('getLocations', uid='/zport/dmd/Devices')
    locations = sorted(response['result']['locations'], key=lambda i: i['name'])
    locations_data = {'locations': {}}
    for location in tqdm(locations, desc='Locations      ', ascii=True):
        g_uid = '/zport/dmd/Locations{}'.format(location['name'])
        response = device_router.callMethod('getInfo', uid=g_uid)
        data = response['result']['data']
        location_name = data['name']
        locations_data['locations'][location_name] = {}
        locations_data['locations'][location_name]['name'] = data['id']
        desc = data.get('description', '')
        if desc:
            locations_data['locations'][location_name]['name'] = desc
    full_data.update(locations_data)
    yaml.safe_dump(full_data, file(output, 'w'), encoding='utf-8', allow_unicode=True)
    return


def get_dcdevices(routers, uid):
    device_router = routers['Device']

    # tag
    # Comments

    device_fields = ['name', 'collector', 'ipAddressString', 'productionState', 'priority', 'comments',
                     'systems', 'groups', 'location']

    dc_devices = []
    for page in device_router.pagingMethodCall('getDevices', uid=uid, keys=['uid'], sort='name', dir='ASC'):
        page_devices = page['result']['devices']
        for d in page_devices:
            if d['uid'].startswith('{}/devices/'.format(uid)):
                dc_devices.append(d['uid'])
    devices_data = {}
    for device in dc_devices:
        if 'devices' not in devices_data:
            devices_data['devices'] = {}
        response = device_router.callMethod('getInfo', uid=device)
        data = response['result']['data']

        device_id = data['id']
        devices_data['devices'][device_id] = {}
        device_prop = get_properties(routers, device)
        devices_data['devices'][device_id].update(device_prop)
        for k in device_fields:
            if k in ['systems', 'groups']:
                v = sorted([g['path'] for g in data[k]])
            elif k in ['location']:
                if data[k]:
                    v = data[k]['name']
                else:
                    v = None
            else:
                v = data[k]
            if v:
                devices_data['devices'][device_id][k] = v

        # Templates
        response = device_router.callMethod('getTemplates', id=device)
        result = response['result']
        d_templates = []
        for t in result:
            r = re.match('^(.*) \(.*\)', t['text'])
            if r:
                d_templates.append(r.group(1))
        if d_templates:
            d_templates.sort()
            devices_data['devices'][device_id]['templates'] = d_templates
    return devices_data


def get_alldevices(routers, output, full_data):
    device_router = routers['Device']
    response = device_router.callMethod('getDeviceClasses', uid='/zport/dmd/Devices')
    device_classes = sorted(response['result']['deviceClasses'], key=lambda i: i['name'])
    # device_classes = device_classes[:10]
    devices_data = {'device_classes': {}}
    # with open(output, 'a') as f:
    #     f.write('device_classes:\r\n')

    dc_loop = tqdm(device_classes, desc='Device Class', ascii=True, file=sys.stdout)
    for device_class in dc_loop:
        dc_name = device_class['name']
        if not dc_name:
            continue
        desc = 'Device Class ({})'.format(dc_name)
        dc_loop.set_description(desc)
        dc_loop.refresh()

        devices_data['device_classes'][dc_name] = {}
        if dc_name == '/':
            dc_uid = '/zport/dmd/Devices'
        else:
            dc_uid = '/zport/dmd/Devices{}'.format(dc_name)
        response = device_router.callMethod('getInfo', uid=dc_uid, keys=['name'])
        data = response['result']['data']
        # dc_data = {dc_name: {}}
        devices_data['device_classes'][dc_name]['name'] = data['name']
        # dc_data[dc_name]['name'] = data['name']
        dc_props = get_properties(routers, dc_uid)
        devices_data['device_classes'][dc_name].update(dc_props)
        # dc_data[dc_name].update(dc_props)

        devices = get_dcdevices(routers, dc_uid)
        devices_data['device_classes'][dc_name].update(devices)

        # dc_data[dc_name].update(devices)
        # Can't find a way do dump yaml info with an original indent.
        # If possible, dump for each class when it's completed
        # yaml.safe_dump(dc_data, file(output, 'a'), encoding='utf-8', allow_unicode=True, indent=2, sort_keys=True)
        full_data.update(devices_data)
        yaml.safe_dump(full_data, file(output, 'w'), encoding='utf-8', allow_unicode=True, sort_keys=True)
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List devices')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    parser.add_argument('-f', dest='output', action='store', default='devices_output.yaml')
    options = parser.parse_args()
    environ = options.environ
    output = options.output

    device_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='DeviceRouter')
    properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')

    routers = {
        'Device': device_router,
        'Properties': properties_router,
    }

    '''
    response = properties_router.callMethod('query', uid='zport/dmd/Devices/Network/Switch',
                                            constraints={'idPrefix': 'z'})
    data = [p for p in response['result']['data'] if p['id'] == 'zDeviceTemplates']
    print(data)
    exit()
    '''

    # TODO: dump into file after each file or device class. Keep all data in one place and dump (write, not append)
    #  after each iteration ?
    data = {}
    get_groups(routers, output, data)
    get_systems(routers, output, data)
    get_locations(routers, output, data)
    get_alldevices(routers, output, data)


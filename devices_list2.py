import zenAPI.zenApiLib
import argparse
import csv
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


def get_dcdevices(routers, uid, writer):
    device_router = routers['Device']

    # Location, Priority, ProdState, tag
    # Systems, Groups, Locations, Comments

    device_fields = ['name', 'collector', 'ipAddressString', 'productionState', 'priority', 'comments',
                     'systems', 'groups', 'location']

    dc_Label = uid[18:]

    dc_devices = []
    for page in device_router.pagingMethodCall('getDevices', uid=uid, keys=['uid'], sort='name', dir='ASC'):
        # print(page)
        page_devices = page['result']['devices']
        for d in page_devices:
            if d['uid'].startswith('{}/devices/'.format(uid)):
                dc_devices.append(d['uid'])
        # print(len(devices))
    dc_device_count = 0
    for device in dc_devices:
        dc_device_count += 1
        response = device_router.callMethod('getInfo', uid=device)
        data = response['result']['data']

        # Devices, FQDN, IP Address, Device Type, Notes, Collectors
        prodState = data['productionState']
        if prodState < 0:
            continue
        osModel = data['osModel']
        if osModel:
            osModel = osModel['name']
        writer.writerow([dc_Label, data['id'], data['ipAddressString'], data['productionStateLabel'], osModel,
                         data['collector']])
        # print(data)
        #exit()

    return dc_device_count


def get_alldevices(routers):
    device_router = routers['Device']
    response = device_router.callMethod('getDeviceClasses', uid='/zport/dmd/Devices')
    device_classes = sorted(response['result']['deviceClasses'], key=lambda i: i['name'])
    device_count = 0

    csvfile = open('devices_list.csv', 'w')
    writer = csv.writer(csvfile, )

    for device_class in device_classes:
        dc_name = device_class['name']
        print(dc_name)
        if not dc_name:
            continue
        dc_uid = '/zport/dmd/Devices{}'.format(device_class['name'])
        # response = device_router.callMethod('getInfo', uid=dc_uid, keys=['name'])
        # data = response['result']['data']
        # print(data)
        # exit()
        # print_properties(routers, dc_uid, indent=4)
        device_count += get_dcdevices(routers, dc_uid, writer)

    csvfile.close()

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

    get_alldevices(routers)



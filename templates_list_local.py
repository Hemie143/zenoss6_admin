import zenAPI.zenApiLib
import re
import time
import argparse
from templates_tools import list_devices_templates, compare_templates
from devices_tools import get_devices_uids

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List local templates')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    parser.add_argument('-d', dest='devclass', action='store', default='Devices', help='Device Class')
    parser.add_argument('-n', dest='tname', action='store', default='', help='Template name')

    options = parser.parse_args()
    environ = options.environ
    devclass = options.devclass

    # Routers
    dr = zenAPI.zenApiLib.zenConnector(section=environ, routerName='DeviceRouter')
    tr = zenAPI.zenApiLib.zenConnector(section=environ, routerName='TemplateRouter')

    print('Fetching list of devices')
    devices = get_devices_uids(dr, devclass)
    if not devices:
        print('No device found under {}'.format(devclass))
        exit()
    print('Found {} devices'.format(len(devices)))

    print('Scanning devices for templates')
    local_templates = list_devices_templates(dr, tr, devices, local=True)
    print('Found {} local templates'.format(len(local_templates)))

    compare_templates(tr, local_templates)



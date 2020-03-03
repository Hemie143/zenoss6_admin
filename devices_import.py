import zenAPI.zenApiLib
import argparse
import re
import yaml
from tools import yaml_print

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import devices from YAML file')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    parser.add_argument('-f', dest='import_file', action='store', default='devices.yaml')
    options = parser.parse_args()
    environ = options.environ
    import_file = options.import_file

    device_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='DeviceRouter')
    properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')

    routers = {
        'Device': device_router,
        'Properties': properties_router,
    }

    with open(import_file, 'r') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        print(data)

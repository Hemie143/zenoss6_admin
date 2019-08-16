import zenAPI.zenApiLib
import re
import time
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List local templates')
    parser.add_argument('-s', dest='environ', action='store', default='z4_prod')
    options = parser.parse_args()
    environ = options.environ

    '''
    for dev in dmd.Devices.getSubDevices():
        for tpl in dev.getRRDTemplates():
            if dev == tpl.__primary_parent__:
                print "%s has local templates: %s" % (dev.id, tpl.id)
    '''
    # Routers
    dr = zenAPI.zenApiLib.zenConnector(section=environ, routerName='DeviceRouter')
    tr = zenAPI.zenApiLib.zenConnector(section=environ, routerName='TemplateRouter')

    device_gen = dr.pagingMethodCall('getDevices')
    print(device_gen)

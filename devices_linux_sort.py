import zenAPI.zenApiLib
import re
import time

dr = zenAPI.zenApiLib.zenConnector(section='zcloud', routerName='DeviceRouter')
pr = zenAPI.zenApiLib.zenConnector(section='zcloud', routerName='PropertiesRouter')
organizers = ['/zport/dmd/Devices/Server/SSH', '/zport/dmd/Devices/Server/Linux']

name_mapping = {
    'aca': '/Infrastructure/Linux/Acceptance',
    'acb': '/Infrastructure/Linux/Acceptance',
    'acc': '/Infrastructure/Linux/Acceptance',
    'ca': '/Infrastructure/Linux/Acceptance',
    'cc': '/Infrastructure/Linux/Production',
    'cd': '/Infrastructure/Linux/Development',
    'cp': '/Infrastructure/Linux/Production',
    'cs': '/Infrastructure/Linux/Staging',
    'ct': '/Infrastructure/Linux/Test',
    'dc1-': '/Infrastructure/Linux/Production',
    'dc2-': '/Infrastructure/Linux/Production',
    'dva-': '/Infrastructure/Linux/Development',
    'dvb-': '/Infrastructure/Linux/Development',
    'dvc-': '/Infrastructure/Linux/Development',
    'pr-': '/Infrastructure/Linux/Production',
    'pra-': '/Infrastructure/Linux/Production',
    'prb-': '/Infrastructure/Linux/Production',
    'prc-': '/Infrastructure/Linux/Production',
    'st-': '/Infrastructure/Linux/Staging',
    'stb-': '/Infrastructure/Linux/Staging',
    'tta-': '/Infrastructure/Linux/Test',
    'ttb-': '/Infrastructure/Linux/Test',
    'ttc-': '/Infrastructure/Linux/Test',
}

for organizer in organizers:
    d_count = 0
    for page in dr.pagingMethodCall('getDevices', uid=organizer, keys=['uid', 'name']):
        devices = page['result']['devices']
        for device in devices:
            deviceName = device['name']
            print(deviceName)
            for k, v in name_mapping.items():
                if deviceName.startswith(k):
                    deviceSystem = v
                    break
            else:
                print('Mapping not found for device: {}'.format(deviceName))
                exit(1)

            response = dr.callMethod('getInfo', uid=device['uid'], keys=['systems'])
            deviceSystemsNames = [s['name'] for s in response['result']['data']['systems']]
            if deviceSystem not in deviceSystemsNames:
                target = "/cz0/zport/dmd/Systems{}".format(deviceSystem)
                response = dr.callMethod('moveDevices', uids=[device['uid']], target=target)
                if not response['result']['success']:
                    print("Could not move device {} to System Org {}".format(deviceName, deviceSystem))
                    exit(1)
            d_count += 1

print("Processed {} devices.".format(d_count))



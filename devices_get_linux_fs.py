import zenAPI.zenApiLib
import re
import time

dr = zenAPI.zenApiLib.zenConnector(section='zcloud', routerName='DeviceRouter')
pr = zenAPI.zenApiLib.zenConnector(section='zcloud', routerName='PropertiesRouter')
organizers = ['/zport/dmd/Devices/Server/SSH']

for organizer in organizers:
    devices = dr.pagingMethodCall('getDevices', uid=organizer, keys=['uid', 'name'])
    d_count = 0
    for batch in devices:
        for device in batch['result']['devices']:
            d_uid = device['uid']
            d_devclass = ''
            r = re.match('/zport/dmd/Devices(.*)/devices', d_uid)
            if r:
                d_devclass = r.group(1)
            d_name = device['name']



            keys = ['server_name', 'totalBytes', 'storageDevice', 'type', 'name', 'productionState', 'mount']
            response = dr.callMethod("getComponents", uid=d_uid, meta_type='LinuxFileSystem', keys=keys)
            result = response['result']
            for fs in result['data']:
                print('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(d_devclass, d_name, fs['productionState'],
                                                                  fs['name'], fs['mount'], fs['type'],
                                                                  fs['server_name'], fs['storageDevice'],
                                                                  fs['totalBytes']))

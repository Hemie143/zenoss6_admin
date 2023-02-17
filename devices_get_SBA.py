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

            '''
            if not d_name.startswith('prb-app-l01'):
                continue
            '''

            keys = ['deviceName', 'sba_application', 'device', 'id', 'name', 'productionStateLabel']
            # response = dr.callMethod("getComponents", uid=d_uid, meta_type='LinuxFileSystem', keys=keys)
            # response = dr.callMethod("getComponents", uid=d_uid, meta_type='SpringBootAdminInstance',)

            for page in dr.pagingMethodCall("getComponents", uid=d_uid, meta_type='SpringBootAdminInstance', keys=keys):
                data = page['result']['data']
                # print(data[0])
                # print(page)
                for app_instance in data:
                    hostingServer = app_instance['name'].split()[-1]
                    print('{}\t{}\t{}\t{}\t{}\t{}'.format(app_instance['deviceName'],
                                                      app_instance['device']['productionStateLabel'],
                                                      app_instance['sba_application'],
                                                      app_instance['id'],
                                                      hostingServer,
                                                      app_instance['name'],
                                                      ))

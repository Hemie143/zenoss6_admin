import zenAPI.zenApiLib
import re
import time

dr = zenAPI.zenApiLib.zenConnector(section='z6_prod', routerName='DeviceRouter')
pr = zenAPI.zenApiLib.zenConnector(section='z6_prod', routerName='PropertiesRouter')
organizers = ['/zport/dmd/Devices/Server/Linux', '/zport/dmd/Devices/Server/SSH']

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
            prop_result = pr.callMethod('getZenProperty', uid=d_uid, zProperty='zCommandUsername')['result']
            prop_value = prop_result['data']['value']
            prop_path = prop_result['data']['path']
            prop_isLocal = prop_path == d_uid[18:]
            print('{}\t{}\t{}\t{}\t{}'.format(d_devclass, d_name, prop_value, prop_isLocal, prop_path))

            if prop_value == 'cs_monitoring' and not prop_isLocal:
                result = pr.callMethod('setZenProperty', uid=d_uid, zProperty='zCommandUsername', value='test')['result']
                # print(result)
                time.sleep(2)
                result = pr.callMethod('setZenProperty', uid=d_uid, zProperty='zCommandUsername', value='cs_monitoring')[
                    'result']

            if prop_value == 'zenoss' and prop_isLocal:
                result = pr.callMethod('deleteZenProperty', uid=d_uid, zProperty='zCommandUsername')['result']


            # print(prop_result)
            # print(d_uid[18:])
            # print(prop_path)
            d_count += 1

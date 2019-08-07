import zenAPI.zenApiLib
dr = zenAPI.zenApiLib.zenConnector(section='z6_prod', routerName='DeviceRouter')
response = dr.pagingMethodCall('getDevices', keys=['uid', 'groups'])

group_uid = '/zport/dmd/Groups/ALL'

for r in response:
    devices = r['result']['devices']
    for device in devices:
        member = any([g['uid']==group_uid for g in device['groups']])
        if member:
            continue
        d_uid = device['uid']
        print(d_uid)
        response = dr.callMethod('moveDevices', uids=[d_uid], target=group_uid)
        job_success = response['result']['success']
        if not job_success:
            print('Job failed: {}'.format(response['result']['new_jobs'][0]['description']))


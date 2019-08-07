import zenAPI.zenApiLib
import re
import time
import argparse

def find_device(router, hostname):
    print('Looking for device {}'.format(hostname))
    response = router.callMethod('getDevices', params={'name': hostname})
    if not response['result']['success']:
        print("Could not find device")
        exit(1)
    totalCount = response['result']['totalCount']
    if totalCount != 1:
        print('Found {} devices with hostname {}'.format(totalCount, hostname))
        exit(1)
    return response['result']['devices'][0]

def device_printinfo(router, device):
    print('Device found: {}'.format(device['name']))
    print('IP address: {}'.format(device['ipAddressString']))
    print('Production state: {}'.format(device['productionState']))
    # TODO: Report templates (device and components)
    response = router.callMethod('getBoundTemplates', uid=device['uid'])
    # print(response)
    d_templates = sorted(response['result']['data'])
    if d_templates:
        for template in d_templates:
            print('---Device Template: {}'.format(template[1]))

    response = router.pagingMethodCall('getComponents', uid=device['uid'], keys=['uid'])
    templates_found = set()
    components_dict = {}
    for r in response:      # response is a generator
        c = r['result']['data']
        for component in c:
            try:
                response = router.callMethod('getInfo', uid=component['uid'])
                '''
                if 'data' not in response['result']:
                    print(component)
                    print(response)
                '''
                c_class = response['result']['data']
                if 'class_plural_label' in c_class:
                    c_class = c_class['class_plural_label']
                else:
                    c_class = c_class['meta_type']
                # TODO: components_dict.setdefault(c_class, 1)
                if c_class in components_dict:
                    components_dict[c_class] = components_dict[c_class] + 1
                else:
                    components_dict[c_class] = 1
                response = tr.callMethod('getObjTemplates', uid=component['uid'])
                c_templates = sorted(response['result']['data'])
                if c_templates:
                    for template in c_templates:
                        template_id = '{} ({})'.format(template['name'], template['definition'])
                        if template_id not in templates_found:
                            print('----Component Template: {}'.format(template_id))
                            templates_found.add(template_id)
            except:
                pass
    # components_dict = components_dict.sort()
    for k in sorted(components_dict.keys()):
        print('{}: {}'.format(k, components_dict[k]))
    return

def move_device(router, device):
    d_uid = device['uid']
    r = re.search('/zport/dmd/Devices(.*)/devices/{}'.format(device['name']), d_uid)
    if not r:
        print('Current Device Class: Not Found')
        exit(1)
    d_class = r.group(1)
    print('Current Device Class: {}'.format(d_class))
    if '/Server/Linux' not in d_class:
        print('Device Class is not compatible')
        exit(1)
    # device['deviceClass'] = d_class
    r = re.search('/Server/Linux(.*)', d_class)
    d_class_new = '/Server/SSH/Linux{}'.format(r.group(1))
    # device['deviceClass_new'] = d_class_new
    d_class_new_list = d_class_new.split('/')
    # target = '/zport/dmd/Devices{}'.format('/'.join(d_class_new_list))
    target = '/zport/dmd/Devices{}'.format(d_class_new)
    print('New Device Class: {}'.format(d_class_new))

    response = router.callMethod('getDeviceClasses')
    device_classes_d = response['result']['deviceClasses']
    device_classes = [d['name'] for d in device_classes_d]
    if d_class_new in device_classes:
        print('New Device Class already present')
    else:
        print('Creating new Device Class')
        # TODO: Check that parent exists
        contextUid = '/zport/dmd/Devices{}'.format('/'.join(d_class_new_list[:-1]))
        id = d_class_new_list[-1]
        response = dr.callMethod('addDeviceClassNode', type='organizer', contextUid=contextUid, id=id)
        if not response['result']['success']:
            print('Device Class creation failed: {}'.format(response))
            exit(1)
        print('Device Class created')

    print('Moving device to: {}'.format(d_class_new))
    response = dr.callMethod('moveDevices', uids=[d_uid], target=target)
    if not response['result']['success']:
        print('Failed to create Job to move device')
        exit(1)
    jobid = response['result']['new_jobs'][0]['uuid']
    job_loop = 0
    while True:
        response = jr.callMethod('getInfo', jobid=jobid)
        job_status = response['result']['data']['status']
        if job_status == 'SUCCESS':
            break
        time.sleep(2)
        job_loop += 1
        if job_loop >= 10:
            print('Job did not finish in time')
            exit(1)
    print('Moved device to: {}'.format(d_class_new))
    d_uid_new = '{}/devices/{}'.format(target, hostname)
    device['d_uid_new'] = d_uid_new
    return

def device_editProperties(router, device):
    d_uid_new = device['d_uid_new']
    zProperty = 'zCommandUsername'
    response = router.callMethod('getZenProperty', uid=d_uid_new, zProperty=zProperty)
    username_old = response['result']['data']['value']
    username_new = 'zenoss'
    if username_new != username_old:
        response = router.callMethod('setZenProperty', uid=d_uid_new, zProperty=zProperty, value=username_new)
        # TODO: check operation
        response = router.callMethod('getZenProperty', uid=d_uid_new, zProperty=zProperty)
        username = response['result']['data']['value']
        print('Changed zCommandUsername from {} to {}'.format(username_old, username))

    zProperty = 'zSnmpEngineId'
    response = router.callMethod('deleteZenProperty', uid=d_uid_new, zProperty=zProperty)
    # TODO: check status
    print('Removed {}'.format(zProperty))
    return

def device_prodState(router, device, state):
    # print('--------------')
    # print(device)
    '''

    dr = zenAPI.zenApiLib.zenConnector(section='z6_prod', routerName='DeviceRouter')
    response = dr.callMethod('getDevices', params={'name': hostname})
    print(response)
    
    hash = response['result']['hash']
    
    device = response['result']['devices'][0]
    d_prodstate = device['productionState']
    d_uid = device['uid']
    
    print('hash: {}'.format(hash))
    print('Device prod state: {}'.format(d_prodstate))
    print('Device uid: {}'.format(d_uid))
    
    response = dr.callMethod('setProductionState', uids=[d_uid], prodState=300, hashcheck=hash)
    print(response)
    '''

    # response = router.callMethod('getDevices', uid=device['d_uid_new'])
    d_uid = device['d_uid_new']

    response = router.callMethod('getDevices', params={'uid': d_uid})
    # print(response)
    dev = response['result']['devices'][0]
    # print(dev)
    # print('hash' in dev)
    hash = response['result']['hash']
    # print('hash: {}'.format(hash))

    # response = router.callMethod('getInfo', uid=device['d_uid_new'])
    # print(response)

    response = router.callMethod('setProductionState', uids=[d_uid], prodState=state, hashcheck=hash)
    check = response['result']['success']
    success = 'SUCCESS' if check else 'FAIL'
    print('Set Production state to {}: {}'.format(state, success))
    # print(response)
    # print('--------------')
    return

def device_remodel(router, device):
    print('Remodeling {}'.format(hostname))
    d_uid_new = device['d_uid_new']
    response = router.callMethod('remodel', deviceUid=d_uid_new)
    jobid = response['result']['jobId']
    job_loop = 0
    while True:
        response = jr.callMethod('getInfo', jobid=jobid)
        job_status = response['result']['data']['status']
        if job_status == 'SUCCESS':
            break
        if job_status == 'FAILURE':
            print('Remodel job failed: {}'.format(response['result']['data']['errors']))
            break
        time.sleep(5)
        job_loop += 1
        if job_loop >= 40:
            print('Remodel job did not finish in time: {}'.format(job_status))
            print('response: {}'.format(response))
            exit(1)
    print('Remodeling job is over')
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate device to SSH')
    parser.add_argument('-d', dest='device', action='store', default='')
    options = parser.parse_args()

    hostname = options.device

    # Routers
    dr = zenAPI.zenApiLib.zenConnector(section='z6_prod', routerName='DeviceRouter')
    jr = zenAPI.zenApiLib.zenConnector(section='z6_prod', routerName='JobsRouter')
    pr = zenAPI.zenApiLib.zenConnector(section='z6_prod', routerName='PropertiesRouter')
    tr = zenAPI.zenApiLib.zenConnector(section='z6_prod', routerName='TemplateRouter')

    device = find_device(dr, hostname)
    prod_state = device['productionState']

    device_printinfo(dr, device)
    move_device(dr, device)
    device_editProperties(pr, device)
    device_prodState(dr, device, prod_state)
    device_remodel(dr, device)




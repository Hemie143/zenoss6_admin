import zenAPI.zenApiLib
import argparse

def find_device(router, device):
    # TODO: Change to pagingmethod if more than 50 devices
    response = router.callMethod('getDevices')
    devices = response['result']['devices']
    for d in devices:
        if d['name'] == device:
            return d['uid']
    return

def get_components(router, uid):
    # TODO: Paging
    '''
    for page in router.pagingMethodCall('getComponents', uid=uid):
        print(page)
        exit()
    '''
    response = router.callMethod('getComponents', uid=uid)
    print(response)
    components = response['result']['data']

    return [c['uid'] for c in components]

def delete_components(router, uids):
    response = router.callMethod('deleteComponents', uids=uids, hashcheck=None)
    print(response)
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clean device')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    parser.add_argument('-d', dest='device', action='store')
    options = parser.parse_args()
    environ = options.environ
    device = options.device

    device_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='DeviceRouter')
    d_uid = find_device(device_router, device)
    print('Found device: {}'.format(d_uid))
    while True:
        d_components = get_components(device_router, d_uid)
        print('Found {} components'.format(len(d_components)))
        if len(d_components) == 0:
            break
        print(d_components)
        exit()
        # delete_components(device_router, d_components)
        print('Deleted {} components'.format(len(d_components)))
    print('Finished job.')

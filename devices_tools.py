

def get_devices_uids(router, uid=None):
    response = router.callMethod('getDeviceUids', uid=uid)
    result = response['result']
    if not result['success']:
        print(result['msg'])
        return
    else:
        devices = response['result']['devices']
    return devices
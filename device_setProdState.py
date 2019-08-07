'''
setProductionState(uids, prodState, hashcheck, **ranges, **sort, **params, **uid, **dir)	Set the production state of device(s).

@type uids: [string]
@param uids: List of device uids to set
@type prodState: integer
@param prodState: Production state to set device(s) to.
@type hashcheck: string
@param hashcheck: Hashcheck for the devices (from getDevices())
@type uid: string
@param uid: (optional) Organizer to use when using ranges to get
additional uids (default: None)
@type ranges: [integer]
@param ranges: (optional) List of two integers that are the min/max
values of a range of uids to include (default: None)
@type params: dictionary
@param params: (optional) Key-value pair of filters for this search.
Can be one of the following: name, ipAddress,
deviceClass, or productionState (default: None)
@type sort: string
@param sort: (optional) Key on which to sort the return result (default:
'name')
@type dir: string
@param dir: (optional) Sort order; can be either 'ASC' or 'DESC'
(default: 'ASC')
@rtype: DirectResponse
@return: Success or failure message
'''

# State: Decommissioned (-1)
# Production:1000
# Staging:900
# Pre-Production:500
# Test:400
# Maintenance:300
# Decommissioned:-1
# Debug:-2

import zenAPI.zenApiLib

hostname = 'zeus'

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


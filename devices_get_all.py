import zenAPI.zenApiLib
dr = zenAPI.zenApiLib.zenConnector(section='z4_prod', routerName='DeviceRouter')
print(dr.callMethod('getDevices'))

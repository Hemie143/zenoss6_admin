import zenAPI.zenApiLib

dr = zenAPI.zenApiLib.zenConnector(section='z6_prod', routerName='DeviceRouter')
print(dr.callMethod('getDevices'))

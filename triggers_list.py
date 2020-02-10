import zenAPI.zenApiLib
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage Manufacturers')
    parser.add_argument('-s', dest='environ', action='store', default='z6_prod')
    # parser.add_argument('-f', dest='filename', action='store', default='local_templates.xlsx')
    options = parser.parse_args()
    environ = options.environ
    # filename = options.filename

    # Routers
    mr = zenAPI.zenApiLib.zenConnector(section=environ, routerName='ManufacturersRouter')

    # "getTriggers": {}
    # "getRecipientOptions": {}
    # "updateTrigger": {uuid: "c42ca88b-d5d9-4253-b875-6c35aae53915", enabled: true, name: "ActiveMQ_Delivery", rule: {,…},…}
    # "getNotifications": {}
    # "getWindows": {uid: "/zport/dmd/NotificationSubscriptions/ActiveMQ_Delivery"}
    # "getTriggerList": {}
    # "getRecipientOptions": {}
    # "updateNotification": [{uid: "/zport/dmd/NotificationSubscriptions/ActiveMQ_Delivery", enabled: true, send_clear: true,…}]

    result = mr.callMethod('getManufacturers')['result']    #dict (data, success)
    print(result)
    print(type(result))
    print(len(result))
    data = result['data']
    print(len(data))

    # id = data[1]['id']
    # response = mr.callMethod('getManufacturerData', uid=id)
    # print(response)
    result = mr.callMethod('getManufacturerList')['result']
    print(result)
    print(type(result))
    print(len(result))
    data = result['data']
    print(len(data))
    '''
    m = data[1]
    print(m)
    '''
    for m in data:
        if 'Check' in m['id']:
            print(m)
            result = mr.callMethod('getProductsByManufacturer', uid=m['uid'])['result']
            print(result)
            data = result['data']
            for p in data:
                if '.1.3.6.1.4.1.2620.1.6.123.1.69' in p['key']:
                    print(p)
                    params = {
                              # u'count': 4,
                              u'type': u'Hardware',
                              # u'id': u'.1.3.6.1.4.1.2620.1.6.123.1.69',
                              # u'key': [u'.1.3.6.1.4.1.2620.1.6.123.1.69'],     # Optional
                              u'oldname': 'Check Point 5800',
                              u'prodname': 'Check Point 5800',
                              u'prodkeys': '.1.3.6.1.4.1.2620.1.6.123.1.69',
                              u'partno': '',
                              u'description': '',
                              u'uid': u'/zport/dmd/Manufacturers/Check Point Software Technologies Ltd/products/Check Point 5800'
                              }
                    result = mr.callMethod('editProduct', params=params)
                    print(result)
                    print(result['result']['success'])
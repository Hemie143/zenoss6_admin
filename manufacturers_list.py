import zenAPI.zenApiLib
import argparse
from tools import yaml_print


def get_manufacturerdata(routers, uid, indent):
    manufacturer_router = routers['Manufacturers']
    response = manufacturer_router.callMethod('getManufacturerData', uid=uid)
    data = response['result']['data'][0]
    fields = ['phone', 'url', 'address1', 'address2', 'city', 'state', 'zip', 'country', 'regexes']
    for k in fields:
        v = data.get(k, '')
        if v:
            yaml_print(key=k, value=v, indent=indent)


def get_manufacturerproducts(routers, uid, indent):
    manufacturer_router = routers['Manufacturers']
    response = manufacturer_router.callMethod('getProductsByManufacturer', uid=uid)
    data = response['result']['data']
    data = sorted(data, key=lambda i: i['id'])
    header = False
    for product in data:
        if not header:
            yaml_print(key='products', indent=indent)
            header = True
        yaml_print(key=product['id'], indent=indent+2)
        yaml_print(key='type', value=product['type'], indent=indent+4)
        get_productdata(routers, uid, product['id'], indent+4)


def get_productdata(routers, uid, name, indent):
    manufacturer_router = routers['Manufacturers']
    response = manufacturer_router.callMethod('getProductData', uid=uid, prodname=name)
    data = response['result']['data'][0]
    fields = ['name', 'partno', 'prodKeys', 'desc', 'os']
    for k in fields:
        v = data.get(k, '')
        if v:
            yaml_print(key=k, value=v, indent=indent)


def parse_manufacturerlist(routers, list):
    list = sorted(list, key=lambda i: i['uid'])
    for manufacturer in list:
        manufacturer_path = '/' + manufacturer['path']
        manufacturer_uid = manufacturer['uid']
        yaml_print(key=manufacturer_path, indent=2)
        get_manufacturerproducts(routers, manufacturer_uid, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage Manufacturers')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    # parser.add_argument('-f', dest='filename', action='store', default='local_templates.xlsx')
    options = parser.parse_args()
    environ = options.environ
    # filename = options.filename

    # Routers
    manufacturer_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='ManufacturersRouter')
    properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')

    routers = {
        'Manufacturers': manufacturer_router,
        'Properties': properties_router,
    }

    # "getManufacturerList": {}
    # "getManufacturerList": {params: {}, uid: "/zport/dmd/Manufacturers/Adaptec"}
    # "getProductData": {uid: "/zport/dmd/Manufacturers/Adaptec", prodname: "Adaptec AHA-39160 _AIC-7899A_ Ultra160 SCSI Host Adapter"}
    # "getProductInstances": {params: {}, id: "Adaptec AHA-39160 _AIC-7899A_ Ultra160 SCSI Host Adapter", uid: "/zport/dmd/Manufacturers/Adaptec"}

    response = manufacturer_router.callMethod('getManufacturerList')
    data = response['result']['data']
    yaml_print(key='manufacturers', indent=0)
    parse_manufacturerlist(routers, data)

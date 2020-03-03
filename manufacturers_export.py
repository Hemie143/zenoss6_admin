import zenAPI.zenApiLib
import argparse
import yaml
from tqdm import tqdm


def get_manufacturerdata(routers, uid):
    manufacturer_router = routers['Manufacturers']
    response = manufacturer_router.callMethod('getManufacturerData', uid=uid)
    data = response['result']['data'][0]
    fields = ['phone', 'url', 'address1', 'address2', 'city', 'state', 'zip', 'country', 'regexes']
    data_json = {}
    for k in fields:
        v = data.get(k, '')
        if v:
            data_json[k] = v
    return data_json


def get_manufacturerproducts(routers, uid):
    manufacturer_router = routers['Manufacturers']
    response = manufacturer_router.callMethod('getProductsByManufacturer', uid=uid)
    data = response['result']['data']
    data = sorted(data, key=lambda i: i['id'])
    products_json = {}
    for product in tqdm(data, desc='    Products', ascii=True):
        if 'products' not in products_json:
            products_json['products'] = {}
        product_id = product['id']
        products_json['products'][product_id] = {}
        products_json['products'][product_id]['type'] = product['type']
        product_data = get_productdata(routers, uid, product['id'])
        products_json['products'][product_id].update(product_data)
    return products_json


def get_productdata(routers, uid, name):
    manufacturer_router = routers['Manufacturers']
    response = manufacturer_router.callMethod('getProductData', uid=uid, prodname=name)
    data = response['result']['data'][0]
    fields = ['name', 'partno', 'prodKeys', 'desc', 'os']
    data_json = {}
    for k in fields:
        v = data.get(k, '')
        if v:
            data_json[k] = v
    return data_json


def parse_manufacturerlist(routers, output):
    manufacturer_router = routers['Manufacturers']

    print('Retrieving all manufacturers')
    response = manufacturer_router.callMethod('getManufacturerList')
    data = response['result']['data']
    print('Retrieving {} manufacturers'.format(len(data)))

    manufacturers = sorted(data, key=lambda i: i['uid'])
    manufacturer_json = {}
    for manufacturer in tqdm(manufacturers, desc='Manufacturers', ascii=True):
        if 'manufacturers' not in manufacturer_json:
            manufacturer_json['manufacturers'] = {}
        manufacturer_path = '/' + manufacturer['path']
        manufacturer_uid = manufacturer['uid']
        manufacturer_json['manufacturers'][manufacturer_path] = {}
        man_data = get_manufacturerdata(routers, manufacturer_uid)
        manufacturer_json['manufacturers'][manufacturer_path].update(man_data)
        man_products = get_manufacturerproducts(routers, manufacturer_uid)
        manufacturer_json['manufacturers'][manufacturer_path].update(man_products)
    yaml.safe_dump(manufacturer_json, file(output, 'w'), encoding='utf-8', allow_unicode=True, sort_keys=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage Manufacturers')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    parser.add_argument('-f', dest='output', action='store', default='manufacturers_output.yaml')
    options = parser.parse_args()
    environ = options.environ
    output = options.output

    # Routers
    manufacturer_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='ManufacturersRouter')
    properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')

    routers = {
        'Manufacturers': manufacturer_router,
        'Properties': properties_router,
    }

    print('Connecting to Zenoss')
    parse_manufacturerlist(routers, output)

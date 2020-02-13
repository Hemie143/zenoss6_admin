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
    mib_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='MibRouter')
    properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')

    routers = {
        'Mib': mib_router,
        'Properties': properties_router,
    }

    # "getOrganizerTree": "/zport/dmd/Mibs"
    # "getInfo": [{uid: "/zport/dmd/Mibs/mibs/ACLMGMT-MIB", useFieldSets: false}]
    # "getOidMappings": [{uid: "/zport/dmd/Mibs/mibs/ACLMGMT-MIB", page: 1, start: 0, limit: 50, sort: "name", dir: "ASC"}]


    response = mib_router.callMethod('getOrganizerTree')
    print(response)

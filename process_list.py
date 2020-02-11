import zenAPI.zenApiLib
import argparse
from tools import yaml_print, get_properties


def get_processzprop(process, indent):
    zprop_keys = sorted([k for k in process if k.startswith('z')])
    header = False
    for k in zprop_keys:
        prop = process[k]
        if not prop['isAcquired']:
            if not header:
                yaml_print(key='zProperties', indent=indent)
                header = True
            yaml_print(key=k, value=prop['localValue'], indent=indent+2)

def get_processinstances(routers, uid, indent):
    process_router = routers['Process']
    response = process_router.callMethod('query', uid=uid)
    process_list = response['result']['processes']
    process_list = sorted(process_list, key=lambda i: i['name'])
    fields = ['includeRegex', 'excludeRegex', 'replaceRegex', 'replacement']
    header = False

    for process in process_list:
        if not process['uid'].startswith('{}/osProcessClasses/'.format(uid)):
            continue
        if not header:
            yaml_print(key='process_class', indent=indent)
            header = True
        yaml_print(key=process['name'], indent=indent+2)
        p_desc = process.get('description', '')
        if p_desc:
            yaml_print(key='description', value=p_desc, indent=indent+4)
        get_processzprop(process, indent=indent+4)
        for k in fields:
            v = process[k]
            if v:
                yaml_print(key=k, value=v, indent=indent+4)


def parse_processtree(routers, tree):
    tree = sorted(tree, key=lambda i: i['uid'])
    process_router = routers['Process']
    for branch in tree:
        branch_path = '/' + branch['path']
        branch_leaf = branch['leaf']
        branch_uid = branch['uid']
        yaml_print(key=branch_path, indent=2)

        branch_desc = branch['text']['description']
        yaml_print(key='description', value=branch_desc, indent=4)

        # Properties
        get_properties(routers, branch_uid, 4)
        # Instances
        get_processinstances(routers, branch_uid, 4)

        children = branch.get('children', [])
        parse_processtree(routers, children)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List processes definition')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    options = parser.parse_args()

    environ = options.environ

    process_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='ProcessRouter')
    properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')


    routers = {
        'Process': process_router,
        'Properties': properties_router,
    }

    print('Checking Zenoss')

    # getTree: /zport/dmd/Processes
    # getInstances: {uid: "/zport/dmd/Processes", page: 1, start: 0, limit: 50, sort: "name", dir: "ASC"}
    # query: {params: {}, uid: "/zport/dmd/Processes", page: 1, start: 0, limit: 400, sort: "name", dir: "ASC"}
    # getInfo: {uid: "/zport/dmd/Processes"}

    # PropertiesRouter: getZenProperties: {uid: "/zport/dmd/Processes/Zenoss/osProcessClasses/zencommand", page: 1, start: 0, limit: 300}
    # getInstances: {uid: "/zport/dmd/Processes/Zenoss/osProcessClasses/zencommand", page: 1, start: 0, limit: 50,}
    # getInfo: {uid: "/zport/dmd/Processes/Zenoss/osProcessClasses/zencommand"}

    process_tree = process_router.callMethod('getTree', id='/zport/dmd/Processes')
    # print(process_tree)
    result = process_tree['result']
    # print(result)
    # print(len(result))
    yaml_print(key='process_class_organizers', indent=0)
    parse_processtree(routers, result)

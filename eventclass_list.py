import zenAPI.zenApiLib
import argparse


def yaml_print(key='', value='', indent=0):
    head = indent*' '
    if key:
        key = '{}: '.format(key)
    if isinstance(value, list):
        value = str(value)      # To enhance...
    elif isinstance(value, int):
        value = str(value).decode('utf-8')
    elif isinstance(value, str):
        value = value.decode('utf-8')
    elif isinstance(value, unicode):
        pass
    else:
        print('value is of type: {}'.format(type(value)))
        exit()
    # value = value.decode('utf-8')

    multiline = len(value.splitlines()) > 1
    if multiline:
        print('{}{}|+'.format(head, key))
        for l in value.splitlines():
            # print('l: {}'.format(type(l)))
            print('  {}{}'.format(head, l.encode('utf-8')))
    else:
        if ':' in value or '%' in value or '#' in value:
            print('{}{}{!r}'.format(head, key, value))
        elif value.startswith("'") or value.startswith("["):
            print('{}{}{!r}'.format(head, key, value))
        else:
            print('{}{}{}'.format(head, key, value))


def get_properties(routers, uid, indent):
    properties_router = routers['Properties']
    response = properties_router.callMethod('getZenProperties', uid=uid)
    properties = response['result']['data']
    properties = sorted(properties, key=lambda i: i['id'])
    header = False
    for property in properties:
        if property['islocal'] == 1:
            if not header:
                yaml_print(key='zProperties', indent=indent)
                header = True
            yaml_print(key=property['id'], value=property['value'], indent=indent+2)
    return


def get_transforms(routers, uid):
    eventclass_router = routers['EventClasses']
    response = eventclass_router.callMethod('getTransformTree', uid=uid)
    data = response['result']['data']
    id = uid[10:]
    for transform in data:
        if transform['transid'] == id:
            yaml_print(key='transform', value=transform['trans'], indent=4)
    return

def get_mappings(routers, uid):
    eventclass_router = routers['EventClasses']
    response = eventclass_router.callMethod('getInstances', uid=uid)
    data = response['result']['data']
    header = False
    fields = ['eventClassKey', 'rule', 'regex', 'example', 'sequence', 'evaluation', 'resolution', 'transform']

    # ONLY MAPPINGS within same UID !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    for mapping in sorted(data, key=lambda i: i['id']):
        if not mapping['uid'].startswith('{}/instances/'.format(uid)):
            continue
        if not header:
            yaml_print(key='mappings', indent=4)
            header = True
        yaml_print(key=mapping['id'], indent=6)
        response = eventclass_router.callMethod('getInstanceData', uid=mapping['uid'])
        mapping_data = response['result']['data'][0]
        for k in fields:
            v = mapping_data[k]
            if v:
                yaml_print(key=k, value=v, indent=8)
        get_properties(routers, mapping['uid'], 8)


def parse_eventtree(routers, tree):
    tree = sorted(tree, key=lambda i: i['uid'])
    eventclass_router = routers['EventClasses']
    for branch in tree:
        branch_path = branch['path']
        branch_leaf = branch['leaf']
        branch_uid = branch['uid']
        yaml_print(key=branch_path, indent=2)

        # Properties
        get_properties(routers, branch_uid, 4)
        # Transforms
        if branch['text']['hasTransform']:
            get_transforms(routers, branch_uid)
        # Mappings
        get_mappings(routers, branch_uid)

        children = branch.get('children', [])
        if not branch_leaf and not children:

            response = eventclass_router.callMethod('asyncGetTree', id=branch_uid)
            children = response['result']
        parse_eventtree(routers, children)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List event classes definition')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    options = parser.parse_args()
    environ = options.environ

    print('Checking Zenoss')
    eventclass_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='EventClassesRouter')
    properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')

    routers = {
        'EventClasses': eventclass_router,
        'Properties': properties_router,
    }

    response = eventclass_router.callMethod('asyncGetTree', id='/zport/dmd/Events')
    root_tree = response['result']
    parse_eventtree(routers, root_tree)

import zenAPI.zenApiLib
import argparse
import re

def get_tree_templates(tree_branch, name_filter=None, known_templates=None):
    # Get all templates by Device Class. 626 on Z6_test
    # Returns a tree where nodes are device classes and leaves are templates
    # Dicts and lists are nested
    # Each lower layer is found in a 'children' key
    if not known_templates:
        known_templates = set()
    for n in tree_branch:
            if n['leaf'] and (n['uid'] not in known_templates):
                # print(n['uid'])
                if (name_filter and name_filter in n['uid']) or not name_filter:
                    known_templates.add(n['uid'])
            elif not n['leaf']:
                known_templates = known_templates.union(get_tree_templates(n['children'], name_filter, known_templates))
            else:
                pass
    return known_templates

def get_backup_templates(router):
    root_tree = router.callMethod('getDeviceClassTemplates', id='/zport/dmd/Devices')     # dict
    result = root_tree['result']                                                                   # list of 1 item (root)
    templates = get_tree_templates(result, name_filter='-backup')
    return templates

def delete_template(router, template_uid, deviceclass, template_name):
    t_data = router.callMethod('getInfo', uid=template_uid)['result']['data']
    t_name = t_data['name']
    t_deviceclass = t_data['text']

    to_delete = False
    if deviceclass and template_name and t_deviceclass == deviceclass and t_name.startswith(template_name):
        to_delete = True
    elif deviceclass and not template_name and t_deviceclass == deviceclass:
        to_delete = True
    elif template_name and not deviceclass and t_name.startswith(template_name):
        to_delete = True
    elif not template_name and not deviceclass:
        to_delete = True
    else:
        to_delete = False
    if to_delete:
        result = router.callMethod('deleteTemplate', uid=template_uid)['result']
        if result['success']:
            print(result['msg'])
        else:
            print('Failed to delete Template: {}  ({})'.format(t_name, t_deviceclass))
            print(result)
    else:
        print('Skipped Template: {}  ({})'.format(t_name, t_deviceclass))
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare upgrade templates')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    parser.add_argument('-d', dest='devclass', action='store', default='')
    parser.add_argument('-n', dest='tname', action='store', default='')
    options = parser.parse_args()
    environ = options.environ

    print('Connecting to Zenoss')
    template_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='TemplateRouter')
    print('Fetching the backup templates')
    backup_templates = sorted(get_backup_templates(template_router))
    print('Found {} backup templates'.format(len(backup_templates)))
    for t in backup_templates:
        delete_template(template_router, t, options.devclass, options.tname)



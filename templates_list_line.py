import zenAPI.zenApiLib
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare upgrade templates')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    options = parser.parse_args()

    environ = options.environ

    template_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='TemplateRouter')
    up_count = 0
    temp_count = 0

    print('Checking Zenoss')

    # Get all templates. Result length: 485 on Z6_test
    # Does not list all templates, but is fast

    root_tree = template_router.callMethod('getTemplates', id='/zport/dmd/Devices')     # dict
    result = root_tree['result']                                                        # list of many items

    i = 0
    templates_count = 0
    for r in result:
        t_uid = r['uid']
        # print(r['name'])
        templates = template_router.callMethod('getTemplates', id=t_uid)['result']
        templates_count += len(templates)
        for t in templates:
            # print('    {}'.format(t['text']))
            print('{}\t{}\t{}'.format(r['name'], t['text'], t['uid']))
    print(templates_count)

    print(len(result))
    t = list(filter(lambda r: 'backup' in r['uid'], result))
    print(t)
    print(len(t))       # 39



    # Get all templates by Device Class. 626 on Z6_test
    # Returns a tree where nodes are device classes and leaves are templates
    # Dicts and lists are nested
    # Each lower layer is found in a 'children' key

    '''
    root_tree = template_router.callMethod('getDeviceClassTemplates', id='/zport/dmd/Devices')     # dict
    result = root_tree['result']                                                                   # list of 1 item (root)

    def list_templates(tree_branch, known_templates=None):
        if not known_templates:
            known_templates = set()
        for n in tree_branch:
            if n['leaf'] and (n['uid'] not in known_templates):
                # print(n['uid'])
                known_templates.add(n['uid'])
            elif not n['leaf']:
                known_templates = known_templates.union(list_templates(n['children'], known_templates))
            else:
                pass
        return known_templates

    templates = list_templates(result)
    for t in templates:
        print(t)
    print(len(templates))
    tt = list(filter(lambda t: 'backup' in t, templates))
    print(tt)
    print(len(tt))  # 39
    '''

    '''
    # Get templates. Result length: 31 on Z6_test
    # Gets the templates defined just under the given uid, not deeper
    root_tree = template_router.callMethod('getObjTemplates', uid='/zport/dmd/Devices')     # dict of 6
    result = root_tree['result']                                                            # dict of 2
    data = result['data']                                                                   # list of 31
    for d in data:
        print(d['name'])
    '''
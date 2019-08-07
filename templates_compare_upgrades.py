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

    # TODO: some templates are renamed with <name>-upgrade-<numbers>, others to <name>-backup-upgrade-<numbers>
    templates = get_tree_templates(result, name_filter='-backup')
    return templates

def inspect_datasources(router, uid1, uid2):
    datasources1 = router.callMethod('getDataSources', uid=uid1)['result']['data']
    datasources1 = sorted(datasources1, key=lambda k: k['id'])
    datasources2 = router.callMethod('getDataSources', uid=uid2)['result']['data']
    datasources2_names = [i['name'] for i in datasources2]
    for ds1 in datasources1:
        ds1_name = ds1['name']
        if ds1_name not in datasources2_names:
            print('        Removed datasource {}'.format(ds1_name))
            continue
        ds1_uid = ds1['uid']
        ds2_uid = '{}/datasources/{}'.format(uid2, ds1_name)
        ds1_details = router.callMethod('getDataSourceDetails', uid=ds1_uid)['result']['record']
        ds2_details = router.callMethod('getDataSourceDetails', uid=ds2_uid)['result']['record']
        for k, v in ds1_details.iteritems():
            if k in ['id', 'uid']:
                continue
            if v != ds2_details[k]:
                print('        Difference for datasource {}: field {}'.format(ds1_name, k))
                print('            Old value={}'.format(v))
                print('            New value={}'.format(ds2_details[k]))
        datasources2_names.remove(ds1_name)
    if datasources2_names:
        print('        New datasources: {}'.format(','.join(datasources2_names)))
    return

def inspect_datapoints(router, uid1, uid2):
    datapoints1 = router.callMethod('getDataPoints', uid=uid1)['result']['data']
    datapoints1 = sorted(datapoints1, key=lambda k: k['id'])
    datapoints2 = router.callMethod('getDataPoints', uid=uid2)['result']['data']
    datapoints2_names = [i['name'] for i in datapoints2]
    for dp1 in datapoints1:
        dp1_name = dp1['name']
        if dp1_name not in datapoints2_names:
            print('        Removed datapoint {}'.format(dp1_name))
            continue
        dp1_uid = dp1['uid']
        r = re.match(r'(.*)/datasources/(.*)/datapoints/(.*)', dp1_uid)
        dp2_uid = '{}/datasources/{}/datapoints/{}'.format(uid2, r.group(2), r.group(3))
        dp1_details = router.callMethod('getDataPointDetails', uid=dp1_uid)['result']['record']
        dp2_details = router.callMethod('getDataPointDetails', uid=dp2_uid)['result']['record']
        aliases1_names = [i['name'] for i in dp1_details['aliases']]
        aliases2_names = [i['name'] for i in dp2_details['aliases']]

        for k, v in dp1_details.iteritems():
            if k in ['id', 'uid']:
                continue
            if k == 'aliases':
                for alias1 in v:
                    if alias1['name'] not in aliases2_names:
                        print('        Removed datapoint {} alias {}'.format(dp1_name, alias1['name']))
                        continue
                    alias2 = [x for x in dp2_details['aliases'] if x['name'] == alias1['name']][0]
                    for kk, vv in alias1.iteritems():
                        if kk in ['id', 'uid']:
                            continue
                        if vv != alias2[kk]:
                            print('        Difference for datapoint {}: alias field {}'.format(dp1_name, kk))
                            print('            Old value={}'.format(vv))
                            print('            New value={}'.format(alias2[kk]))
                    aliases2_names.remove(alias1['name'])
            elif v != dp2_details[k]:
                print('        Difference for datapoint {} field {}'.format(dp1_name, k))
                print('            Old value={}'.format(v))
                print('            New value={}'.format(dp2_details[k]))
        if aliases2_names:
            print('        New datapoint {} aliases: {}'.format(dp1_name, ','.join(aliases2_names)))
        datapoints2_names.remove(dp1_name)
    if datapoints2_names:
        print('        New datapoints: {}'.format(','.join(datapoints2_names)))
    return

def inspect_thresholds(router, uid1, uid2):
    thresholds1 = router.callMethod('getThresholds', uid=uid1)['result']['data']
    thresholds1 = sorted(thresholds1, key=lambda k: k['id'])
    thresholds2 = router.callMethod('getThresholds', uid=uid2)['result']['data']
    thresholds2_names = [i['name'] for i in thresholds2]
    for th1 in thresholds1:
        th1_name = th1['name']
        if th1_name not in thresholds2_names:
            print('        Removed threshold {}'.format(th1_name))
            continue
        th1_uid = th1['uid']
        th2_uid = '{}/thresholds/{}'.format(uid2, th1_name)
        th1_details = router.callMethod('getThresholdDetails', uid=th1_uid)['result']['record']
        th2_details = router.callMethod('getThresholdDetails', uid=th2_uid)['result']['record']
        for k, v in th1_details.iteritems():
            if k in ['id', 'uid']:
                continue
            if k not in th2_details.keys():
                print('        Difference for threshold {} field {} removed: value={}'.format(th1_name, k, v))
            elif v != th2_details[k]:
                # TODO : Inspect a level lower, as v is a list => compare lists
                print('        Difference for threshold {}: field {}'.format(th1_name, k))
                print('            Old value={}'.format(v))
                print('            New value={}'.format(th2_details[k]))

        thresholds2_names.remove(th1_name)
    if thresholds2_names:
        print('        New thresholds: {}'.format(','.join(thresholds2_names)))
    return

def inspect_graphs(router, uid1, uid2):
    graphs1 = router.callMethod('getGraphs', uid=uid1)['result']
    graphs1 = sorted(graphs1, key=lambda k: k['id'])
    graphs2 = router.callMethod('getGraphs', uid=uid2)['result']
    graphs2_names = [i['name'] for i in graphs2]
    for gr1 in graphs1:
        gr1_name = gr1['name']
        if gr1_name not in graphs2_names:
            print('        Removed graph: {}'.format(gr1_name))
            continue
        gr1_uid = gr1['uid']
        gr2_uid = '{}/graphDefs/{}'.format(uid2, gr1_name)
        gr1_def = router.callMethod('getGraphDefinition', uid=gr1_uid)['result']['data']
        gr2_def = router.callMethod('getGraphDefinition', uid=gr2_uid)['result']['data']
        for k, v in gr1_def.iteritems():
            if k in ['uid', 'fakeGraphCommands']:
                continue
            if v != gr2_def[k]:
                print('        Difference for graph {}: field {}'.format(gr1_name, k))
                print('            Old value={}'.format(v))
                print('            New value={}'.format(gr2_def[k]))

        gr1_points = router.callMethod('getGraphPoints', uid=gr1_uid)['result']['data']
        gr1_points = sorted(gr1_points, key=lambda k: k['id'])
        gr2_points = router.callMethod('getGraphPoints', uid=gr2_uid)['result']['data']
        gr2_points_names = [i['name'] for i in gr2_points]
        for gp1 in gr1_points:
            gp1_name = gp1['name']
            if gp1_name not in gr2_points_names:
                print('        Removed graph {} graphpoint {}'.format(gr1_name, gp1_name))
                continue
            gp2 = [i for i in gr2_points if i['id'] == gp1['id']][0]
            for k, v in gp1.iteritems():
                if k in ['uid']:
                    continue
                if v != gp2[k]:
                    print('        Difference for graph {} graphpoint {}: field {}'.format(gr1_name, gp1_name, k))
                    print('            Old value={}'.format(v))
                    print('            New value={}'.format(gp2[k]))
            gr2_points_names.remove(gp1_name)
        if gr2_points_names:
            print('        New graph {} graphpoint {}'.format(gr1_name, gp1_name))
        graphs2_names.remove(gr1_name)
    if graphs2_names:
        print('        New graphs: {}'.format(','.join(graphs2_names)))
    return

def inspect_template(router, template_uid):
    # child: [u'isOrganizer', u'qtip', u'leaf', u'uid', u'text', u'children', u'iconCls', u'path', u'hidden', u'id', u'uuid']

    t_data = router.callMethod('getInfo', uid=template_uid)['result']['data']
    t_name = t_data['name']
    t_deviceclass = t_data['text']

    print('Template: {}  ({})'.format(t_name, t_deviceclass))
    if template_uid.endswith('-backup'):
        new_template_uid = template_uid[:-7]
    else:
        r = re.match(r'(.*)-backup-preupgrade-\d+', template_uid)
        new_template_uid = r.group(1)
    result = router.callMethod('getInfo', uid=new_template_uid)['result']
    if not result['success']:
        print(result['msg'])
        return
    inspect_datasources(router, template_uid, new_template_uid)
    inspect_datapoints(router, template_uid, new_template_uid)
    inspect_thresholds(router, template_uid, new_template_uid)
    inspect_graphs(router, template_uid, new_template_uid)
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare upgrade templates')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    options = parser.parse_args()
    environ = options.environ

    print('Connecting to Zenoss')
    template_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='TemplateRouter')
    print('Fetching the backup templates')
    backup_templates = sorted(get_backup_templates(template_router))
    print('Found {} backup templates'.format(len(backup_templates)))
    for t in backup_templates:
        inspect_template(template_router, t)



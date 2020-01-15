from tqdm import tqdm
import re


def get_parent_template(router, uid):
    levels = uid.split('/')
    template_name = levels[-1]
    for i in range(len(levels)-3, 3, -1):
        root_uid = '{}/rrdTemplates/{}'.format('/'.join(levels[0:i]), template_name)
        # print('root_uid: {}'.format(root_uid))
        response = router.callMethod('getInfo', uid=root_uid)
        if response['result']['success'] and response['result']['data']['uid'] == root_uid:
            # print(root_uid)
            # print(response)
            return root_uid
    return

def list_local_templates(router, deviceClass='', templateName=''):

    def parse_templates(branch, templateName='', found_templates=None):
        if not found_templates:
            found_templates = set()
        for n in branch:
            if n['leaf'] and (n['uid'] not in found_templates) and n['text'].endswith('(Locally Defined)'):
                # print(n['uid'])
                parent = get_parent_template(router, n['uid'])
                if parent:
                    found_templates.add(n['uid'])
                    # t_info = router.callMethod('getInfo', uid=n['uid'])
                    # print(t_info)
                    # print(n)
                    # print(n['uid'])
                    # print(parent)
            elif n['leaf']:
                pass
            elif not n['leaf']:
                found_templates = found_templates.union(parse_templates(n['children'],
                                                                        templateName=templateName,
                                                                        found_templates=found_templates))
            else:
                pass
                print('Element found that is not a template, nor a branch')
                print(n)
        return found_templates

    id = '/zport/dmd/Devices{}'.format(deviceClass)
    root_tree = router.callMethod('getDeviceClassTemplates', id=id)  # dict
    result = root_tree['result']  # list of 1 item (root)
    return parse_templates(result, templateName)

def list_zenpacks_templates(router, template_router):
    result = router.callMethod('getZenPackMetaData')['result']
    for zp, zp_value in result['data'].items():
        # print(zp_value)
        zp_uid = zp_value['uid']
        uid = '{}/packables'.format(zp_uid)
        zp_info = template_router.callMethod('getInfo', uid=zp_uid)
        # zp_info = template_router.callMethod('getCollectorTemplate', id=uid)
        # zp_info = router.callMethod('getZenPackMetaData', zenpacks=[zp_uid])['result']
        print(zp_info)
    return

def list_devices_templates(device_router, template_router, devices, local=False):

    templates_set = set()

    def filter_templates(t_list):
        for t in t_list:
            if t['uid'] not in templates_set:
                if (local and 'devices' in t['uid']) or (not local):
                    templates_set.add(t['uid'])


    for dev_uid in tqdm(devices):
        # print(dev_uid)
        dev_templates = template_router.callMethod('getObjTemplates', uid=dev_uid)['result']['data']
        # print(dev_templates)
        '''
        for t in dev_templates:
            if t['uid'] not in templates_set:
                if (local and 'devices' in t['uid']) or (not local):
                    templates_set.add(t['uid'])
        '''
        filter_templates(dev_templates)
        components = device_router.pagingMethodCall('getComponents', uid=dev_uid, keys=['uid'])
        for c in components:
            dev_comp = c['result']['data']
            for c in dev_comp:
                comp_templates = template_router.callMethod('getObjTemplates', uid=c['uid'])['result']['data']
                filter_templates(comp_templates)
    return sorted(list(templates_set))

def compare_templates(router, t_list):
    for t in t_list:
        print(t)
        parent_uid = get_parent_template(router, t)
        compare_datasources(router, parent_uid, t)
        compare_datapoints(router, parent_uid, t)
        compare_thresholds(router, parent_uid, t)
        compare_graphs(router, parent_uid, t)

def compare_datasources(router, uid1, uid2):
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
            if k in ['id', 'uid', 'source']:
                continue
            if isinstance(v, bool):
                new_value = bool(ds2_details[k])
            elif isinstance(v, int):
                new_value = ds2_details[k]
                if isinstance(new_value, unicode) and new_value.isdigit():
                    new_value = int(new_value)
            else:
                new_value = ds2_details[k]
            if v != new_value:
                print('        Difference for datasource {}: field {}'.format(ds1_name, k))
                print('            Old value={} ({})'.format(v, type(v)))
                print('            New value={} ({})'.format(new_value, type(new_value)))
        datasources2_names.remove(ds1_name)
    if datasources2_names:
        print('        New datasources: {}'.format(','.join(datasources2_names)))
    return

def compare_datapoints(router, uid1, uid2):
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

def compare_thresholds(router, uid1, uid2):
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
            else:
                new_value = th2_details[k]
                if v != new_value:
                    # TODO : Inspect a level lower, as v is a list => compare lists
                    print('        Difference for threshold {}: field {}'.format(th1_name, k))
                    print('            Old value={} ({})'.format(v, type(v)))
                    print('            New value={} ({})'.format(new_value, type(new_value)))

        thresholds2_names.remove(th1_name)
    if thresholds2_names:
        print('        New thresholds: {}'.format(','.join(thresholds2_names)))
    return

def compare_graphs(router, uid1, uid2):
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
            if k in ['uid', 'fakeGraphCommands', 'rrdVariables']:
                continue
            new_value = gr2_def[k]
            if k in ['height']:
                v = int(v)
                new_value = int(new_value)
            if k in ['graphPoints']:
                v = ','.join(sorted(v.split(', ')))
                new_value = ','.join(sorted(new_value.split(', ')))
            if k in ['rrdVariables']:
                v = sorted(v)
                new_value = sorted(new_value)
            if v != new_value:
                print('        Difference for graph {}: field {}'.format(gr1_name, k))
                print('            Old value={} ({})'.format(v, type(v)))
                print('            New value={} ({})'.format(gr2_def[k], type(gr2_def[k])))

        gr1_points = router.callMethod('getGraphPoints', uid=gr1_uid)['result']['data']
        gr1_points = sorted(gr1_points, key=lambda k: k['id'])
        gr2_points = router.callMethod('getGraphPoints', uid=gr2_uid)['result']['data']
        gr2_points_names = [i['name'] for i in gr2_points]
        for gp1 in gr1_points:
            gp1_name = gp1['name']
            if gp1_name not in gr2_points_names:
                print('        Removed graph {} graphpoint {}'.format(gr1_name, gp1_name))
                continue
            gp2 = [i for i in gr2_points if i['id'] == gp1['id']]
            if not gp2:
                continue
            gp2 = gp2[0]
            for k, v in gp1.iteritems():
                if k in ['uid', 'rrdVariables']:
                    continue
                if v != gp2[k]:
                    print('        Difference for graph {} graphpoint {}: field {}'.format(gr1_name, gp1_name, k))
                    print('            Old value={}'.format(v))
                    print('            New value={}'.format(gp2[k]))
            gr2_points_names.remove(gp1_name)
        if gr2_points_names:
            print('        New graph "{}" graphpoints: {}'.format(gr1_name, gr2_points_names))
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

def get_template_uid(router, template_name, device_class=None, device_name=None, component=None, index=0, object_type=''):

    if device_class:
        # Device class is defined
        parent_uid = '/zport/dmd{}'.format(device_class)
        template_uid = '/zport/dmd{}/rrdTemplates/{}'.format(device_class, template_name)
    elif device_name:
        # Device name is defined
        # Look for device
        result = router.callMethod('getDevices', uid=None, params={'name': device_name})['result']
        if result['success'] and result['totalCount'] == 0:
            print('{} Row {}: Device not found: {}'.format(object_type, index, device_name))
            return None, None
        elif result['success'] and result['totalCount'] > 1:
            print('{} Row {}: Multiple devices matching name ({})'.format(object_type, index, device_name))
            return None, None
        device_uid = result['devices'][0]['uid']
        if component:
            result = router.callMethod('getComponents', uid=device_uid, name=component,
                                       keys=['name', 'uid', 'meta_type'])['result']
            comp_list = []
            for c in result['data']:
                if component == c['name']:
                    comp_list.append(c['uid'])
            if len(comp_list) != 1:
                # TODO: check for same template. If there's another component with the same name, it won't find it.
                # TODO: Template may not exist yet...
                # If needed, filter on relationship name which is close to template name in most cases. Not nice...
                comp_list = [c for c in comp_list if template_name.lower() in c.split('/')[-2].lower()]
                if len(comp_list) != 1:
                    print('{} Row {}: Multiple components: {}: {}'.format(object_type, index, component, comp_list))
                    return None, None
            component_uid = comp_list[0]
            parent_uid = component_uid
            template_uid = '{}/{}'.format(component_uid, template_name)
        else:
            # Device but no component
            parent_uid = device_uid
            template_uid = '{}/{}'.format(device_uid, template_name)

    return parent_uid, template_uid

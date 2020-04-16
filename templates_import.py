import zenAPI.zenApiLib
import argparse
import re
from collections import OrderedDict
import yaml
import sys
import time
from tqdm import tqdm


def import_datasource(routers, device_class, template_uid, datasource, ds_data):
    template_router = routers['Template']

    ds_uid = '{}/datasources/{}'.format(template_uid, datasource)
    # Test with objectExists does not always work...
    # response = template_router.callMethod('objectExists', uid=ds_uid)
    response = template_router.callMethod('getInfo', uid=ds_uid)
    # if not response['result']['success']:
    #     print(ds_uid)
    #     print(response)
    #     exit()
    if not response['result']['success'] or response['result']['data']['uid'] != ds_uid:
        response = template_router.callMethod('addDataSource', name=datasource, type=ds_data['type'],
                                              templateUid=template_uid)
        if not response['result']['success']:
            print(response)
            exit()

    # Change properties
    # response = template_router.callMethod('getDataSources', uid=template_uid)
    response = template_router.callMethod('getDataSourceDetails', uid=ds_uid)
    current_data = response['result']['record']
    new_info = {}
    for k, new_value in ds_data.items():
        if k in ['datapoints']:
            continue
        current_value = current_data.get(k, None)
        if current_value != new_value:
            new_info[k] = new_value
    if new_info:
        response = template_router.callMethod('setInfo', uid=ds_uid, **new_info)
        if not response['result']['success']:
            print(ds_uid)
            print(new_info)
            print(response)
            exit()

    # Datapoints
    if 'datapoints' not in ds_data:
        return
    response = template_router.callMethod('getDataPoints', uid=template_uid)
    if not response['result']['success']:
        print(response)
        exit()
    current_data = response['result']['data']
    new_info = {}
    for dp, dp_data in ds_data['datapoints'].items():
        dp_uid = '{}/datapoints/{}'.format(ds_uid, dp)
        current_dp = [x for x in current_data if x['uid'] == dp_uid]
        if not current_dp:
            response = template_router.callMethod('addDataPoint', dataSourceUid=ds_uid, name=dp)
            if not response['result']['success']:
                print(response)
                print(ds_uid)
                print(dp)
                exit()
            time.sleep(2)
            current_dp = {}
        else:
            current_dp = current_dp[0]
        new_info = {}
        for k, v in dp_data.items():
            current_value = current_dp.get(k, None)
            if current_value != v:
                new_info[k] = v
        if new_info:
            response = template_router.callMethod('setInfo', uid=dp_uid, **new_info)
            if not response['result']['success']:
                print(response)
                exit()
        '''
        aliases: [{id: "test", formula: "1, *"}, {id: "test2", formula: "2, *"}]
        '''
    return


def import_threshold(routers, device_class, template_uid, threshold, th_data):
    template_router = routers['Template']

    response = template_router.callMethod('getDataPoints', uid=template_uid)
    if not response['result']['success']:
        print(response)
        exit()
    datapoints = response['result']['data']
    dp_maps = {}
    for x in datapoints:
        r = re.match('{}/datasources/(.*)/datapoints/(.*)'.format(template_uid), x['uid'])
        if r:
            dp_maps['{}_{}'.format(r.group(1), r.group(2))] = x['uid']

    th_uid = '{}/thresholds/{}'.format(template_uid, threshold)
    response = template_router.callMethod('objectExists', uid=th_uid)
    if not response['result']['success']:
        print(response)
        exit()
    # TODO: if threshold exists but with a different type, it should be deleted first
    if not response['result']['exists']:
        th_type = th_data.get('type', 'MinMaxThreshold')
        response = template_router.callMethod('addThreshold', uid=template_uid, thresholdId=threshold,
                                              thresholdType=th_type, dataPoints=[])
        if not response['result']['success']:
            print(response)
            exit()

    # Change properties
    # response = template_router.callMethod('getDataSources', uid=template_uid)
    response = template_router.callMethod('getThresholdDetails', uid=th_uid)
    current_data = response['result']['record']
    new_info = {}
    for k, new_value in th_data.items():
        if k in ['xxx']:
            continue
        current_value = current_data.get(k, None)
        if current_value != new_value:
            new_info[k] = new_value

    if new_info:
        response = template_router.callMethod('setInfo', uid=th_uid, **new_info)
        if not response['result']['success']:
            print(response)
            print(th_uid)
            print(new_info)
            exit()
    return


def import_graph(routers, device_class, template_uid, graph, gr_data):
    template_router = routers['Template']

    gr_uid = '{}/graphDefs/{}'.format(template_uid, graph)
    response = template_router.callMethod('objectExists', uid=gr_uid)
    if not response['result']['success']:
        print(response)
        exit()
    if not response['result']['exists']:
        response = template_router.callMethod('addGraphDefinition', templateUid=template_uid,
                                              graphDefinitionId=graph)
        if not response['result']['success']:
            print(response)
            exit()

    # Change properties
    # response = template_router.callMethod('getDataSources', uid=template_uid)
    response = template_router.callMethod('getGraphDefinition', uid=gr_uid)
    if not response['result']['success']:
        print(response)
        exit()
    current_data = response['result']['data']
    # print(current_data)
    new_info = {}
    for k, new_value in gr_data.items():
        # print('{} - {} ({})'.format(k, new_value, type(new_value)))
        if k in ['graphpoints']:
            continue
        current_value = current_data.get(k, None)
        # print('{} ({}) - {}'.format(current_value, type(current_value), new_value))
        if current_value != new_value or type(current_value) != type(new_value):
            new_info[k] = new_value
    # print(new_info)
    if new_info:
        response = template_router.callMethod('setInfo', uid=gr_uid, **new_info)
        if not response['result']['success']:
            print(response)
            exit()

    # Graphpoints
    if 'graphpoints' not in gr_data:
        return
    # Get current graphpoints
    response = template_router.callMethod('getGraphPoints', uid=gr_uid)
    if not response['result']['success']:
        print(response)
        exit()
    current_data = response['result']['data']
    # Get Datapoints
    response = template_router.callMethod('getDataPoints', uid=template_uid)
    if not response['result']['success']:
        print(response)
        exit()
    datapoints = response['result']['data']
    dp_maps = {}
    for x in datapoints:
        r = re.match('{}/datasources/(.*)/datapoints/(.*)'.format(template_uid), x['uid'])
        if r:
            dp_maps['{}_{}'.format(r.group(1), r.group(2))] = x['uid']

    # Get Thresholds
    response = template_router.callMethod('getThresholds', uid=template_uid)
    if not response['result']['success']:
        print(response)
        exit()
    thresholds = response['result']['data']
    th_maps = {x['name']: x['uid'] for x in thresholds}

    for gp, gp_data in gr_data['graphpoints'].items():
        #TODO: correct following, not correctly checking whether Threshold is present if not using default id
        gp_uid = '{}/graphPoints/{}'.format(gr_uid, gp)
        current_gp = [x for x in current_data if x['uid'] == gp_uid]
        # print('current_gp: {}'.format(current_gp))
        if not current_gp:
            gp_type = gp_data.get('type', 'DataPoint')
            if gp_type == 'DataPoint':
                # print('Create graphpoint')
                gp_dpname = gp_data['dpName']
                dataPointUid = dp_maps[gp_dpname]
                response = template_router.callMethod('addDataPointToGraph', dataPointUid=dataPointUid, graphUid=gr_uid)
                if not response['result']['success']:
                    print(response)
                    exit()
                # By default, the gp name is based on dpName.
                gp_default_name = '_'.join(gp_dpname.split('_')[1:])
                gp_uid = '{}/graphPoints/{}'.format(gr_uid, gp_default_name)
                if gp_default_name != gp:
                    time.sleep(2)
                    response = template_router.callMethod('setInfo', uid=gp_uid, newId=gp)
                    if not response['result']['success']:
                        print(response)
                        exit()
                gp_uid = '{}/graphPoints/{}'.format(gr_uid, gp)
                time.sleep(2)
                current_gp = {}
            elif gp_type == 'Threshold':
                # print('Create threshold')
                gp_id = gp_data['description']
                response = template_router.callMethod('addThresholdToGraph', thresholdUid=th_maps[gp_id], graphUid=gr_uid)
                if not response['result']['success']:
                    print(response)
                    exit()
                time.sleep(2)
                current_gp = {}
                gp_uid = '{}/graphPoints/{}'.format(gr_uid, gp_id)
            else:
                print(gp_uid)
                print(gp_type)
                exit()
        else:
            current_gp = current_gp[0]
        new_info = {}
        for k, v in gp_data.items():
            if k in ['dpName', 'description', 'type']:
                continue
            current_value = current_gp.get(k, None)
            if current_value != v:
                new_info[k] = v
        if new_info:
            response = template_router.callMethod('setInfo', uid=gp_uid, **new_info)
            if not response['result']['success']:
                print(gp_uid)
                print(new_info)
                print(response)
                exit()
    return


def create_template(routers, dc_uid, template_id):
    template_router = routers['Template']
    if 'devices' in dc_uid:
        response = template_router.callMethod('makeLocalRRDTemplate', templateName=template_id, uid=dc_uid)
    else:
        response = template_router.callMethod('addTemplate', id=template_id, targetUid=dc_uid)
    if not response['result']['success']:
        print(response)
        exit()
    return


def import_template(routers, device_class, template, template_data):
    template_router = routers['Template']

    # print('device_class: {}'.format(device_class))
    # print('template: {}'.format(template))
    # print('template_data: {}'.format(template_data))

    if device_class == '/':
        dc_uid = '/zport/dmd/Devices'
        template_uid = '/zport/dmd/Devices/rrdTemplates/{}'.format(template)
    elif '/devices/' in device_class:
        # dc = /Datacenter/Raritan/devices/dc3-probe-s01.fednot.be/raritanHumiditySensors/Relative Humidity 1/RaritanHumiditySensor

        dc_uid = '/zport/dmd/Devices{}'.format(device_class)
        # /zport/dmd/Devices/Datacenter/Raritan/devices/dc3-probe-s01.fednot.be/raritanHumiditySensors/Relative Humidity 1/RaritanHumiditySensor
        template_uid = '/zport/dmd/Devices{}/{}'.format(device_class, template)

    else:
        dc_uid = '/zport/dmd/Devices{}'.format(device_class)
        template_uid = '/zport/dmd/Devices{}/rrdTemplates/{}'.format(device_class, template)

    # print(dc_uid)
    # print(template_uid)

    response = template_router.callMethod('objectExists', uid=template_uid)
    if not response['result']['success']:
        print(response)
        exit()
    if not response['result']['exists']:
        # print('create_template')
        create_template(routers, dc_uid, template)

    # Properties
    response = template_router.callMethod('getInfo', uid=template_uid)
    if not response['result']['success']:
        print(response)
        exit()
    current_data = response['result']['data']
    new_info = {}
    for k, v in template_data.items():
        if k in ['datasources', 'thresholds', 'graphs']:
            continue
        current_value = current_data.get(k, None)
        if current_value != v:
            new_info[k] = v
    if new_info:
        response = template_router.callMethod('setInfo', uid=template_uid, **new_info)
        if not response['result']['success']:
            print(response)
            exit()

    # Datasources & Datapoints
    if 'datasources' in template_data:
        datasources = template_data['datasources']
        for datasource, ds_data in sorted(datasources.items()):
            import_datasource(routers, device_class, template_uid, datasource, ds_data)

    # Thresholds
    if 'thresholds' in template_data:
        thresholds = template_data['thresholds']
        for threshold, th_data in thresholds.items():
            import_threshold(routers, device_class, template_uid, threshold, th_data)

    # Graphs & Graphpoints
    if 'graphs' in template_data:
        graphs = template_data['graphs']
        for graph, gr_data in graphs.items():
            import_graph(routers, device_class, template_uid, graph, gr_data)

    return

def parse_templates(routers, output):
    print('Loading input file')
    data = yaml.safe_load(file(filename, 'r'))         # dict
    print('Loaded input file')
    if 'device_classes' not in data:
        print('No device class found. Skipping.')
        return
    device_classes = sorted(data['device_classes'])
    print('Found {} device_classes in input'.format(len(device_classes)))

    dc_loop = tqdm(device_classes, desc='Device Classes', ascii=True, file=sys.stdout)
    for device_class in dc_loop:
        dc_loop.set_description('Device Class ({})'.format(device_class))
        dc_loop.refresh()
        dc_data = data['device_classes'][device_class]['templates']
        template_names = sorted(dc_data.keys())

        t_loop = tqdm(template_names, desc='    Templates', ascii=True, file=sys.stdout)
        for template in t_loop:
            t_loop.set_description('    Template ({})'.format(template))
            t_loop.refresh()
            template_data = dc_data[template]
            import_template(routers, device_class, template, template_data)
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List templates definition')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    parser.add_argument('-f', dest='input', action='store', default='templates_input.yaml')
    options = parser.parse_args()
    environ = options.environ
    filename = options.input

    template_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='TemplateRouter')
    properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')

    routers = {
        'Template': template_router,
        'Properties': properties_router,
    }

    # yaml_print(key='device_classes', indent=0)
    print('Connecting to Zenoss')
    parse_templates(routers, filename)

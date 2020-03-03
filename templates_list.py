import zenAPI.zenApiLib
import argparse
import re
from tools import yaml_print
from collections import OrderedDict

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


def get_parent_template(routers, uid):
    template_router = routers['Template']
    levels = uid.split('/')
    template_name = levels[-1]
    for i in range(len(levels)-3, 3, -1):
        root_uid = '{}/rrdTemplates/{}'.format('/'.join(levels[0:i]), template_name)
        response = template_router.callMethod('getInfo', uid=root_uid)
        if response['result']['success'] and response['result']['data']['uid'] == root_uid:
            return root_uid
    return


ds_all_fields = set()
dp_all_fields = set()
th_all_fields = set()
gr_all_fields = set()
gp_all_fields = set()
templates_devices = []

def print_datasources(routers, uid, indent):
    template_router = routers['Template']
    response = template_router.callMethod('getDataSources', uid=uid)
    ds_data = response['result']['data']

    if not ds_data:
        return

    response = template_router.callMethod('getDataPoints', uid=uid)
    dp_data = response['result']['data']

    '''
    [
     
     ('jmxPort', None), ('availableParsers', None), ('source', None), ('jmxProtocol', None), 
     ('raw20', None), ('attributeName', None), ('password', None), ('plugin_classname', None), 
     ('resource', None), ('name', None), ('jmxRawService', None), ('minimumInterval', None)
     ('meta_type', None), ('timeout', None), ('debug', None), ('ilo_result_key', None), 
     ('ports', None), ('operationParamValues', None), ('operationParamTypes', None), 
     ('webTxTimeout', None), ('statusname', None), ('group_key', None), ('operation', None), 
     ('port', None), ('description', None), ('ldapServer', None), ('authenticate', None), 
     ('ldapBaseDN', None), ('ldapBindVersion', None), ('rollup', None), ('critical', None), 
     ('result_component_value', None), ('useBasisInterval', None), ('host', None), 
     ('rmiContext', None), ('inspector_type', None), ('expression', None), ('entity_id', None), 
     ('useSSL', None), ('class_name', None), ('classname', None), ('testable', None), 
     ('cycleTime', None), ('script', None), ('strategy', None), ('result_component_key', None),
     ('username', None), ('objectName', None), ('queryset', None), ('ilo_query', None), 
     ('availableStrategies', None), ('recording', None), ('counter_key', None), 
     ('ilo_component_name_xpath', None), ('ilo_status_values', None), ('asRate', None), 
     ('uid', None), ('xpath_query', None), ('timeout_delay', None), 
     ('ilo_status_monitor', None), ('warning', None), ('maximumInterval', None), ('id', None), 
     ('property_name', None), ('initialPassword', None), ('result_value_key', None), 
     ('hostname', None), ('namespace', None), ('usePowershell', None), ('attributePath', None), 
     ('instance', None), ('expectedIpAddress', None), ('ldapBindDN', None), 
     ('ldapBindPassword', None), ('user', None), ('initialUser', None), ('chunk_size', None), 
     ('initialURL', None), ('dnsServer', None), ('database', None), ('counter', None), 
     ('dbtype', None), ('command', None)
     ]
    '''

    # TODO : commandTemplate not collected ?
    ds_fields = OrderedDict([('type', None), ('enabled', True), ('plugin_classname', None), ('component', ''),
                             ('eventClass', ''), ('eventKey', ''), ('severity', 3), ('cycletime', 300), ('oid', None),
                             ('commandTemplate', None), ('usessh', False), ('parser', 'Auto'),
                             ('extraContexts', None), ('initialRealm', None), ('userAgent', None),
                             ('user', None), ('password', None),
                             ('raw20_aggregation', None), ('raw20', None),
                             ('jmxPort', None),  ('jmxProtocol', 'RMI'), ('rmiContext', 'jmxrmi'),
                             ('ldapServer', None), ('ldapBaseDN', None), ('ldapBindVersion', None),
                             ('ldapBindDN', None), ('ldapBindPassword', None),
                             ('ilo_result_key', None), ('ilo_component_name_xpath', None), ('ilo_query', None),
                             ('ilo_status_values', None), ('ilo_status_monitor', True),
                             ('attributeName', None), ('resource', None), ('timeout', None), ('ports', None),
                             ('webTxTimeout', None), ('statusname', None), ('group_key', None), ('operation', None),
                             ('port', None),  ('authenticate', None), ('rollup', None), ('critical', None),
                             ('result_component_value', None), ('useBasisInterval', True), ('host', None),
                             ('expression', None), ('entity_id', None), ('useSSL', True), ('class_name', None),
                             ('classname', None), ('strategy', None), ('result_component_key', None),
                             ('username', None), ('objectName', None), ('queryset', None), ('counter_key', None),
                             ('xpath_query', None), ('timeout_delay', 60), ('warning', None), ('property_name', None),
                             ('initialPassword', None), ('result_value_key', None), ('hostname', None),
                             ('namespace', None), ('usePowershell', True), ('instance', None),
                             ('expectedIpAddress', None), ('initialUser', None), ('chunk_size', None),
                             ('initialURL', None), ('counter', None), ('dbtype', None), ('command', None),
                             ('attempts', 2)])

    '''
    [
    ('xpath', None), ('isrow', None), ('leaf', None), ('xpath_query', None), ('handler', None), 
    ('availableRRDTypes', None), ('name', None), ('rpn', None), ('rate', None), ('meta_type', None), 
    ('newId', None), ('createCmd', None), ('inspector_type', None), ('aliases', None), 
    ('type', None), 
    ]
    '''

    dp_fields = OrderedDict([('description', ''), ('rrdtype', ''), ('rrdmin', None), ('rrdmax', None),
                             ('xpath', None), ('isrow', True), ('leaf', True), ('xpath_query', None), ('handler', None),
                             ('rpn', None), ('rate', True), ('createCmd', None),
                             ])

    yaml_print(key='datasources', indent=indent)
    ds_data = sorted(ds_data, key=lambda i: i['name'])
    dp_data = sorted(dp_data, key=lambda i: i['name'])
    for ds in ds_data:
        ds_keys = ds.keys()
        ds_keys.remove('name')
        yaml_print(key=ds['name'], indent=indent + 2)
        for k, default in ds_fields.items():
            v = ds.get(k, None)
            if k in ds_keys:
                ds_keys.remove(k)
            if v and v != default:
                yaml_print(key=k, value=v, indent=indent + 4)
        v = ds.get('source', None)
        if v and v != ds.get('plugin_classname', None):
            yaml_print(key=k, value=v, indent=indent + 4)
        ds_all_fields.update(ds_keys)

        # Datapoints
        ds_uid = ds['uid']
        ds_dp_data = [d for d in dp_data if d['uid'].startswith('{}/datapoints/'.format(ds_uid))]
        if ds_dp_data:
            yaml_print(key='datapoints', indent=indent + 4)
        for dp in ds_dp_data:
            dp_keys = dp.keys()
            dp_keys.remove('name')
            dp_name = dp['name'][len(ds['name'])+1:]
            yaml_print(key=dp_name, indent=indent + 6)
            for k, default in dp_fields.items():
                v = dp.get(k, None)
                if k in dp_keys:
                    dp_keys.remove(k)
                if v and v != default:
                    yaml_print(key=k, value=v, indent=indent + 8)

            dp_keys.remove('aliases')
            dp_aliases = dp.get('aliases', [])
            aliases_text = []
            for alias in dp_aliases:
                alias_formula = alias.get('formula', 'null')
                if not alias_formula:
                    alias_formula = 'null'
                aliases_text.append("{}: '{}'".format(alias['name'], alias_formula))
            if aliases_text:
                value = '{{{}}}'.format(', '.join(aliases_text)).encode('ascii')
                yaml_print(key='aliases', value=value, indent=indent + 8)
            dp_all_fields.update(dp_keys)


def print_thresholds(routers, uid, indent):
    template_router = routers['Template']
    response = template_router.callMethod('getThresholds', uid=uid)
    th_data = response['result']['data']

    if not th_data:
        return

    '''
    [
    ('uid', None), ('escalateCount', None), ('newId', None), ('timePeriod', None), 
    ('total_expression', None), ('id', None), ('eventClassKey', None), 
    ('explanation', None), ('capacity_type', None), ('description', None), 
    ('dsnames', None), ('used_expression', None), ('violationPercentage', None), 
    ('meta_type', None), ('dataPoints', None), ('inspector_type', None), 
    ('pct_threshold', None), ('resolution', None)
    ]
    '''

    th_fields = OrderedDict([('type', 'MinMaxThreshold'), ('enabled', True), ('eventClass', None),
                             ('eventClassKey', None),
                             ('severity', 3), ('optional', False), ('minval', None), ('maxval', None),
                             ('escalateCount', None), ('timePeriod', None), ('violationPercentage', None),
                             ('pct_threshold', None), ('total_expression', None), ('used_expression', None),
                             ('capacity_type', None), ('resolution', None),
                             ])

    th_data = sorted(th_data, key=lambda i: i['name'])
    yaml_print(key='thresholds', indent=indent)
    for threshold in th_data:
        th_keys = threshold.keys()
        th_keys.remove('name')
        yaml_print(key=threshold['name'], indent=indent + 2)
        for k, default in th_fields.items():
            v = threshold.get(k, '')
            if k in th_keys:
                th_keys.remove(k)
            if v and v !=  default:
                yaml_print(key=k, value=v, indent=indent + 4)
        if 'dsnames' in th_keys:
            th_keys.remove('dsnames')
        dsnames = threshold.get('dsnames', [])
        if dsnames:
            v = '[{}]'.format(', '.join(dsnames))
            yaml_print(key='dsnames', value=v, indent=indent + 4)
        th_all_fields.update(th_keys)


def print_graphs(routers, uid, indent):
    template_router = routers['Template']
    response = template_router.callMethod('getGraphs', uid=uid)
    result = response['result']
    if not result:
        return

    '''
    All graph fields
    [
    ]
    '''

    gr_fields = OrderedDict([('type', ''), ('units', ''), ('miny', -1), ('maxy', -1), ('log', False),
                             ('base', False), ('hasSummary', True), ('height', 500), ('width', 500),
                             ('comments', []), ('sequence', None), ('ceiling', None), ('description', None),
                             ])

    '''
    All graphpoint fields
    [
    ('type', None), ('skipCalc', None), 
    ('meta_type', None), ('rrdVariables', None), ('inspector_type', None), 
    ]
    '''

    gp_fields = OrderedDict([('description', 'DataPointGraphPoint'), ('legend', ''), ('dpName', ''),
                             ('lineType', 'LINE'), ('lineWidth', 1), ('stacked', False), ('color', ''),
                             ('colorindex', None), ('format', '%5.2lf%s'), ('cFunc', 'AVERAGE'),
                             ('limit', -1), ('rpn', ''), ('includeThresholds', False), ('thresholdLegends', {}),
                             ('threshId', None), ('text', '')])

    yaml_print(key='graphs', indent=indent)
    gr_data = sorted(result, key=lambda i: i['name'])
    # dp_data = sorted(dp_data, key=lambda i: i['name'])
    for graph in gr_data:
        yaml_print(key=graph['name'], indent=indent + 2)
        for k, default in gr_fields.items():
            v = graph.get(k, None)
            if v and v != default:
                yaml_print(key=k, value=v, indent=indent + 4)
        gr_all_fields.update(graph.keys())

        # Graphpoints
        graph_uid = graph['uid']
        response = template_router.callMethod('getGraphPoints', uid=graph_uid)
        gp_data = sorted(response['result']['data'], key=lambda i: i['name'])

        if gp_data:
            yaml_print(key='graphpoints', indent=indent + 4)
        for graphpoint in gp_data:
            yaml_print(key=graphpoint['name'], indent=indent + 6)
            for k, default in gp_fields.items():
                v = graphpoint.get(k, None)
                if v and v != default:
                    yaml_print(key=k, value=v, indent=indent + 8)
            gp_all_fields.update(graphpoint.keys())


def print_template(routers, uid, parent_uid, indent):
    template_router = routers['Template']
    response = template_router.callMethod('getInfo', uid=uid)
    data = response['result']['data']

    fields = ['description', 'targetPythonClass']
    yaml_print(key=data['name'], indent=indent)
    if parent_uid:
        yaml_print(key='# Parent: {}'.format(parent_uid), indent=indent)
    for k in fields:
        v = data[k]
        if v:
            yaml_print(key=k, value=v, indent=indent + 2)

    print_datasources(routers, uid, indent + 2)
    print_thresholds(routers, uid, indent + 2)
    print_graphs(routers, uid, indent + 2)

def parse_templates(routers):
    template_router = routers['Template']
    templates_name_set = set()
    templates_uid_set = set()

    # Generate full set of template uids, down to local component templates
    response = template_router.callMethod('getTemplates', id='/zport/dmd/Devices')
    result = response['result']
    for t in result:
        if t['name'] in templates_name_set:
            continue
        templates_name_set.add(t['name'])
        t_response = template_router.callMethod('getTemplates', id=t['uid'])
        t_result = t_response['result']
        for r in t_result:
            templates_uid_set.add(r['uid'])
    templates_uid = sorted(list(templates_uid_set))


    # Loop through templates
    while templates_uid:
        # POP ?
        uid = templates_uid[0]

        '''
        if uid < '/zport/dmd/Devices/Server/HP/ILO':
            templates_uid.remove(uid)
            continue
        '''
        # print(uid)
        if '/rrdTemplates/' in uid:
            r = re.match('((\/zport\/dmd\/Devices)(.*))(\/rrdTemplates\/)(.*)', uid)
            if not r:
                print('No regex match for {}'.format(uid))
                exit()
            # Retrieve all templates for same device class
            dc_path = '{}{}'.format(r.group(1), r.group(4))
            dc_name = r.group(3)
            if not dc_name:
                dc_name = "/"
            # dc_template_name = r.group(5)
            yaml_print(key=dc_name, indent=2)
            yaml_print(key='templates', indent=4)

            dc_r = re.compile(dc_path)
            dc_templates = filter(dc_r.match, templates_uid)

            # Loop through each template and dump yaml info
            for t_uid in dc_templates:
                parent_uid = get_parent_template(routers, t_uid)
                print_template(routers, t_uid, parent_uid, indent=6)
                templates_uid.remove(t_uid)
        elif '/devices/' in uid:
            if uid.startswith('/zport/dmd/Devices/ControlCenter/'):
                templates_uid.remove(uid)
                continue

            dc_name = uid[18:]
            yaml_print(key=dc_name, indent=2)
            yaml_print(key='templates', indent=4)
            parent_uid = get_parent_template(routers, uid)
            print_template(routers, uid, parent_uid, indent=6)
            templates_devices.append(uid)
            templates_uid.remove(uid)
        else:
            print('No analysis for {}'.format(uid))
            templates_uid.remove(uid)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List templates definition')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    options = parser.parse_args()
    environ = options.environ

    template_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='TemplateRouter')
    properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')

    routers = {
        'Template': template_router,
        'Properties': properties_router,
    }

    yaml_print(key='device_classes', indent=0)
    parse_templates(routers)

    print
    print('Datasource fields')
    print(ds_all_fields)
    print('Datapoint fields')
    print(dp_all_fields)
    print('Threshold fields')
    print(th_all_fields)
    print('Graph fields')
    print(gr_all_fields)
    print('Graphpoint fields')
    print(gp_all_fields)

    print(templates_devices)



import zenAPI.zenApiLib
import argparse
import yaml
from tqdm import tqdm


def get_properties(routers, uid):
    properties_router = routers['Properties']
    response = properties_router.callMethod('getZenProperties', uid=uid)
    properties = response['result']['data']
    properties = sorted(properties, key=lambda i: i['id'])
    prop_data = {}
    for property in properties:
        if property['islocal'] == 1:
            if 'zProperties' not in prop_data:
                prop_data['zProperties'] = {}
            prop_data['zProperties'][property['id']] = property['value']
    return prop_data


def get_servicezprop(service):
    zprop_keys = sorted([k for k in service if k.startswith('z')])
    prop_data = {}
    for k in zprop_keys:
        prop = service[k]
        if not prop['isAcquired']:
            if 'zProperties' not in prop_data:
                prop_data['zProperties'] = {}
            prop_data['zProperties'][k] = prop['localValue']
    return prop_data


def get_serviceinstances(routers, uid):
    service_router = routers['Service']
    response = service_router.callMethod('query', uid=uid, sort='name', dir='ASC')
    service_list = response['result']['services']
    service_list = filter(lambda x: x['uid'].startswith('{}/serviceclasses/'.format(uid)), service_list)
    fields = ['port', 'serviceKeys', 'sendString', 'expectRegex', 'monitoredStartModes']

    service_json = {}
    for service in tqdm(service_list, desc='    Services'):
        if 'service_class' not in service_json:
            service_json['service_class'] = {}
        service_name = service['name']
        service_json['service_class'][service_name] = {}
        p_desc = service.get('description', '')
        if p_desc:
            service_json['service_class'][service_name]['description'] = p_desc
        response = service_router.callMethod('getInfo', uid=service['uid'])
        service_info = response['result']['data']
        service_props = get_servicezprop(service_info)
        service_json['service_class'][service_name].update(service_props)
        for k in fields:
            v = service_info.get(k, '')
            if v:
                service_json['service_class'][service_name][k] = v
    return service_json


def list_organizers(routers, uids=[]):
    service_router = routers['Service']
    organizers_uids = []
    if not uids:
        service_tree = service_router.callMethod('getOrganizerTree', id='/zport/dmd/Services')
        uids = service_tree['result']

    for branch in sorted(uids, key=lambda i: i['uid']):
        branch_uid = branch['uid']
        organizers_uids.append(branch_uid)
        branch_children = sorted(branch.get('children', []))
        if branch_children:
            children = list_organizers(routers, branch_children)
            organizers_uids.extend(children)
    return organizers_uids


def parse_servicetree(routers, output):
    service_router = routers['Service']

    default_organizers = ['/zport/dmd/Services', '/zport/dmd/Services/IpService/Privileged',
                          '/zport/dmd/Services/IpService/Registered', '/zport/dmd/Services/WinService']

    print('Retrieving all organizers')
    org_list = list_organizers(routers)

    for org in default_organizers:
        if org not in org_list:
            org_list.append(org)
        org_list.sort()
    print('Retrieved {} organizers'.format(len(org_list)))

    service_json = {'service_organizers': {}}
    for organizer_uid in tqdm(org_list, desc='Organizers'):
        response = service_router.callMethod('getOrganizerTree', id=organizer_uid)
        organizer = response['result'][0]

        organizer_path = '/' + organizer['path']
        service_json['service_organizers'][organizer_path] = {}
        # Properties
        organizer_props = get_properties(routers, organizer_uid)
        service_json['service_organizers'][organizer_path].update(organizer_props)
        # Instances
        organizer_services = get_serviceinstances(routers, organizer_uid)
        service_json['service_organizers'][organizer_path].update(organizer_services)
    yaml.safe_dump(service_json, file(output, 'w'), encoding='utf-8', allow_unicode=True, sort_keys=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List services definition')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    parser.add_argument('-f', dest='output', action='store', default='services_output.yaml')
    options = parser.parse_args()
    environ = options.environ
    output = options.output

    service_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='ServiceRouter')
    properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')

    routers = {
        'Service': service_router,
        'Properties': properties_router,
    }

    print('Connecting to Zenoss')
    parse_servicetree(routers, output)

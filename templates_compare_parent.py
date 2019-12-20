import zenAPI.zenApiLib
import argparse
import re

from templates_tools import get_parent_template, compare_templates

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare template with parent')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    parser.add_argument('-d', dest='devclass', action='store', default='Devices/Server/SSH/Linux', help='Device Class')
    parser.add_argument('-n', dest='tname', action='store', default='Device', help='Template name')
    options = parser.parse_args()
    environ = options.environ
    devclass = options.devclass
    template_name = options.tname

    print('Connecting to Zenoss')
    template_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='TemplateRouter')
    print('Validating arguments')
    template_uid = '/zport/dmd/{}/rrdTemplates/{}'.format(devclass, template_name)
    result = template_router.callMethod('getInfo', uid=template_uid)['result']
    if not result['success']:
        print('Template UID is not valid: {}'.format(template_uid))
        exit()
    print('Template UID: {}'.format(template_uid))
    print('Searching for parent')
    parent_uid = get_parent_template(template_router, template_uid)
    if not parent_uid:
        print('Parent not found.')
    print('Parent UID  : {}'.format(parent_uid))
    print('Comparing')
    compare_templates(template_router, [template_uid])

    '''
    print('Found {} backup templates'.format(len(backup_templates)))
    for t in backup_templates:
        inspect_template(template_router, t)
    '''


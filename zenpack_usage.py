# from templates_tools import list_zenpacks_templates
import zenAPI.zenApiLib
import argparse

def list_zenpacks_templates(zenpack_router, template_router):
    result = zenpack_router.callMethod('getZenPackMetaData')['result']
    # result = zenpack_router.callMethod('zenPackList')['result']
    '''
    {
    u'count': 80,
    u'data': {
        u'ZenPacks.zenoss.MySqlMonitor': {
          u'compatZenossVers': u'>=4.1',
          u'ZenPackName': u'MySqlMonitor',
          u'description': u'',
          u'license': u'GPLv2',
          u'author': u'Zenoss',
          u'url': u'',
          u'isEggPack': True,
          u'isBroken': False,
          u'namespace': u'zenoss',
          u'isDevelopment': False,
          u'meta_type': u'ZenModelRM',
          u'version': u'3.1.0',
          u'path': u'/opt/zenoss/ZenPacks/ZenPacks.zenoss.MySqlMonitor-3.1.0-py2.7.egg/ZenPacks/zenoss/MySqlMonitor',
          u'inspector_type': u'ZenModelRM',
          u'organization': u'',
          u'uid': u'/zport/dmd/ZenPackManager/packs/ZenPacks.zenoss.MySqlMonitor',
          u'id': u'ZenPacks.zenoss.MySqlMonitor',
          u'name': u'ZenPacks.zenoss.MySqlMonitor'
        },
    '''

    t_uid = '/zport/dmd/Devices/Network/Cisco/ACE/rrdTemplates/ACEContext'
    # response = template_router.callMethod('getInfo', uid=t_uid)
    response = template_router.callMethod('getCollectorTemplate', id=t_uid)
    print(response)


    for zp, zp_value in result['data'].items():
        print(zp_value)
        zp_uid = zp_value['uid']
        print(zp_uid)
        uid = '{}/packables'.format(zp_uid)
        print(uid)
        # zp_info = template_router.callMethod('getInfo', uid=uid)
        # zp_info = zenpack_router.callMethod('getInfo', uid=uid)
        # zp_info = template_router.callMethod('getCollectorTemplate', id=uid)
        # zp_info = zenpack_router.callMethod('getZenPackMetaData', zenpacks=uid)
        print(zp_info)
        exit()
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List Zenpacks')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    options = parser.parse_args()
    environ = options.environ

    template_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='TemplateRouter')
    zenpack_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='ZenPackRouter')


    properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')
    response = properties_router.callMethod('getInfo', uid='/zport/dmd/ZenPackManager/packs/ZenPacks.zenoss.MySqlMonitor')
    print(response)
    exit()



    list_zenpacks_templates(zenpack_router, template_router)
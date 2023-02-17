import zenAPI.zenApiLib
import argparse
from tools import yaml_print
import yaml
import os

# TODO: Add logging
# TODO: Add progress bars

def parse_notificationlist(routers, list):
    list = sorted(list, key=lambda i: i['name'])

    fields = ['enabled', 'send_clear', 'send_initial_occurrence', 'delay_seconds', 'repeat_seconds']

    content_fields = ['body_content_type', 'subject_format', 'action_timeout', 'body_format',
                      'clear_subject_format', 'clear_body_format', 'user_env_format'
                      'skipfails', 'email_from', 'host', 'port', 'useTls', 'user', 'password']

    for notification in list:
        yaml_print(key=notification['name'], indent=2)

        for k in fields:
            v = notification.get(k, '')
            if v:
                yaml_print(key=k, value=v, indent=4)
        notification_subs = notification.get('subscriptions', [])
        if notification_subs:
            trigger_list = [t['name'] for t in notification_subs]
            yaml_print(key='triggers', value=trigger_list, indent=4)
        notification_content = notification.get('content', {})
        print(notification_content)
        if notification_content:
            items = notification_content['items'][0]['items']
            for k in content_fields:
                for item in items:
                    if item['name'] == k:
                        items.remove(item)
                        break
                else:
                    item = None
                if item:
                    value = item.get('value', None)
                    if value:
                        yaml_print(key=item['name'], value=value, indent=4)
        notification_recipients = notification.get('recipients', [])
        if notification_recipients:
            recipient_list = [r['label'] for r in notification_recipients]
            yaml_print(key='recipients', value=recipient_list, indent=4)


def notif_save(routers, filename):
    print('Saving current notifications setup.')
    trigger_router = routers['Triggers']
    response = trigger_router.callMethod('getNotifications')
    output = {}
    for notification in response['result']['data']:
        # print(notification['name'])
        output[notification['name']] = {'enabled': notification['enabled']}
    yaml.safe_dump(output, file(filename, 'w'), encoding='utf-8', allow_unicode=True, sort_keys=True)

def notif_restore(routers, filename):
    print('Restoring current notifications setup.')
    trigger_router = routers['Triggers']
    response = trigger_router.callMethod('getNotifications')

    config_data = yaml.safe_load(file(filename, 'r'))  # dict
    # print(config_data)
    # print(type(config_data))

    for notification in response['result']['data']:
        # print(notification['name'])
        notif_name = notification['name']
        current_value = notification['enabled']
        if notif_name not in config_data:
            continue
        config_value = config_data[notif_name]['enabled']
        if current_value != config_value:
            new_notif = notif_copy(notification)
            new_notif['enabled'] = config_value
            response = trigger_router.callMethod('updateNotification', **new_notif)
    print('Restored notifications setup.')

def notif_enable(routers, filename, switch):
    print('Checking current notifications')
    trigger_router = routers['Triggers']
    response = trigger_router.callMethod('getNotifications')
    notif_names = [n['name']  for n in response['result']['data']]

    config_data = yaml.safe_load(file(filename, 'r'))  # dict
    if not all(name in config_data for name in notif_names):
        # TODO: Should update only the unknown notif, the following could reset all values
        # notif_save(routers, filename)
        config_data = yaml.safe_load(file(filename, 'r'))  # dict

    print('Switching notifications')
    for notif in response['result']['data']:
        current_value = notif['enabled']
        if switch != current_value:
            new_notif = notif_copy(notif)
            new_notif['enabled'] = switch
            response = trigger_router.callMethod('updateNotification', **new_notif)
    print('Switched all notifications')

def notif_copy(data):
    fields = ['body_content_type', 'body_format', 'clear_body_format', 'clear_subject_format', 'delay_seconds',
              'email_from', 'enabled', 'host', 'notification_globalManage', 'notification_globalRead',
              'notification_globalWrite', 'password', 'port',  'recipients', 'repeat_seconds', 'send_clear',
              'send_initial_occurrence', 'skipfails', 'subject_format', 'subscriptions', 'uid', 'useTls', 'user',
              ]
    output = {k: data[k] for k in fields if k in data}
    if 'subscriptions' in output:
        new_val = [s['uuid'] for s in output['subscriptions']]
        subs = output['subscriptions']
        output['subscriptions'] = new_val
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage Triggers')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    parser.add_argument('--on', dest='on', action='store_true')
    parser.add_argument('--off', dest='off', action='store_true')
    parser.add_argument('--save', dest='save', action='store_true')
    parser.add_argument('--restore', dest='restore', action='store_true')
    options = parser.parse_args()
    environ = options.environ
    action_on  = options.on
    action_off = options.off
    action_save = options.save
    action_restore = options.restore

    # Routers
    trigger_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='TriggersRouter')
    properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')

    routers = {
        'Triggers': trigger_router,
        'Properties': properties_router,
    }

    config_file = 'notif_{}.yaml'.format(environ)
    if options.save:
        notif_save(routers, config_file)
    elif options.restore:
        notif_restore(routers, config_file)
    elif options.on:
        pass
    elif options.off:
        # Save current config
        notif_save(routers, config_file)
        # Disable all notifs
        notif_enable(routers, config_file, False)

    print('Job done.')

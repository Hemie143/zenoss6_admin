import zenAPI.zenApiLib
import argparse
from tools import yaml_print


def parse_triggerlist(routers, list):
    list = sorted(list, key=lambda i: i['name'])
    for trigger in list:
        yaml_print(key=trigger['name'], indent=2)
        fields = ['enabled']
        for k in fields:
            v = trigger.get(k, '')
            if v:
                yaml_print(key=k, value=v, indent=4)
        trigger_rule = trigger.get('rule', {})
        if trigger_rule:
            yaml_print(key='rule', indent=4)
            yaml_print(key='source', value=trigger_rule['source'], indent=6)
            yaml_print(key='type', value=trigger_rule['type'], indent=6)


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



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage Triggers')
    parser.add_argument('-s', dest='environ', action='store', default='z6_test')
    options = parser.parse_args()
    environ = options.environ

    # Routers
    trigger_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='TriggersRouter')
    properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')

    routers = {
        'Triggers': trigger_router,
        'Properties': properties_router,
    }

    # "getTriggers": {}
    # "getRecipientOptions": {}
    # "updateTrigger": {uuid: "c42ca88b-d5d9-4253-b875-6c35aae53915", enabled: true, name: "ActiveMQ_Delivery", }
    # "getNotifications": {}
    # "getWindows": {uid: "/zport/dmd/NotificationSubscriptions/ActiveMQ_Delivery"}
    # "getTriggerList": {}
    # "getRecipientOptions": {}
    # "updateNotification": [{uid: "/zport/dmd/NotificationSubscriptions/ActiveMQ_Delivery", enabled: true, send_clear: true,}]

    response = trigger_router.callMethod('getTriggers')
    data = response['result']['data']
    yaml_print(key='triggers', indent=0)
    # parse_triggerlist(routers, data)

    response = trigger_router.callMethod('getNotifications')
    data = response['result']['data']
    yaml_print(key='notifications', indent=0)
    parse_notificationlist(routers, data)

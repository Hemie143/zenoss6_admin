import zenAPI.zenApiLib
import argparse
import logging
import csv
from tqdm import tqdm


def parse_notificationlist(routers, output, progress_disable):
    trigger_router = routers['Triggers']
    response = trigger_router.callMethod('getNotifications')
    notifications = response['result']['data']
    notifications = sorted(notifications, key=lambda i: i['name'])

    data = {}
    for notification in tqdm(notifications, desc='Notifications', ascii=True, disable=progress_disable):
        notification_name = notification['name']
        notification_subs = notification.get('subscriptions', [])
        if notification_subs:
            trigger_list = [t['name'] for t in notification_subs]
        else:
            print("No trigger for {}".format(notification_name))

        notification_recipients = notification.get('recipients', [])
        if notification_recipients:
            recipient_list = [r['label'] for r in notification_recipients]
            for r in recipient_list:
                if r in data:
                    if notification_name in data[r]:
                        data[r][notification_name].append(trigger_list)
                    else:
                        data[r][notification_name] = trigger_list
                else:
                    data[r] = {notification_name: trigger_list}
        else:
            print("No recipient for {}".format(notification_name))

    with open(output, "wb") as csvfile:
        notifwriter = csv.writer(csvfile)
        for recipient, r_data in data.items():
            for notif, triggers in r_data.items():
                for trigger in triggers:
                    notifwriter.writerow([recipient, notif, trigger])

def export(environ, output, progress_disable=False, device_class='', template_name=''):
    # Routers
    try:
        trigger_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='TriggersRouter')
        properties_router = zenAPI.zenApiLib.zenConnector(section=environ, routerName='PropertiesRouter')
    except Exception as e:
        logging.error('Could not connect to Zenoss: {}'.format(e.args))
        exit(1)

    routers = {
        'Triggers': trigger_router,
        'Properties': properties_router,
    }

    # parse_triggerlist(routers, output, progress_disable)
    parse_notificationlist(routers, output, progress_disable)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage Triggers')
    parser.add_argument('-s', dest='environ', action='store', default='zcloud')
    parser.add_argument('-f', dest='output', action='store', default='notifs_report.csv')
    options = parser.parse_args()
    environ = options.environ
    output = options.output

    export(environ, output)

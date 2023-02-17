import requests
import urllib
import urllib2

base_url = 'http://10.4.93.11/index.php/jsonrpc/sms'
data = {
    'method': 'sms.send_sms',
    'params': {
        'login': 'appd',
        'pass': '83xUagW4EsWpggJQ',
        'to': '32473808709',
        'message': 'python test post'
    }
}

headers = {
    'Content-Type': 'application/json'
}

r = requests.post(url=base_url, json=data, headers=headers)
print(r.text)


# curl -H "Content-Type: application/json" -X POST -d '{"method":"sms.send_sms", "params":{"login":"appd","pass":"83xUagW4EsWpggJQ","to":"+32473808709","message":"curl test post"}}' https://10.4.93.11/index.php/jsonrpc/sms

import urllib
import urllib2

base_url = 'http://10.4.93.11/index.php/http_api/send_sms'
query_args = { 'login':'appd', 'pass':'83xUagW4EsWpggJQ', 'to':'32473808709', 'message':'python test get' }
encoded_args = urllib.urlencode(query_args)
url = base_url + '?' + encoded_args
result = urllib2.urlopen(url).read()
print(result)
import json

data = '''
{
"dc3-probe-s01.fednot.be": 
    {
        "compname": "",
        "relname": "raritanHumiditySensors", 
        "modname": "ZenPacks.community.Raritan.RaritanHumiditySensor",
        "objects": [{"id": "Relative Humidity 1"}]
    }
}'''




myjson = json.loads(data)
print(myjson)
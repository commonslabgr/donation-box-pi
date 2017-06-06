import urllib2, json

url = "http://thecoopbox.commonslab.gr/network_output.php?idproject=1"
response = urllib2.urlopen(url)
data = json.loads(response.read())
print data[0]['amount']

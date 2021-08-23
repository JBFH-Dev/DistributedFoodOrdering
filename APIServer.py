import urllib
import urllib.request
from uuid import uuid4
import Pyro4
import json

@Pyro4.expose
class APIServer(object):
    def __init__(self):
        self.api = 'https://api.postcodes.io/postcodes/'
    
    def get_location(self, address):
        postcode = address[1].replace(" ", "")
        url = self.api+postcode
        try:
            resp = urllib.request.urlopen(url)
        except urllib.error.HTTPError:
            print("Address was found invalid by API")
            raise Exception("InvalidAddress")
        except urllib.error.URLError:
            print("API offline")
            raise Exception("ExternalAPIDown")
        decoded_response = resp.read().decode('utf-8')
        d = json.loads(decoded_response)
        if not d['status'] == 200:
            print("Address was found invalid by API")
            raise Exception("InvalidAddress")
        parish = d['result']['parish']
        admin = d['result']['admin_district']
        output = (parish, admin)
        return output

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
a = APIServer()
uri = daemon.register(a)
ns.register("APIServer", uri)
print("APIServer ready")
daemon.requestLoop()
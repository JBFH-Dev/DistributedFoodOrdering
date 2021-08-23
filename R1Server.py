#Imports necessary packages
import Pyro4
import re
import json
import urllib
import urllib.request
from uuid import uuid4

#exposes class for hosting on pyro
@Pyro4.expose
class Replica1(object):
    def __init__(self, sid):
        #Stores local variables
        self.sid = sid
        self.ns = Pyro4.locateNS()
        self.orders = dict()
        self.state = dict()
        self.custs = dict()
        self.menu = ["Chicken Chow Mein", "Meat Feast Pizza", "Lamb Rogan Josh", "Fish and Chips", "Thai Green Curry"]
        self.inuse = []

    def external_add(self, id_num, address):
        #Externally verifies address and gets extra information from api
        #Checks state for previously sent response
        found = self.state_check(id_num)
        if not found == False:
            return found
        apis = [i for i in self.ns.list() if i == "APIServer"]
        if apis == []:
            print("API Server down, continuing without external validation")
            self.state[id_num] = ("Unavailable","Unavailable")
            return ("Unavailable","Unavailable")
        with Pyro4.Proxy("PYRONAME:"+apis[0]) as target:
            try:
                output = target.get_location(address)
            except Exception as e:
                if str(e) == "InvalidAddress":
                    print("Address was found invalid by API")
                    raise Exception("InvalidAddress")
                self.ns.remove(name = apis[0])
                print("API Server down, continuing without external validation")
                output = ("Unavailable","Unavailable")
        self.state[id_num] = output
        return output

        #Checks that the given address suits the regex function for postcode
    def check_validity(self, id_num, address):
        found = self.state_check(id_num)
        if not found == False:
            return found
        #Compares postcode to regular expression for postcode
        valid = bool(re.match(r"([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})", address[1]))
        if not valid:
            self.state[id_num] = 404
            raise Exception("InvalidAddress")
        self.state[id_num] = 1
        return 1

    def logout(self, id_num, userID):
        found = self.state_check(id_num)
        self.state[id_num] = 1
        if not found == False:
            return found
        if userID in self.inuse:
            self.inuse.remove(userID)
            return 1
        return 1

    def find_cust(self, id_num, userID):
        found = self.state_check(id_num)
        if not found == False:
            return found
        if userID in self.inuse:
            print("User ID already in use by another client")
            self.state[id_num] = 501
            raise Exception("UserLoggedIn")
        if userID in self.custs:
            self.state[id_num] = self.custs[userID]
            self.inuse.append(userID)
            return self.custs[userID]
        raise Exception("CustomerNotFound")
        
    def view_orders(self, id_num, userID):
        found = self.state_check(id_num)
        if not found == False:
            return found
        if userID in self.orders:
            self.state[id_num] = self.orders[userID]
            return self.orders[userID]
        raise Exception("OrderNotFound")

    def get_menu(self, id_num):
        found = self.state_check(id_num)
        if not found == False:
            return found
        self.state[id_num] = self.menu
        return self.menu

    def place_order(self, id_num, order, userID):
        found = self.state_check(id_num)
        if not found == False:
            return found
        #Register order to userID
        self.orders[userID] = order
        self.state[id_num] = 1
        replicas = []
        #sends updated state and orders to replica backend servers
        for name in self.ns.list():
            if 'R' in name and not name == self.sid:
                replicas.append(name)
        for replica in replicas:
            with Pyro4.Proxy("PYRONAME:"+replica) as target:
                try:
                    resp = target.send_update(id_num, self.orders, self.custs, 1)
                    print("Sent update")
                except Exception as e:
                    self.ns.remove(name = replica)
        if replicas == []:
            print("Could not update replicas, try again later")
        return 1

    def new_cust(self, id_num, userID, location):
        found = self.state_check(id_num)
        if not found == False:
            return found
        #Adds new customer to dictionary
        self.inuse.append(userID)
        self.custs[userID] = location
        self.state[id_num] = 1
        replicas = []
        #Updates replica backend servers
        for name in self.ns.list():
            if 'R' in name and not name == self.sid:
                replicas.append(name)
        for replica in replicas:
            with Pyro4.Proxy("PYRONAME:"+replica) as target:
                try:
                    resp = target.send_update(id_num, self.orders, self.custs, 1)
                    print("Sent update")
                except Exception as e:
                    self.ns.remove(name = replica)
        if replicas == []:
            print("Could not update replicas, try again later")
        return 1

    #Function to send updates to replicas
    def send_update(self, id_num, data, users, response):
        print(self.sid, " has been updated")
        self.state[id_num] = response
        self.orders = data
        self.custs = users
        return 1

    def state_check(self, id_num):
        #Checks that function has not been previously handled
        found = self.state.get(id_num)
        if found == None:
            return False
        if found == 404:
            raise Exception("InvalidAddress")
        if found == 406:
            raise Exception("AllServersDown")
        if found == 407:
            raise Exception("MenuNotFound")
        if found == 408:
            raise Exception("OrderNotPlaced")
        if found == 501:
            raise Exception("UserLoggedIn")
        return found

#Register class on the network server
daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
#Generates unique id for each server
name = str(uuid4())
sid = "R"+name+"Server"
while sid in ns.list():
    name = str(uuid4())
    sid = "R"+name+"Server"
#Host object on pyro4
r = Replica1(sid)
uri = daemon.register(r)
ns.register(sid, uri)
print("ready, name is: ",sid)
daemon.requestLoop()
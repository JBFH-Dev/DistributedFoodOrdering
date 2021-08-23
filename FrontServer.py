import Pyro4
#Exposes class to naming server
@Pyro4.expose
class Frontend(object):
    count = 0
    #name server to be used to connect to the backend servers
    ns = Pyro4.locateNS()
    #Validates and retreives address information
    def get_address(self, address):
        #generates unique id of function call
        id_num = hash("GET" + address[0] + address[1]+str(self.count))
        self.count += 1
        replicas = []
        #Lists active backend replicas
        for name in self.ns.list():
            if 'R' in name:
                replicas.append(name)
        #Attempts to call primary and if the request fails that replica is removed from the list
        for replica in replicas:
            with Pyro4.Proxy("PYRONAME:"+replica) as target:
                try:
                    resp = target.check_validity(id_num, address)
                    break
                except Exception as e:
                    if str(e) == "InvalidAddress":
                        print("Address was invalid")
                        raise Exception("InvalidAddress")
                    self.ns.remove(name = replica)
        #If every replica was inactive then exit gracefully
        if replicas == []:
            print("All servers currently down, try again later")
            raise Exception("AllServersDown")
        #hashes arguments to create unique function id
        id_num = hash("VALIDATE" + address[0] + address[1]+str(self.count))
        self.count+=1
        replicas = []
        #lists all active replicas
        for name in self.ns.list():
            if 'R' in name:
                replicas.append(name)
        #requests each replica until one succeeds or they all fail
        for replica in replicas:
            with Pyro4.Proxy("PYRONAME:"+replica) as target:
                try:
                    api_add = target.external_add(id_num, address)
                    return api_add
                except Exception as e:
                    if str(e) == "InvalidAddress":
                        print("Address was invalid")
                        raise Exception("InvalidAddress")
                    self.ns.remove(name = replica)
        #If every replica was inactive then exit gracefully
        if replicas == []:
            print("All servers currently down, try again later")
            raise Exception("AllServersDown")
    
    def get_menu(self):
        #Retreives menu from backend
        id_num = hash(self.count)
        self.count += 1
        replicas = []
        #lists available replicas
        for name in self.ns.list():
            if 'R' in name:
                replicas.append(name)
        #Requests each rpelica until one succeeds or they all fail
        for replica in replicas:
            with Pyro4.Proxy("PYRONAME:"+replica) as target:
                try:
                    menu = target.get_menu(id_num)
                    return menu
                except Exception as e:
                    if str(e) == "MenuNotFound":
                        print("Menu could not be retreived")
                        raise Exception("MenuNotFound")
                    self.ns.remove(name = replica)
        #If every replica was inactive then exit gracefully
        if replicas == []:
            print("All servers currently down, try again later")
            raise Exception("AllServersDown")

    def new_cust(self, userID, location):
        #Registers new customer to backend
        hashable = location[0] + location[-1] + userID + "NEW" + str(self.count)
        self.count += 1
        id_num = hash(hashable)
        replicas = []
        for name in self.ns.list():
            if 'R' in name:
                replicas.append(name)
        for replica in replicas:
            with Pyro4.Proxy("PYRONAME:"+replica) as target:
                try:
                    order_placed = target.new_cust(id_num, userID, location)
                    return 1
                except Exception as e:
                    if str(e) == "CustomerNotAdded":
                        print("Customer could not be added at this time")
                        raise Exception("CustomerNotAdded")
                    self.ns.remove(name = replica)
        if replicas == []:
            print("All servers currently down, try again later")
            raise Exception("AllServersDown")

    def find_cust(self, userID):
        #Retreives user information based on id
        id_num = hash(userID + "find"+ str(self.count))
        self.count += 1
        replicas = []
        for name in self.ns.list():
            if 'R' in name:
                replicas.append(name)
        for replica in replicas:
            with Pyro4.Proxy("PYRONAME:"+replica) as target:
                try:
                    location = target.find_cust(id_num, userID)
                    return location
                except Exception as e:
                    if str(e) == "CustomerNotFound":
                        print("Customer could not be found at this time")
                        raise Exception("CustomerNotFound")
                    if str(e) == "UserLoggedIn":
                        print("User ID already in use by another client")
                        raise Exception("UserLoggedIn")
                    self.ns.remove(name = replica)
        if replicas == []:
            print("All servers currently down, try again later")
            raise Exception("AllServersDown")

    def logout(self, userID):
        id_num = hash("logout"+userID+str(self.count))
        self.count += 1
        replicas = []
        for name in self.ns.list():
            if 'R' in name:
                replicas.append(name)
        for replica in replicas:
            with Pyro4.Proxy("PYRONAME:"+replica) as target:
                try:
                    target.logout(id_num, userID)
                    return 1
                except Exception as e:
                    self.ns.remove(name = replica)
        if replicas == []:
            print("All servers currently down, try again later")
            raise Exception("AllServersDown")


    def view_orders(self, userID):
        #Retreives orders for a user profile
        id_num = hash(userID + "orders"+str(self.count))
        self.count += 1
        replicas = []
        for name in self.ns.list():
            if 'R' in name:
                replicas.append(name)
        for replica in replicas:
            with Pyro4.Proxy("PYRONAME:"+replica) as target:
                try:
                    orders = target.view_orders(id_num, userID)
                    return orders
                except Exception as e:
                    if str(e) == "OrderNotFound":
                        print("Order could not be found at this time")
                        raise Exception("OrderNotFound")
                    self.ns.remove(name = replica)
        if replicas == []:
            print("All servers currently down, try again later")
            raise Exception("AllServersDown")

    def place_order(self, userID, order):
        #Places order to user profile on the backend
        hashable = ' '.join([str(elem) for elem in order]) + userID
        id_num = hash(hashable)
        replicas = []
        for name in self.ns.list():
            if 'R' in name:
                replicas.append(name)
        for replica in replicas:
            with Pyro4.Proxy("PYRONAME:"+replica) as target:
                try:
                    order_placed = target.place_order(id_num, order, userID)
                    return 1
                except Exception as e:
                    if str(e) == "OrderNotPlaced":
                        print("Order could not be placed at this time")
                        raise Exception("OrderNotPlaced")
                    self.ns.remove(name = replica)
        if replicas == []:
            print("All servers currently down, try again later")
            raise Exception("AllServersDown")

#registers instance of class and hosts it with unique id
daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(Frontend)
ns.register("FrontServer", uri)

print("ready")
daemon.requestLoop()
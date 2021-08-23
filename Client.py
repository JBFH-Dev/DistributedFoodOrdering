#Imports necessary packages
import Pyro4
from uuid import uuid4
import sys

#Gets and validates the parish and admin district from the frontend
def get_address(Front):
    confirm = "n"
    while not confirm == "y" or confirm == "Y":
        postcode = input("Enter your address to continue: ").strip()
        number = input("Now enter your house number: ").strip()
        print()
        try:
            address = Front.get_address((number, postcode))
        except Exception as e:
            #Parse varieties of error returned by frontend
            if str(e) == "InvalidAddress":
                print("Address was invalid")
                continue
            if str(e) == "AllServersDown":
                print("All servers currently down, try again later")
                sys.exit(406)
            print("Frontend server offline")
            sys.exit(111)
        print("Great! Is this your address?")
        print("-------  Number: \t",number)
        print("-------  Parish: \t",address[0])
        print("-------  District: \t",address[1])
        print("-------  Parish: \t",postcode)
        confirm = input("(y/n)").strip()
    print()
    location = number, address[0], address[1], postcode
    return location

def order_food(Front):
    print("Thanks! Now take a look at our menu:")
    print("----------------MENU------------------")
    #Retreives the menu items
    try:
        menu = Front.get_menu()
    except Exception as e:
        if str(e) == "MenuNotFound":
            print("Menu could not be retreived")
            sys.exit(407)
        if str(e) == "AllServersDown":
            print("All servers currently down, try again later")
            sys.exit(406)
        print("Frontend server offline")
        sys.exit(111)
    for i in range(len(menu)):
        print(i, " |\t", menu[i])
    choosing = True
    order = []
    #Asks the user for the food items they want to order
    print("Type the numbers of the items you want individually or 'done' to quit!")
    while choosing:
        item = input("-->").strip()
        if item == "done":
            choosing = False
        else:
            try:
                val = int(item)
            except ValueError:
                print("Not a valid integer")
                continue
            if val < 0 or val >= len(menu):
                print("Invalid menu item")
                continue
            order.append(item)
    return order

def place_order(Front, userID, order):
    #Sends order and userid to place order
    try:
        placed = Front.place_order(userID, order)
    except Exception as e:
        if str(e) == "OrderNotPlaced":
            print("Order could not be placed at this time")
            sys.exit(408)
        if str(e) == "AllServersDown":
            print("All servers currently down, try again later")
            sys.exit(406)
        print("Frontend server offline")
        sys.exit(111)
    print("-------------ORDER PLACED-------------")
    return 1

def options():
    #Prints menu and parses response
    print("----------------OPTIONS---------------")
    print("--> 1)\tLog in")
    print("--> 2)\tLog out")
    print("--> 3)\tAdd food to order")
    print("--> 4)\tView order")
    print("--> 5)\tUpdate order and checkout")
    print("--> 6)\tExit")
    chosen = False
    while not chosen:
        item = input("--> ").strip()
        try:
            val = int(item)
        except ValueError:
            print("Not a valid integer")
            continue
        if val <= 0 or val >= 7:
            print("Invalid menu item")
            continue
        chosen = True
    return item

def new_reg(Front):
    #Registers a new user
    print("------------NEW REGISTRATION----------")
    userID = str(uuid4())
    print("Your new user ID is:\n--> ", userID)
    #Validtes address of new user
    location = get_address(Front)
    try:
        #Registers new user to frontend
        Front.new_cust(userID, location)
        print("---------REGISTRATION COMPLETE--------")
        return userID, location
    except Exception as e:
        if str(e) == "AllServersDown":
            print("All servers currently down, try again later")
            sys.exit(406)
        print("Frontend server offline")
        sys.exit(111)

def login(Front):
    #Retreives a users information or makes a new record
    valid = False
    while not valid:
        userID = input("Enter your user ID or type 'new' to register:\n--> ")
        #Finds the users info based on their id
        if userID == 'new':
            return new_reg(Front)
        try:
            location = Front.find_cust(userID)
            #Print users information once found
            print()
            print("---------------LOGGED IN--------------")
            print("--- WELCOME, resident of:\n--> ", location[0], "\n--> ", location[-1])
            return userID, location
        except Exception as e:
            if str(e) == "CustomerNotFound":
                print("Customer could not be found")
                return new_reg(Front)
            if str(e) == "UserLoggedIn":
                print("User ID already in use by another client")
                continue
            if str(e) == "AllServersDown":
                print("All servers currently down, try again later")
                sys.exit(406)
            print("Frontend server offline")
            sys.exit(111)

def view_orders(Front, userID):
    #Retreives menu to add context to order numbers
    try:
        menu = Front.get_menu()
    except Exception as e:
        if str(e) == "MenuNotFound":
            print("Menu could not be retreived")
            sys.exit(407)
        if str(e) == "AllServersDown":
            print("All servers currently down, try again later")
            sys.exit(406)
        print("Frontend server offline")
        sys.exit(111)
    print("-----------------ORDERS---------------")
    #Retreives list of orders for user
    try:
        orders = Front.view_orders(userID)
    except Exception as e:
        if str(e) == "OrderNotFound":
            print("No orders could be found")
            return 411
        if str(e) == "AllServersDown":
            print("All servers currently down, try again later")
            sys.exit(406)
        print("Frontend server offline")
        sys.exit(111)
    for item in orders:
        print("-->\t", menu[int(item)])
        print()
    return 1

def checkout(Front, userID, order):
    #Places an order of food currently in the basket
    print("-------------CHECKING OUT-------------")
    if order == []:
        print("Hey! There's nothing in your basket!")
        return
    place_order(Front, userID, order)
    view_orders(Front, userID)

def logout(Front, userID):
    try:
        Front.logout(userID)
        return 1
    except Exception as e:
        if str(e) == "AllServersDown":
            print("All servers currently down, try again later")
            sys.exit(406)
        print("Frontend server offline")
        sys.exit(111)

def JustHungry(Front):
    userID = None
    location = None
    order = []
    print("--------------------------------------")
    print("-------------JUST HUNGRY!!------------")
    print()
    print("-------WELCOME TO JUST HUNGRY!--------")
    print()
    while True:
        item = options()
        if not userID == None:
            if item == "1":
                print("Already logged in")
                continue
        if userID == None:
            if item == "2" or item == "3" or item == "4" or item == "5":
                print("Not logged in")
                continue
        if item == "1":
            userID, location = login(Front)
            continue
        if item == "2":
            logout(Front, userID)
            userID = None
            location = None
            order = []
            continue
        if item == "3":
            order = order + order_food(Front)
            continue
        if item == "4":
            resp = view_orders(Front, userID)
            continue
        if item == "5":
            resp = checkout(Front, userID, order)
            logout(Front, userID)
            userID = None
            location = None
            order = []
            continue
        if item == "6":
            print("---------------QUITTING---------------")
            logout(Front, userID)
            sys.exit(6)
    
#Runs client with frontend server as a proxy object
with Pyro4.Proxy("PYRONAME:FrontServer") as Front:
    JustHungry(Front)


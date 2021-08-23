# JustHungry
### A distributed system for ordering and delivering delicious food!

## Overview
JustHungry is a distributed system consisting of four models of server:
* Frontend Server
* Name Server
* Backend Server
* APIServer

as well as a Client that the user can access to order food.

## Setting up JustHungry
To run JustHungry, you will need to install Pyro4, a Python package available via the package manager pip. Simply type:
```
pip install Pyro4
``` 
or
```
pip3 install Pyro4
```
Every other python package used in JustHungry is part of the Python Standard Library and thus does not need to be installed via a package manager or third party website. Each component can be located within different areas of the file system and do not need to be in the same directory to function, fulfilling the location and relocation transparency requirement.

## Running JustHungry
JustHungry relies on a naming server that does not exist as an executable file but instead is part of the Pyro4 package. This naming server can be run by typing:
```
python3 -m Pyro4.naming
```
Then, in any order, run the servers:
```
python3 FrontServer.py
```
```
python3 R1Server.py
```
```
python3 APIServer.py
```
R1Server.py contains code that allows for the creation of a new backend server (with a unique id number) every time it is run. Thus, you can initialise as many servers as you want by repeatedly executing this file. While running the program, to test the failure transparency requirement, simply terminate a server and, providing there is another backend server available, the system will continue to function.

### Running backend individually
It is suggested that each server is run in a separate terminal tab or window, this way it is visible which servers are currently running as well as terminate each individual server at will.

#### Terminate server
To terminate a server type:
```
Ctrl c
```

#### Restart server
To restart a terminated server type:
```
python3 <Server Name>
```

Upon terminating and restarting various backend servers, the API server and the frontend server, you will see that the failure and replication transparency requirements are all upheld.

### Running backend automatically
To run the FrontServer, R1Servers and APIServer automatically, you can execute the script ```multi-loader.sh``` which will run the frontend server as well as 4 backend servers. Do this by typing:
```
./multi-loader.sh
```
```NOTE:``` This method will still require you to set up the name server as described earlier, this is because when the name server is running as a background process in a terminal, it cannot be terminated and prevents the creation of another name server.

## How to Order
1. log in
2. choose 'Add food to order'
3. choose the food you want
4. type 'done'
5. choose 'Update order and checkout' to push chosen order to backend

## Overall transparency
### Replication
* The backend servers use passive replication to propagate changed data to the replicas and also use the state variable to store responses to function calls. 
* The frontend server generates a list of active backend servers to request and will always make requests to the first functioning one (the primary).
* If the primary backend server is terminated with ```Ctrl c```, the next backend server will begin to be used as primary. 

### Failure
* The system only requires one backend server to be online to function.
* This means that for ```n``` active backend servers, ```n-1``` can temrinate without functionality being affected.
* The APIServer can terminate without disrupting the system function and so can the external API.
* If any server is offline and causes the system to be inoperable then an error is displayed and the system quits gracefully.

### Location
* Any server can be hosted from anywhere in the filesystem due to the name server handling all server locations and providing these to requests.

### Relocation
* Since any backend server can be terminated without affecting the system functionality, and the frontend scans for active servers before each request, a backend server could be terminated, moved to a new location and then restarted successfully.

### Content locking
* The backend primary contains a list of active users which prevents multiple clients from logging in to the same user profile at one time.

## Client Interface
When running Client.py you will be presented with 6 menu options as follows:
1. Log in - Enter a user id or get assigned a new id if you do not have one
2. Log out - Log out of user profile
3. Add food to order - Retrieve the menu and select items to order
4. View order - View any orders submitted to the server
5. Update order and checkout - Send currently selected items to the server to be added to the order
6. Exit - quit

When external input or processing is needed, the client will invoke methods from the FrontServer and await for a response. Calls to FrontServer include:
* get_address() - validates postcode and returns additional address information
* get_menu() - returns the list of available food items
* place_order() - places an order for a customer
* new_cust() - creates a new  profile
* find_cust() - finds a customer profile based on an id string
* view_orders() - view orders for a given user

Each request is invoked to a Pyro4 object passed as an argument and so could be replaced by an alternate frontend with identical methods. This allows for modularity in the distributed system.

## FrontServer
This server acts as a bridge between the clients and the backend servers and hides any of their functionality. This is to adhere to the transparency requirements of the system. Calls made to the FrontServer contain zero context of the backend and its capabilities again allowing for transparency between modular aspects of the system.
Calls to R1Server include:
* check_validity() - checks a given address is valid
* external_add() - uses an external api to verify the validity of an address
* get_menu() - retrieves a menu from the backend
* new_cust() - adds a new customer profile to the backend
* find_cust() - finds a profile for a given customer id
* view_orders() - finds orders for a given user
* place_order() - places a new order for a user

### Failure and Replication Transparency
Each call to the backend server is performed by requesting a list of active backend servers from the name server, then making the request to each available server until the request returns a valid result and removing any backend servers that do not respond. Through this method, one backend server will consistently be used for requests (acting as primary) until it fails and is replaced with another active server. This allows for failure from any backend server while maintaining functionality in the frontend.

Each request is invoked with an identifying hash as an argument which is generated in the FrontServer and sent to the primary backend server for use in passive replication.

## R1Server
These servers hold all functionality within the system and act as a bridge between the frontend server and the APIServer for validating addresses. This server holds local variables containing the menu, customers and orders which all are accessed through remotely accessible methods.

### Replication
The R1Server adheres to replication and failure transparency requirements by maintaining a dictionary called ```state``` containing a set of hashes and corresponding responses. When a request arrives at the server, it checks its state for the id of that request and if found, the previous response is re-sent.

If the request has not been previously fulfilled, the response is generated and then stored in the state. If the request involved updating the orders or customers, the new data is propagated to any active duplicate backend servers. The replicas then send an acknowledgment of being updated to the primary.

### Content Locking
The primary R1Server contains a list of currently logged in users which is added to on login and reduced on logout of a user. This is to prevent the case of a user logging in from multiple clients and editing their orders simultaneously.

## APIServer
This server acts as a bridge between the primary backend server and the external API and serves requests from the backend server to https://postcodes.io.
postcodes.io has a postcode appended to the url and when requested via the urllib python package, provides information on that address, of which the Parish and Admin District are used.
The url of the external address validation API is held within an attribute of the APIServer class and so can easily be edited.

### Failure
If the APIServer is offline or the external API is offline, "Unavailable" will be returned as the parish and admin_district values however the system will continue to function normally. This is to account for the possibility that the API may change or require payment to use in future.

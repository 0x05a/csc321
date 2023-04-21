import zmq
from collections import defaultdict
import logging
from typing import Callable
context = zmq.Context()
# create server that listens on port 1337 and accepts connections and adds all ip addresses of clients into a list
server = context.socket(zmq.REP)
print(type(server))
server.bind("tcp://*:1337")
clients = []
b2s = lambda s: s.decode('utf-8')
s2b = lambda s: s.encode('utf-8')

class client:
    def __init__(self, ip) -> None:
        self.ip = ip
        self.pub: int # port
    
    def __str__(self):
        return f"Client({self.ip}, {self.pub})"
    
    def __repr__(self):
        return f"Client({self.ip}, {self.pub})"

class room:
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size
        self.clients = []
    
    def add_client(self, client: client):
        self.clients.append(client)
    
    def remove_client(self, client: client):
        self.clients.remove(client)
    
    def __str__(self):
        return f"Room({self.name}, {self.size}, {self.clients})"

rooms: list[room] = []
clients: list[client] = []


def list_clients(socket: zmq.Context.socket):
    """Return a list of all the clients connected to the server

    Args:
        socket (zmq.Socket): The server socket

    Returns:
        (list) List of clients connected to the server
    """
    ret = {"clients": clients, "rooms": str(rooms)}
    client_str = s2b(f"{str(ret)}")
    socket.send(client_str)

# create a function called add_client which adds it's ip to clients
def add_client(socket: zmq.sugar.socket.Socket, cmd: list[str]):
    """Add the ip address of the client to the list of clients

    Args:
        socket (zmq.Socket): The server socket
        command (list): ip sent from the client

    Returns:
        None
    """
    # get the ip address of the client
    ip = cmd[0]
    # add the ip address of the client to the list
    if ip not in clients:
        clients.append(ip)
        socket.send(b"Done")
    else:
        socket.send(b"Already in list")
    # log that we added the client
    logging.info(f"Added {ip} to the list of clients")

def remove_client(socket: zmq.sugar.socket.Socket, cmd: list[str]):
    """Remove the ip address of the client from the list of clients

    Args:
        socket (zmq.Socket): The server socket
        command (list): ip sent from the client

    Returns:
        None
    """
    # get the ip address of the client
    ip = cmd[0]
    # remove the ip address of the client from the list
    if ip in clients:
        clients.remove(ip)
        socket.send(b"Done")
    else:
        socket.send(b"Not in list")
    # log that we removed the client
    logging.info(f"Removed {ip} from the list of clients")


def query(socket: zmq.sugar.socket.Socket):
    """Query the server for a list of clients

    Args:
        socket (zmq.Socket): The server socket

    Returns:
        None
    """
    # send the list of clients 
    # 

def add_room(socket: zmq.sugar.socket.Socket, cmd: list[str]):
    """Add the ip address of the client to the list of clients

    Args:
        socket (zmq.Socket): The server socket
        command (list): name of the room and size of the room

    Returns:
        None
    """
    name = cmd[0]
    size = cmd[1]
    # add the ip address of the client to the list
    if name not in room:
        room[name] = []
        for i in range(int(size)):
            room[name].append("")
        socket.send(b"Done")

    else:
        socket.send(b"Already exists")
    # log that we added the client
    logging.info(f"Added {name} to the list of rooms")

def join_room(socket: zmq.sugar.socket.Socket, cmd: list[str]):
    """Add the ip address of the client to the list of clients

    Args:
        socket (zmq.Socket): The server socket
        command (list): name of the room, ip of client

    Returns:
        None
    """
    name = cmd[0]
    ip = cmd[1]
    # add the ip address of the client to the list
    if name in room:
        if len(list(filter(lambda x: x == "", room[name]))) == len(room[name]): # if no one in room
            room[name][0] = ip
            for a in room[name][1:]:
                socket.send(b'port:')
                p = b2s(socket.recv())
                client_room[ip].append(int(p))

        elif len(list(filter(lambda x: x == "", room[name]))) < len(room[name]): # if someone in room
            # logic to add them into room and then send them ip port combo to connect
            socket.send(b"Done")
    # now we need to connected to the client's ports using a req-reply server
        
print(type(join_room))

actions: dict[str: Callable] = {"list": list_clients, "add": add_client, 
 "remove": remove_client, "add_room": add_room}

# set logging level to listen for info level
logging.basicConfig(level=logging.INFO)

while True:
    # wait for a connection
    message = server.recv()
    # log message using logger module
    logging.info(message)
    command = b2s(message)
    if " " in command:
        command = command.split(" ")
    if command[0] in actions:
        actions[command[0]](server, command[1:])
    
    elif type(command) == str:
        if command in actions:
            actions[command](server)

    else:
        server.send(b"Invalid command")
        logging.info("Recieved invalid command")
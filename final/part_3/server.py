import zmq
from collections import defaultdict
import logging
from typing import Callable
import threading
import pdb
context = zmq.Context()
# create server that listens on port 1337 and accepts connections and adds all ip addresses of clients into a list
server = context.socket(zmq.REP)
server.bind("tcp://*:1337")

b2s = lambda s: s.decode('utf-8')
s2b = lambda s: s.encode('utf-8')

class client:
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.pub: int = port # port
    
    def __str__(self):
        return f"Client({self.ip}, {self.pub})"
    
    def __repr__(self):
        return f"Client({self.ip}, {self.pub})"

    def __eq__(self, o) -> bool:
        if o.ip == self.ip and o.pub == self.pub:
            return True
        else:
            return False

class room:
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size
        self.curr = 0
        self.clients = []
        self.votes = defaultdict(int)
        self.vote_port = defaultdict(int)
        self.vote_pswd = defaultdict(str)

    def add_votee(self, ip, port, pswd):
        print("Adding votee")
        self.votes[ip] = 0
        self.vote_port[ip] = port
        self.vote_pswd[ip] = pswd

    def vote(self, vote: str):
        if vote in self.votes:
            self.votes[vote] += 1
        
    def add_client(self, client: client):
        if client not in self.clients:
            self.clients.append(client)
            self.curr += 1
        if client.ip in self.votes:
            del self.votes[client.ip]
            del self.vote_port[client.ip]
            passwds.append(self.vote_pswd[client.ip])
            del self.vote_pswd[client.ip]
    
    def remove_client(self, client: client):
        if client in self.clients:
            self.clients.remove(client)
    
    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.name}"

    def __eq__(self, other) -> bool:
        if other.name == self.name and other.size == self.size:
            return True
        else:
            return False

rooms: list[room] = []
clients: list[client] = []
passwds: list[str] = []

def random_s() -> str:
    """Generates a random string of length 10"""
    import random
    import string
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(10))

def query(socket: zmq.sugar.socket.Socket, cmd: list[str]):
    """Query the server for a list of clients

    Args:
        socket (zmq.Socket): The server socket

    Returns:
        None
    """
    # check to see if anyone has been accepted into a channel
    for r in rooms:
        if len(r.votes) > 0:
            try:
                for v in r.votes:
                    print(f"DEBUG line 96 {r.votes[v]}")
                    if r.votes[v] >= r.curr:
                        r.add_client(client(v, r.vote_port[v]))
                        logging.info(f"Added {v} to {r.name}")
                        # pdb.set_trace()
            except RuntimeError:
                pass
            
            except Exception as e:
                print(e)
                quit()

            
    if cmd[0] not in passwds:
        socket.send(b"Bad req")
        return

    if "votes" in cmd[1]:
        info_str = ""
        for r in rooms:
            if len(r.votes) > 0:
                info_str += f"{list(r.votes.keys())[0]}"
                break
        socket.send(s2b(info_str))
    
    elif "room" in cmd[1]:
        if len(cmd) >= 3:
            info_str = ""
            for r in rooms:
                if r.name == cmd[2]:
                    for c in r.clients:
                        info_str += f"{c.ip}:{c.pub} "
            socket.send(s2b(info_str))
    else:
        socket.send(b"Bad req")

def add_room(socket: zmq.sugar.socket.Socket, cmd: list[str]):
    """Add the ip address of the client to the list of clients

    Args:
        socket (zmq.Socket): The server socket
        command (list): name of the room and size of the room

    Returns:
        None
    """
    name = cmd[0]
    size = int(cmd[1])
    # add the ip address of the client to the list
    if room(name, size) not in rooms:
        rooms.append(room(name, size))
         
    # log that we added the client
    logging.info(f"Added {name} to the list of rooms")
    socket.send(b"Added room")

def accept(socket: zmq.sugar.socket.Socket, cmd: list[str]):
    """Add the ip address of the client to the list of clients

    Args:
        socket (zmq.Socket): The server socket
        command (list): name of the room, ip of client

    Returns:
        None
    """
    # accept ip
    # flaw is not authenticated, someone can vote twice. 
    pswd = cmd[0]
    if pswd not in passwds:
        socket.send(b"Bad req")
        return
    ip = cmd[1]
    sent = False
    # add the ip address of the client to the list
    for room in rooms:
        for c in room.votes:
            if ip == c:
                room.vote(ip)
                socket.send(b"Accepted")
                sent = True
    if not sent:
        socket.send(b"vote not accepted")
    

def reject(socket: zmq.sugar.socket.Socket, cmd: list[str]):
    """Add the ip address of the client to the list of clients

    Args:
        socket (zmq.Socket): The server socket
        command (list): name of the room, ip of client

    Returns:
        None
    """
    # reject ip
    paswd = cmd[0]
    if paswd not in passwds:
        socket.send(b"Bad req")
        return

    ip = cmd[1]
    sent = False
    # add the ip address of the client to the list
    for room in rooms:
        for c in room.clients:
            if ip == c.ip:
                del room.votes[ip]
                socket.send(b"Rejected")
                sent = True
    if not sent:
        socket.send(b"vote not accepted")

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
    port = int(cmd[2])
    # add the ip address of the client to the list
    for room in rooms:
        if room.name == name:
            print(f"DEBUG 207 {room.curr} <? {room.size}")
            if room.curr < room.size:
                if room.curr == 0:
                    room.add_client(client(ip, port))
                    ret_str = random_s()
                    passwds.append(ret_str)
                    socket.send(s2b(ret_str))

                elif room.curr >= 0:
                    ret_str = random_s()
                    room.add_votee(ip, port, ret_str)
                    socket.send(s2b(ret_str))
            else:
                socket.send(b"Room is full")
                return

actions: dict[str: Callable] = {"add_room": add_room, "join_room": join_room, "query": query, "accept": accept, "reject": reject}
# set logging level to listen for info level
logging.basicConfig(level=logging.INFO)

def handle_req(message: bytes, socket: zmq.sugar.socket.Socket):
    """Handle a request from a client

    Args:
        socket (zmq.Socket): The server socket

    Returns:
        None
    """
    # wait for a connection
    # log message using logger module
    logging.info(message)
    print("AB")
    command = b2s(message)
    if " " in command:
        command = command.split(" ")
    if command[0] in actions:
        actions[command[0]](socket, command[1:])
    
    elif type(command) == str:
        if command in actions:
            actions[command](socket)

    else:
        socket.send(b"Invalid command")
        logging.info("Recieved invalid command")

while True:
    message = server.recv()
    # log message using logger module
    logging.info(message)
    command = b2s(message)
    if " " in command:
        command = command.split(" ")

    if command[0] in actions:
        actions[command[0]](server, command[1:])
    
    elif type(command) == str:
        func = False
        if command in actions:
            actions[command](server)
            func = True
        if not func:
            server.send(b"Invalid command")
            logging.info("Recieved invalid command")

    else:
        server.send(b"Invalid command")
        logging.info("Recieved invalid command")
# simple zeromq client
import zmq
import netifaces
import ipaddress
import socket
from typing import Union
import json # for turning strings into dictionaries
import threading
import time

msg_queue: dict[str, int] = {}
room_size: int

# str to dict function
def s2d(s: str): # -> dict[str, str]
    """Convert a string to a dictionary"""
    return ""


def get_interfaces(): # -> list[str]:
    """Return a list of all the interfaces on this host

    Args: None
    Returns: (list) List of interfaces for this host
    """
    return netifaces.interfaces()

def get_ips(interface: str): # -> dict[str, Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]:
    """For the given interface string, return a dictionary with
    the IPv4 and IPv6 address objects for that interface

    Args:
      interface (str): String representation of the interface
          (e.g. "eth0" or "en0")

    Returns: (dict) Dictionary with the following form
      {'v4': ipaddress.IPv4Address('192.168.65.48'),
       'v6': ipaddress.IPv6Address('fe80::14e1:8686:e720:57a')}
    """
    ret: dict[str, Union[ipaddress.IPv6Address, ipaddress.IPv4Address]] = {}
    ipv4_addr = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
    ret['v4'] = ipaddress.IPv4Address(ipv4_addr)
    return ret



# function that sets up a subscriber socket to a client ip and port
def setup_subscriber(ip: str, port: int): # -> zmq.Socket:
    """Set up a subscriber socket to the given ip and port"""
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect(f"tcp://{ip}:{port}")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
    while True:
        msg = subscriber.recv()
        print(b2s(msg))


def setup_publisher(port: int): # -> zmq.Socket:
    """Set up a publisher socket to the given ip and port"""
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    sent = [] # I believe this is like a static variable, I am hoping it is unique for every thread
    publisher.bind(f"tcp://*:{port}")
    # if there is a message queued up, send it
    while True:
        try:
            if len(msg_queue) > 0:
                for msg in msg_queue:
                    if msg not in sent:
                        publisher.send_string(msg)
                        sent.append(msg)
                        msg_queue[msg] += 1
                        if msg_queue[msg] >= room_size:
                            del msg_queue[msg]
            # else:
                # sent = []
        except RuntimeError:
            pass
            
subscribers: list[tuple[str, int]] = []

ifaces = get_interfaces()

ips = get_ips(ifaces[1])
ip = ips['v4']
room_name: str = ""
port: int = 31337
b2s = lambda s: s.decode('utf-8')
s2b = lambda s: s.encode('utf-8')

# function that creates n subscriber sockets threads that takes a list of ips and ports
def create_subscribers(ips: list[str], ports: list[int]): # -> list[zmq.Socket]:
    """Create n subscriber threads that take a list of ips and ports"""
    subscribers = []
    for i in range(len(ips)):
        t = threading.Thread(target=setup_subscriber, args=(ips[i], ports[i]), daemon=True)
        t.start()
        subscribers.append(t)
    return subscribers

# create_publisher function which takes a list of ports and creates threads for each port
def create_publishers(ports: list[int]): # -> list[zmq.Socket]:
    """Create n publisher threads that take a list of ports"""
    publishers = []
    for i in range(len(ports)):
        t = threading.Thread(target=setup_publisher, args=(ports[i],), daemon=True)
        t.start()
        publishers.append(t)
    return publishers
    
def join_room(socket: zmq.sugar.socket.Socket, room: str):
    """Join a room with the given socket"""
    socket.send_string(f"join {room} {ip} {str(port)}")
    msg = socket.recv()
    msg = b2s(msg)
    if "Joined!" in msg:
        parse = msg.split("!")[1]
        parse = parse.split(" ")
        for p in parse:
            ip = p.split(":")[0]
            port = int(p.split(":")[1])
            create_subscribers([ip], [port])
            subscribers.append((ip, port))
            print(f"Joined {ip}:{port}")
    elif "Room is full" in msg:
        print("Room is full")

def create_room(socket: zmq.sugar.socket.Socket, room: str, size: int):
    """Create a room with the given socket"""
    socket.send_string(f"add_room {room} {size}")
    msg = socket.recv()
    msg = b2s(msg)
    if "dded" in msg:
        print("Created room!")

def query(socket: zmq.sugar.socket.Socket):
    i = 0
    while 1:
        if (i % 2) == 0:
            time.sleep(5)
            socket.send_string("query votes")
            msg = socket.recv()
            msg = b2s(msg)
            if len(msg):
                i = input("Accept {msg}? (y/n) ")
                if i == "y":
                    socket.send(s2b(f"accept {msg}"))
                else:
                    socket.send(s2b(f"reject {msg}"))
                msg = socket.recv()
                if "Accepted" in b2s(msg):
                    print("Accepted")
                else:
                    print("Rejected")
            i += 1
        else:
            time.sleep(5)
            socket.send_string("query room {room_name}")
            msg = socket.recv()
            msg = b2s(msg)
            if len(msg):
                s = msg.split(" ")
                for p in s:
                    ip = p.split(":")[0]
                    port = int(p.split(":")[1])
                    if (ip, port) not in subscribers:
                        create_subscribers([ip], [port])
                        print(f"Joined {ip}:{port}")
            i += 1
                


create_publishers([31337])

# req socket that connects to localhost port 1337
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:1337")
#create_room(socket, "test", 2)
#join_room(socket, "test")
# create while loop which takes user input and sends it to the server
while True:
    msg = input("Enter a message: ")
    socket.send_string(msg)
    msg = socket.recv()
    print(b2s(msg))




# while loop that sends the server whatever is input
# while True:
#     msg = input("Enter a message: ")

# simple zeromq client
import zmq
import netifaces
import ipaddress
import socket
from typing import Union
import json # for turning strings into dictionaries
import threading

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
        print(msg)


def setup_publisher(port: int): # -> zmq.Socket:
    """Set up a publisher socket to the given ip and port"""
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    sent = [] # I believe this is like a static variable, I am hoping it is unique for every thread
    publisher.bind(f"tcp://*:{port}")
    # if there is a message queued up, send it
    if len(msg_queue) > 0:
        for msg in msg_queue:
            if msg not in sent:
                publisher.send_string(msg)
                sent.append(msg)
                msg_queue[msg] += 1
                if msg_queue[msg] >= room_size:
                    del msg_queue[msg]
    else:
        sent = []

    

ifaces = get_interfaces()

ips = get_ips(ifaces[1])
ip = ips['v4']

b2s = lambda s: s.decode('utf-8')
s2b = lambda s: s.encode('utf-8')

context = zmq.Context()
# create client that connects to server on port 1337
client = context.socket(zmq.REQ)
client.connect("tcp://localhost:1337")
# create a loop that sends user input to the server
while True:
    # get user input
    cmd = input("Enter a command: ")
    # send the user input to the server
    if "connect" in cmd:
        cmd = cmd.split(" ")
        ip = cmd[1]
        port = cmd[2]
        # set up daemon thread that listens for messages from the server
        t = threading.Thread(target=setup_subscriber, args=(ip, port), daemon=True)
        t.start()
        # we need to set up room size so we can publish and subscribe properly
    if "send" in cmd:
        cmd = cmd.split(" ")
        msg = cmd[1]
        # set up daemon thread that sends messages to the server
        msg_queue[msg] = 0
    client.send(s2b(cmd))
    # get the response from the server
    resp = client.recv()
    # print the response
    print(b2s(resp))
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
            

ifaces = get_interfaces()

ips = get_ips(ifaces[1])
ip = ips['v4']

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
    


# TODO SET UP SERVER AND CLIENT SET UP
# connection
# create a n - 1 publisher sockets and subscriber sockets
# create a n - 1 thread for each publisher and subscriber socket
n = 3 # will change in a bit
room_size = n - 1
# create a publisher socket and thread

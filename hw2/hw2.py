# Author Zack Chapman
import netifaces
import ipaddress
from typing import Union

def get_interfaces() -> list[str]:
    """Return a list of all the interfaces on this host

    Args: None
    Returns: (list) List of interfaces for this host
    """
    return netifaces.interfaces()


def get_mac(interface: str) -> str:
    """For the given interface string, return the MAC address as a
    string

    Args:
      interface (str): String representation of the interface
          (e.g. "eth0" or "en0")

    Returns: (str) MAC address
    """
    return netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']

def get_ips(interface: str) -> dict[str, Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]:
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
    ipv6_addr = netifaces.ifaddresses(interface)[netifaces.AF_INET6][0]['addr']
    if "%" in ipv6_addr:
      ipv6_addr = ipv6_addr.split("%")[0]
    ret['v6'] = ipaddress.IPv6Address(ipv6_addr)
    return ret


def get_netmask(interface: str) -> dict[str, Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]:
    """For the given interface string, return a dictionary with the
    IPv4 and IPv6 netmask objects (as IPv4/v6Address objects) for that
    interface

    Args:
      interface (str): String representation of the interface
          (e.g. "eth0" or "en0")

    Returns: (dict) Dictionary with the following form
      {'v4': ipaddress.IPv4Address('255.255.255.0'),
       'v6': ipaddress.IPv6Address('ffff:ffff:ffff:ffff::')}
    """
    ret: dict[str, Union[ipaddress.IPv6Address, ipaddress.IPv4Address]] = {}
    ipv4_addr = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['netmask']
    ret['v4'] = ipaddress.IPv4Address(ipv4_addr)
    ipv6_addr = netifaces.ifaddresses(interface)[netifaces.AF_INET6][0]['netmask'].split("/")[0]
    ret['v6'] = ipaddress.IPv6Address(ipv6_addr)
    return ret

def get_network(interface: str) -> dict[str, Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]:
    """For the given interface string, return a dictionary with
    the IPv4 and IPv6 network objects for that interface

    Args:
      interface (str): String representation of the interface
          (e.g. "eth0" or "en0")

    Returns: (dict) Dictionary with the following form
      {'v4': ipaddress.IPv4Network('192.168.65.0/24'),
       'v6': ipaddress.IPv6Network('fe80::/64')}
    """
    
    
    ipv4 = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
    ipv6 = netifaces.ifaddresses(interface)[netifaces.AF_INET6][0]['addr']
    ipv4_network_str = f"{ipv4}"
    ipv6_network_str = f"{ipv6}"
    ret: dict[str, Union[ipaddress.IPv4Network, ipaddress.IPv6Network]] = {}
    ret['v4'] = ipaddress.IPv4Network(ipv4_network_str)
    ret['v6'] = ipaddress.IPv6Network(ipv6_network_str)
    return ret

# HW Questions:
"""What is the IP configuration for your computer (i.e. what is the output of the shell 
command used for this purpose)? Write a function that uses the netifaces module and returns
 a list of all interfaces on for this host:"""

"""
➜  ~ ifconfig
lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 3057  bytes 245512 (239.7 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 3057  bytes 245512 (239.7 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

wlp0s20f3: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.0.0.23  netmask 255.255.255.0  broadcast 10.0.0.255
        inet6 fe80::328:8d44:44cf:27b2  prefixlen 64  scopeid 0x20<link>
        ether 48:51:c5:58:f8:86  txqueuelen 1000  (Ethernet)
        RX packets 1042642  bytes 934837956 (891.5 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 594215  bytes 70142127 (66.8 MiB)
        TX er
"""
print("List of interfaces\n")
for x in get_interfaces():
    print(f"\t{x}")
"""
What are the MAC addresses for these interfaces? 
Write a function that uses netifaces to return the MAC address for a given interface:
we can see it after ether in ifconfig command
"""
print("\n\nmac addresses related to interface\n")
for x in get_interfaces():
    print(f"{x} -> {get_mac(x)}")
"""
What are the IPv4 and IPv6 addresses associated with these interfaces? 
Write a function that uses netifaces to return both the IPv4Address Links
to an external site. and IPv6Address Links to an external site. objects
for the given interface as a dictionary.
"""
print("\n\nip address related to interfaces\n")
for x in get_interfaces():
  ips = get_ips(x)
  print(f"{x}\n\tipv4: {ips['v4']}\n\tipv6: {ips['v6']}")

"""
What are the IPv4 and IPv6 netmasks of each of these IP subnets? 
Write a function that users netifaces to return both the IPv4Address 
Links to an external site. and IPv6Address Links to an external site. 
object representation of the netmasks for the given interface as a dictionary.
"""
print("\n\nNetmask for each interface\n")
for x in get_interfaces():
  nm = get_netmask(x)
  print(f"{x}\n\tipv4: {nm['v4']}\n\tipv6: {nm['v6']}")

"""
What are the IPv4 and IPv6 networks associated with each of these addresses? 
Write a function that users netifaces to return both the IPv4Network Links to an external site. 
and IPv6Network Links to an external site. objects for the given interface as a dictionary.
"""
print("\n\nNetwork for each interface\n")
for x in get_interfaces():
  nw = get_network(x)
  print(f"{x}\n\tipv4: {nw['v4']}\n\tipv6: {nw['v6']}")
# Parsing the packets out of the full-take.pcap
## Overview:
    as you know the full-take.pcap has a pcap dump from all servers and clients from the weather 0MQ and task 0MQ programs.
    To distinguish between the services we use the port numbers that the services use. The weather services use port 5556 and the task suite uses port 5557 and 5558. We then wrote a python script that uses scapy to parse the packets and pull all packets which had either a sending or destination port of those above.
    
```python
def get_packets_with_ports(ports):
    packets = rdpcap("full-take.pcap") # parse the dump
    packets_with_ports = []
    for packet in packets: # iterate over packets
        if packet.haslayer(TCP): # check if tcp packet
            # source or dest should have this port
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
            if src_port in ports or dst_port in ports: # check if the ports work out
                packets_with_ports.append(packet) # add to the list of packets
    # return list of packets
    return packets_with_ports
```
We can then just simply create a list of packets and use a scapy function to turn the list of packets into a file
```python
def main() -> None:
    # we know that the client is connecting to port 5556 which the server is listening to
    wu_ports = [5556]
    wu_packts = get_packets_with_ports(wu_ports)
    wrpcap("weather.pcap", wu_packts)
    # we also know that the task suite is using ports 555[7, 8]
    task_ports = [5557, 5558]
    task_packts = get_packets_with_ports(task_ports)
    wrpcap("task.pcap", task_packts)
    print("Parsed packets into weather.pcap and task.pcap!")
```
If you insepct eather.pcap and task.pcap you will see that these pcaps indeed hold the network traffic.
Thanks!

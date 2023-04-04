from scapy.all import *
from scapy.layers.inet import TCP
from scapy.layers.inet import IP

# gets all packets with a specific list of ports 
def get_packets_with_ports(ports: list[int]) -> list[Packet]:
    packets = rdpcap("full-take.pcap")
    packets_with_ports = []
    for packet in packets:
        if packet.haslayer(TCP):
            # source or dest should have this port
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
            if src_port in ports or dst_port in ports:
                packets_with_ports.append(packet)
    # return list of packets
    return packets_with_ports


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

# helper function that gets data from tcp packets
def get_data(packet) -> None:
    if packet.haslayer(TCP):
        data = packet[TCP].payload
        if data:
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
            timestamp = packet.time
            #convert from Edecimal to simething datetime can parse
            timestamp = int(timestamp)
            #change timestamp from scapy format to datetime
            timestamp = datetime.fromtimestamp(timestamp)
            # print data
            print(f"{src_ip}:{src_port} -> {dst_ip}:{dst_port} @ {timestamp} \n{data.show(dump=True)}")
if __name__ == "__main__":
    main()
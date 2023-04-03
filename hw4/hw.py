from dns import reversename
from dns.resolver import resolve
import dns
import networkx as nx
from networkx.drawing.nx_pydot import write_dot
import os
name2index = {"site": 0, "domain": 1, "alexia": 2, "similarweb": 3, "type": 4, "country": 5}
# this function will create a list of tuples, the tuples will have 6 values which will be taken from the tab seperated file, then appended to the list
def read_file(filename):
    f = open(filename, 'r')
    list = []
    for line in f:
        line = line.split('\t')
        tuple = (line[0], line[1], line[2], line[3], line[4], line[5].replace("\n", ""))
        list.append(tuple)
    return list

G = nx.DiGraph()

domains = list(map(lambda x: x[name2index["domain"]], read_file("domains.tsv")))[1:]

for domain in domains:
    G.add_node(domain)
    print(f"Adding node {domain}")
    try:
        a_record = resolve(domain, "A")
    except dns.resolver.NXDOMAIN:
        continue
    except dns.resolver.NoAnswer:
        continue
    if len(a_record):
        for addr in a_record:
            search_addr = reversename.from_address(str(addr))
            try:
                reverse_search_results = resolve(search_addr, "PTR")
            except dns.resolver.NXDOMAIN:
                continue
            except dns.resolver.NoNameservers:
                continue
            except dns.resolver.LifetimeTimeout:
                continue
            if len(reverse_search_results):
                for d in reverse_search_results:
                    G.add_node(str(d))
                    G.add_edge(domain, str(d))
                    print(f"Adding edge {domain} -> {str(d)}")

print("Writing dotfile")
write_dot(G, "Graph.dot")
os.system("dot -Tpng Graph.dot -o Graph.png")
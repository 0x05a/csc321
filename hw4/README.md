# DNS Graphing

first we have to parse the tsv file which is pretty simple to do.
I just created a list of tuples which are ordered by the column ordering.
then I just threw all the domains into a list and did dns forward then reverse lookups.
this code uses the dnspython module to perform all dns requests.

it uses the resolve function to forward and reverse search a records or ptr records.
```
# forward search
a_record = resolve(domain, "A")
# reverse search
search_addr = reversename.from_address(str(addr))
reverse_search_results = resolve(search_addr, "PTR")
``` 
from this information we create a networkx directed graph that has arcs (directed edge) between domains and reverse lookup'd domains
The code below shows how simple that is.
```
# Where domain is the domain from the tsv and d is the reverse lookup'd domain
G.add_edge(domain, str(d))
print(f"Adding edge {domain} -> {str(d)}")
```
With this information in mind we can write some pseudo code to show what we are trying to accomplish.
```
domains = parse_tsv(file)
for domain in domains:
    forward_lookup(domain)
        if ip:
            reverse_search(ip)
            for domains in reverse_search:
                create arc from domain -> reverse'd domain
display graph
```
The code has some slight error handling incase the dns server does not have a record or fails. We use networkx to create a dotfile and then convert the dotfile to become a png. Unfortunately the way it renders is difficult to view well. Networkx is written to do analysis moreso than render graphs but we still get an accurate image.

*Note* to view image, click on it believe and scroll from left to right and you will see the image.
![](Graph.png)
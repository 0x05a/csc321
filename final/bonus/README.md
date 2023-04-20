## Overview

To create our p2p chat server, we need to have a server that the clients connect to in order to receive relevant information. We must fulfill the following demands:

- Chat clients do not need to have prior IP information of other chat clients.
- Chat content must be 100% P2P. I.e. chat content must not go through a 3rd party server.
- All parties in chat must agree to all additional peers.

We have a request-reply server that when you connect you have some commands to use:

- `LIST` - list out the clients
- `ADD ip` - let the server know we are happy to participate
- `create room (name) (size)`
- `join room (name)`
- `delete room` only creator can delete room

When you have a room, if anyone who would like to connect to your room, they can do so through the following process:

1. `room` - whenever you create a room, let's say there are R clients expected to be in the room.
2. Each client opens R-1 ports and tells the server which ports are open for the room.
3. The server connects on those ports, and then whenever all the participants in the room agree (they listen to the server on that port for new connections), the server disconnects and a new client connects to the peers.

Note that we do not send chat data to the server port that is connected to us for decentralized privacy purposes.

The protocol for creating a room is:
    Client sends server create room name size
    the server adds the name and size to a dictionary relating them
    then the client sends the server the ports it is listening on
    the server connects to the clients ports
the protocol for joining a room is:
    Client sends server join room (name)
    server responds with ip and port of the client to connect to and size and disconnects form that port
    the client connects and sends the server a list of size - 1 ports
    the server connects to those ports

For the client we will use a zeromq pubsub patten. it will list as a published and connect to other clients as a subscriber port

can daemonize the part of the client that is subscribed and listening to messages
hardest part to code is just client and server setting up dominion
we are maybe making it too complex
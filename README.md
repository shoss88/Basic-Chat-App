# Basic-Chat-App

This is just a simple client-server chat application that can be run on the command line. Each server can run with multiple registered clients.

To start the server, open one command prompt in the same directory as server.py and type: python server.py -p (port number).

To register a client, open another command prompt in the same directory as client.py and type: python client.py -p (server port number) -u (username).

For multiple clients, open seperate command prompts for each and register them as mentioned above. Make sure they all connect to their intended server using that server's port number.

There are 4 possible actions that can be made by a client:
* Message: Send a message to other clients (specified in the input) connected to the same server. If a name is duplicated within the input, that client will only receive 1 message. The command format is below:
  * msg (number_of_users) (username1) (username2) … (message)
* List of users: Lists all users within the same server to the client requesting the list. The names are listed in alphabetical order. The command format is below:
  * list
* Help: Returns the full list of commands and their proper format to the client requesting them. The command format is below:
  * help
* Quit: Closes the connection to the server and shuts the client down. The command format is below:
  * quit

If the server receives an unknown command, the server has no more space for more clients, or the client's username has already been taken by another client, the server will print an error.


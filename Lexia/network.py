import socket
import threading
import sys
from requests import get

class Pi2Pi(object):
    def __init__(self,adress = 'XXX.XXX.X.XXX',port=0000): #Replace with Stuff
        self.adress = adress
        self.port = port

    def send(self,msg):
        try:
            get('http://'+self.adress+':'+str(self.port)+'/'+msg)
        except Exception as e:
            print(e)

class ComObj(object): # Not Thread safe but who cares
    def __init__(self):
        self.id = 0
        self.str = ""
		
class WebServer(object):
    def __init__(self, port=0000, com=ComObj()):
        self.host = 'XXX.XXX.X.XXX' #socket.gethostname().split('.')[0] # Default to any avialable network interface
        self.port = port
        self.com = com

    def run(self):
        """
        Attempts to create and bind a socket to launch the server
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            print("Starting server on {host}:{port}".format(host=self.host, port=self.port))
            self.socket.bind((self.host, self.port))
            print("Server started on port {port}.".format(port=self.port))

        except Exception:
            print("Error: Could not bind to port {port}".format(port=self.port))
            sys.exit(1)

        self._listen() # Start listening for connections

    def _listen(self):
        """
        Listens on self.port for any incoming connections
        """
        self.socket.listen(5)
        print("start listening ...")
        while True:
            (client, address) = self.socket.accept()
            client.settimeout(60)
            print("Recieved connection from {addr}".format(addr=address))
            threading.Thread(target=self._handle_client, args=(client, address)).start()
        print("Webserver ended.")
        self.socket.shutdown(socket.SHUT_RDWR)
        

    def _handle_client(self, client, address):
        """
        Main loop for handling connecting clients and serving files from content_dir
        Parameters:
            - client: socket client from accept()
            - address: socket address from accept()
        """
        PACKET_SIZE = 1024
        while True:
            data = client.recv(PACKET_SIZE).decode() # Recieve data packet from client and decode
            if not data: break

            request_method = data.split(' ')[0]
            
            if request_method == "GET" or request_method == "HEAD":
                # Ex) "GET /index.html" split on space
                command = data.split(' ')[1]
                temp = command.split('&')
                if len(temp)<2:
                    client.send('HTTP/1.1 200 OK\n'.encode())
                    client.close() 
                    break
                code,string = temp[0],temp[1]
                self.com.id = int(code[1:])
                self.com.str = string.replace('_',' ')
                client.send('HTTP/1.1 200 OK\n'.encode())
                client.close()
                break
            else:
                print("Unknown HTTP request method: {method}".format(method=request_method))
                break


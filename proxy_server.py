from socket import *
import sys

# function to check if the url exists in the block list or not for filtering
def filter_url(url) :
    with open('block_list.txt', 'r', encoding='utf-8') as file:
        if url in file:
            print("/////////////////////////URL IS BLOCKED/////////////////////////")
            return True
        else:
            return False

# check if we entered a correct command in the terminal
# we should enter the address so our arguments are 2
if len(sys.argv) <= 1:
    print('Usage : "python proxy_server.py server_ip"\n[server_ip: It is the IP Address Of Proxy Server]')
    sys.exit(2)

# Create a server socket, bind it to a port and start listening 
tcpSerSock = socket(AF_INET, SOCK_STREAM)

# Standard loopback interface address (localhost)
HOST = "127.0.0.1"
# Our chosen port number
PORT = 5050
# check command arguments and take the address from it
if sys.argv[1] :
    HOST = sys.argv[1]
tcpSerSock.bind((sys.argv[1], PORT))
tcpSerSock.listen(10)

while 1:
    # Start receiving data from the client 
    print('\n\nReady to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)
    # 1024 is the buffer size
    message =  tcpCliSock.recv(1024)
    print("Received message\n" , message)

    # Extract the filename from the given message 
    print (message.split()[1])
    #if url not blocked and not empty message
    if(not filter_url(message.split()[1].decode("utf-8")) and message != ""):
        filename = message.split()[1].decode("utf-8").rpartition("/")[2]
        print(filename)
        fileExist = "false"
        file_to_use = "\\cache_files\\" + filename
        print(file_to_use)

        try:
            # Check if the file exist in the cache_files
            f = open(file_to_use[1:], "rb")
            outputdata = f.readlines()
            print('Read from cache')
            fileExist = "true"
            
            # proxy_server finds a cache hit and generates a response message
            tcpCliSock.send(b"HTTP/1.0 200 OK\r\n")
            tcpCliSock.send(b"Content-Type:text/html\r\n")
            
            for line in outputdata:
                tcpCliSock.send(line)
            f.close()
            
        except IOError:
            # Error handling for file not found in cache_files
            if fileExist == "false":
                # Create a socket on the proxy_server
                mysocket = socket(AF_INET, SOCK_STREAM)
                hostn = message.split()[4].decode("utf-8")
                print(hostn)
                
                try:
                    # Connect to the socket to port 80
                    mysocket.connect((hostn, 80))              
                    
                    # Create a temporary file on this socket and ask port 80 for the file requested by the client
                    fileobj = mysocket.makefile('w', None)
                    fileobj.write("GET " + message.split()[1].decode("utf-8") + " HTTP/1.0\n\n")
                    fileobj.close()

                    # Read the response into buffer
                    fileobj = mysocket.makefile("rb", None)
                    buffer = fileobj.readlines()
                    fileobj.close()
                    
                    # Create a new file in the cache_files for the requested file
                    # Also send the response in the buffer to client socket and the corresponding file in the cache_files
                    tmpFile = open("./cache_files/" + filename, "wb+")
                    for line in buffer:
                            tmpFile.write(line)
                            tcpCliSock.send(line)
                    tmpFile.close()
                    mysocket.close()
                except:
                    print("Illegal request")
            else:
                # HTTP response message for file not found
                # Close the client and the server sockets
                tcpCliSock.close()
    else :
        # HTTP response message for file not found
        tcpCliSock.send(b'HTTP/1.0 404 sendError\r\n')
        tcpCliSock.send(b'Content-Type:text/html\r\n')
        # Close the client and the server sockets
        tcpCliSock.close()
        print("socket closed")
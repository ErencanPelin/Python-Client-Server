from socket import *

def debug(msg):
    if True:
        print(msg)

# import socket module
serverSocket = socket(AF_INET, SOCK_STREAM)
# Prepare a sever socket
#Fill in start
serverPort = 6544  # port number for HTTP protocol
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort)) #binds to the socket of number serverPort on the ip of this local machine
serverSocket.listen(1) #1 is the queue size means we can handle 1 connection at a time. The listen function makes a socket ready for accepting connections
#Fill in end
print('Ready to serve...')
while True: # forever listen
    # Establish the connection
    print("\nReady to accept new connection")
    # waiting for TCP connection request
    connectionSocket, addr = serverSocket.accept() # we found a connection
    debug(" -- Accepted connection")
    # if any errors move on
    try:
        try:
            # decoding msg recieved bytes into string
            message = connectionSocket.recv(2048).decode() #we decode from raw bytes (1's and 0's) and turn it into utf-8
            debug(" -- HTTP Request: ")
            debug(message.replace("\r\n", ", ")) # spits out the entire msg request we got

            # get filename from request
            splitMessage = message.split() # splits the message at every whilespace - including line breaks

            # Sometimes an empty request is made, don't let it mess us up
            if len(splitMessage) < 3: # if the length of the split message is less than 3 then its not a valid http request
                debug(" -- Aborting, not enough params for HTTP Request")
                raise ConnectionResetError #we purposely create an error to prevent errors further down the line

            # split returns array, [1] gets path from HTTP request array
            filename = splitMessage[1] #
            method = splitMessage[0] # is the 'GET'
            httpVer = splitMessage[2].split("/")[1]

            # If the last character of a request path is a /, fetch the index.html file from that directory
            if filename[-1] == "/": # if the last character is a / then they are requesting the 'home page' and so we add index.html so that the 
                filename += "index.html"

            # try and read filename from public directory on OS
            # [1:] string slice removes the slash
            f = open("public/" + filename[1:]) # a string slive. -> open the file they host is requesting so that we can read the data within it - Starts reading from the second character to the end of the file
            outputdata = f.read() # read the data within the html page file
            f.close() # close the html file - we don't need it anymore 

            # Search the html file for advanced replacement strings and overwrite with variables
            replacements = { # some fancy functionality, not necessary, displays content about the host on the actual html page
                "%PATH%": filename,
                "%IP%": addr[0],
                "%METHOD%": method,
                "%HTTPVER%": httpVer
            }
            for keyword in replacements:
                outputdata = outputdata.replace(keyword, str(replacements[keyword]))
            debug(" -- File read & replaced.") # apply the fancy stuff to the html 

            responseHeaders = [ # set up our response headers
                "HTTP/1.1 200 OK",
                "Content-Length: " + str(len(outputdata)),
                "Content-Type: text/html; charset=utf-8"
            ]

            # Send the HTTP headers line into socket
            for header in responseHeaders: #send our header one by one back to user while encoding them back into bytes
                # encode each header in byte form and push it to the socket
                connectionSocket.send((header + "\r\n").encode())
            # adds blank new line to seperate headers and content/body
            connectionSocket.send("\r\n".encode()) #we then send a line break, because we need to seperate the headers and the body of the html file from each other since HTTP relies on this 
            debug(" -- Headers sent.")

            # Send the content of the requested file to the client
            connectionSocket.send(outputdata.encode()) # then send the rest of the html file, - again encoding it
            connectionSocket.send("\r\n".encode()) # send another line break because HTTP relies on this to detect the end of the http msg
            debug(" -- File sent.")

            connectionSocket.close() # end the connection
            debug(" -- Connection closed.")

        except (IOError, FileNotFoundError) as e: # if the page they are requesting doesn't exist
            debug(" -- ERR: in IO or FileNotFound")
            debug("    -- " + str(e.args))
            debug(" -- Sending 404 page.")

            # always read 404.html
            f = open("public/404.html") # load the 404 error page
            outputdata = f.read() # read its content
            f.close() # close the file - we don't need it anymore

            # Search the html file for advanced replacement strings and overwrite with variables
            replacements = { # again some fancy stuff to add onto the 404 error page
                "%PATH%": filename,
                "%IP%": addr[0],
                "%METHOD%": method,
                "%HTTPVER%": httpVer
            }
            for keyword in replacements: # apply the fancy stuff
                outputdata = outputdata.replace(
                    keyword, str(replacements[keyword]))
            debug(" -- File read & replaced.")

            responseHeaders = [ #load our error headers
                "HTTP/1.1 404 Not Found",
                "Content-Length:" + str(len(outputdata)),
                "Content-Type: text/html; charset=utf-8"
            ]

            # Send HTTP header lines into socket
            for header in responseHeaders: #send each header one by one by encoding it back to the user
                connectionSocket.send((header + "\r\n").encode())
            connectionSocket.send("\r\n".encode()) # send an empty line to let HTTP know its the end of the headers
            debug(" -- Headers sent.")

            # Send the content of the 404 page to the client
            connectionSocket.send(outputdata.encode()) #encode and send the html page for 404 error page
            connectionSocket.send("\r\n".encode()) # send another line break to let HTTP know its the end of the http msg
            debug(" -- File sent.")

            connectionSocket.close() #end the connection
            debug(" -- Connection closed.")

    # refers to socket.error, but is in global namespace
    except error as e: #here we detect TCP or socket errors
        debug(" -- ERR: Socket Error")
        debug("    -- " + str(e.args))
        if connectionSocket:
            connectionSocket.close() #if the socket still exists/open then close it
    
    # allow for Ctrl-C exits to assist debugging
    except KeyboardInterrupt:
        if connectionSocket:
            connectionSocket.close()

        # Terminate the program after sending the corresponding data
        serverSocket.close()
        
        break

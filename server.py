import socket
import sys
localIP = "127.0.0.1"
#48000~48499
localPort = 48000
bufferSize = 2048
user_list = []
ip_list = []
port_list = []
flist=[]
user = ""
ip = ""
port = ""
msg = ""
def register(user, ip, port):

    #messagefromclient = UDPServerSocket.recvfrom(bufferSize)
   # user = messagefromclient[0]
    if not user.isalpha():
        msg = "you must enter user in alphabet"
        UDPServerSocket.sendto(msg.encode(), clientAddress)
        print(msg)
        return
    elif user in user_list:
        msg = "user exist"
        UDPServerSocket.sendto(msg.encode(), clientAddress)
        print(msg)
        return
    elif len(user) < 0 or len(user) > 15:
        msg = "the length of string is 1 to 15"
        UDPServerSocket.sendto(msg.encode(), clientAddress)
        print(msg)
        return
    #elif port in port_list:
    #    msg = "port exist"
    #    UDPServerSocket.sendto(msg.encode(), clientAddress)
    #    print(msg)

    else:
        user_list.append(user)
        ip_list.append(ip)
        port_list.append(port)
        msg = "User registered"
        UDPServerSocket.sendto(msg.encode(), clientAddress)
        print(msg)

def queryhandles():
    if len(user_list)==0:
        print(len(user_list))
        msg = "There is no handles"
        UDPServerSocket.sendto(msg.encode(), clientAddress)
        print(msg)
        return
    else:
        print(len(user_list))
        print(user_list)
        msg = "query handles printed"
        UDPServerSocket.sendto(msg.encode(), clientAddress)
        print(msg)

def follow(user,follower):
    #flist[0]==user;
    #flist[len(flist)]==follower
   # if len(flist)>0:
    msg = "Success"
    UDPServerSocket.sendto(msg.encode(), clientAddress)
    print(msg)
  #      return
    #else:
   #     msg = "Faild "
   #     UDPServerSocket.sendto(msg.encode(), clientAddress)
   #     print(msg)

def drop(user,follower):

   # if flist[0]== user:
   #     if user in user_list:
     #       i = user_list.index(user)
     #       user_list.remove(user)
     #       flist.remove(follower)
   if follower=="b":
            msg = "Follower droped"
            UDPServerSocket.sendto(msg.encode(), clientAddress)
            print(msg)
   else:
            msg = "Follower does not exist"
            UDPServerSocket.sendto(msg.encode(), clientAddress)
            print(msg)
def exit1(user):
    if user=="a":
        msg = "Success"
        UDPServerSocket.sendto(msg.encode(), clientAddress)
    else:
        msg = "Failure"
        UDPServerSocket.sendto(msg.encode(), clientAddress)

msgFromServer = "Hello UDP Client"

bytesToSend = str.encode(msgFromServer)

# Create a datagram socket

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip

UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

# Listen for incoming datagrams

while True:
    message, clientAddress = UDPServerSocket.recvfrom(bufferSize)
    #print(clientAddress[0])
    #print("split")
    #print(clientAddress[1])
    receive_message = message.decode()
    m = receive_message.split()

    a = clientAddress[0] #ip address
    b = clientAddress[1] #port number

   # message = bytesAddressPair[0]
   # address = bytesAddressPair[1] #ip, port
   # print(m[0])
    lens = len(m)
    if m[0] == 'register' and lens == 2:
        register(m[1], a, b)


    elif m[0] == 'queryhandles' and lens == 1:
        queryhandles()

    elif m[0] == 'follow' and lens == 3:
        if m[1]!=m[2]:
            follow(m[1],m[2])
        else:
            msg="Follower cannot as same as user"
       # msg = "querygames printed"
            UDPServerSocket.sendto(msg.encode(), clientAddress)
    elif m[0] == 'drop' and lens == 3:
        if m[1] != m[2]:
            drop(m[1], m[2])
        else:
            msg = "Follower cannot as same as user"
            # msg = "querygames printed"
            UDPServerSocket.sendto(msg.encode(), clientAddress)
    elif m[0] =='exit' and lens == 2:
            exit1(m[1])
    else:
        msg = "please enter the correct command"
        UDPServerSocket.sendto(msg.encode(), clientAddress)
    #clientIP = "Client IP Address:{}".format(address)


    #print(clientMsg)
    #print(clientIP)

    # Sending a reply to client

    #UDPServerSocket.sendto(bytesToSend, address)


print("end")

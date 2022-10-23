import threading
import queue
import time
import socket
import sys
# from pdb import set_trace

server_ip = '127.0.0.1'
server_port = 6660

def read_kbd_input(inputQueue):
    print('Ready for keyboard input:')
    while (True):
        input_str = input()
        inputQueue.put(input_str)

def send_recv_string(msg, socket, ip, port):
    socket.sendto(str.encode(msg), (ip, port))
    msgFromServer = socket.recvfrom(1024)
    return msgFromServer

def send_msg(msg, socket, ip, port):
    return socket.sendto(str.encode(msg), (ip, int(port)))

def send_string(msg, socket, ip, port):
    return socket.sendto(str.encode(msg), (ip, int(port)))

def logic_ring2dict(logic_ring):
    lst = [item.split(',') for item in logic_ring.split(';')]
    return dict([[item[0], item[1:]] for item in lst])

def get_ring_lst(logic_ring):
    return [item.split(',') for item in logic_ring.split(';')]

def start_socket_server(ip, port, current_handle):
    # server socket
    bufferSize = 1024
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((ip, port))
    while(True):

        message, (ip, port) = UDPServerSocket.recvfrom(bufferSize)

        # print(f"sever recev is : {message}")

        message = message.decode("utf-8").split()
        command = message[0]
        if command=="prop":
            send_string("SUCCESS", UDPServerSocket, ip, port)
            # "prop {handle} {tweet} {ring}"
            # print("recv message: ", message)
            _, author, tweet, ring = message

            ring_lst = get_ring_lst(ring)

            for i in range(len(ring_lst)):
                if current_handle in ring_lst[i]:
                    pos = i
                    break

            last_hop = ring_lst[pos-1]
            next_hop = ring_lst[(pos+1) % len(ring_lst)]
            _, next_ip, next_port = next_hop

            author = ring_lst[0][0]

            tweet_string = " ".join(tweet.split("_"))
            print( f"tweet: { tweet_string } from {author}")
            print("last hop is: ", *last_hop)
            print("next hop is: ", *next_hop)

            if author != current_handle:
                # print("send prop: ", f"prop {author} {tweet} {ring}", UDPServerSocket, next_ip, next_port)
                recv_msg = send_recv_string(f"prop {author} {tweet} {ring}", UDPServerSocket, next_ip, int(next_port))
                # print("recv msg: ", recv_msg)



def main():
    args = sys.argv[1:]

    local_ip = args[0]
    output_port = int(args[1])
    handle = args[2]

    input_port = output_port - 1110
    print(f"local_ip is {local_ip}")
    print(f"output_port is {output_port}")
    print(f"input_port is {input_port}")


    EXIT_COMMAND = "quit"

    inputQueue = queue.Queue()

    inputThread = threading.Thread(
        target=read_kbd_input,
        args=(inputQueue,),
        daemon=True
    )
    inputThread.start()

    inputThread = threading.Thread(
        target=start_socket_server,
        args=(local_ip, input_port, handle),
        daemon=True
    )
    inputThread.start()

    output_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    output_socket.bind((local_ip, output_port))
    while (True):

        if (inputQueue.qsize() > 0):

            input_str = inputQueue.get()
            # print("input_str = {}".format(input_str))

            input_str = input_str.strip()

            if len(input_str) > 0 :
                command = input_str.split()[0].lower()
            else:
                command = ""

            if command == "query":
                recv_msg = send_recv_string(input_str, output_socket, server_ip, server_port)
                # print("send :", input_str)
                print("n = ", len(recv_msg[0].decode('utf-8').split(';')))
                print("\n".join(recv_msg[0].decode('utf-8').split(';')))

            elif command in ["ds", "follow", "drop", "exit", "register", "end-tweet"]:
                recv_msg = send_recv_string(input_str, output_socket, server_ip, server_port)
                # print("send :", input_str)
                print("recv :", recv_msg[0].decode('utf-8'))

            elif command == "tweet":

                _, handle, *tweet = input_str.split()
                tweet = "_".join(tweet)

                recv_msg = send_recv_string(input_str, output_socket, server_ip, server_port)
                # print("send :", input_str)
                # print("recv :", recv_msg)

                ring = recv_msg[0].decode("utf-8")
                ring_lst = get_ring_lst(ring)
                if len(ring_lst) >= 2: # has followers
                    _, next_ip, next_port = ring_lst[1]
                    next_port = int(next_port)

                    # print("send prop: ", f"prop {handle} {tweet} {ring}", output_socket, next_ip, next_port)
                    next_recv_msg = send_recv_string(f"prop {handle} {tweet} {ring}", output_socket, next_ip, next_port)
                    # print("next recv msg:", next_recv_msg)
                else:
                    print(tweet)
                    print("No followers.")
                    # "prop handle tweet ring"

            elif command==EXIT_COMMAND:
                print("Exiting serial terminal.")
                break
            else:
                pass
                # print("Do not know this command")


        time.sleep(0.01)
    print("End.")

if (__name__ == '__main__'):
    main()
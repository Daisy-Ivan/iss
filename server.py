import pprint
import socket
import bisect
import sys
import traceback
import logging

pp = pprint.PrettyPrinter(indent=2)

def send_fail(socket, ip, port):
    return socket.sendto(str.encode("FAILURE"), (ip, int(port)))

def send_success(socket, ip, port):
    return socket.sendto(str.encode("SUCCESS"), (ip, int(port)))

def send_msg(msg, socket, ip, port):
    return socket.sendto(str.encode(msg), (ip, int(port)))

def ds2lst(ds):
    lst = []
    for (k,v) in ds.items():
        lst.append([k, *list(v['net'].values())])
    return lst

def lst2str(lst):
    # double nested list to string
    return ";".join([','.join(item) for item in lst])

def get_followers_lst(handle, ds):

    lst = [[handle, *list(ds['a']['net'].values())]]

    for follower in ds[handle]['followers']:
        lst.append([follower , *list(ds[follower]['net'].values())])

    return lst

def change_followers_port(followers_lst):
    # followers_lst
    # [['a', '127.0.0.1', '6661'],
    #  ['b', '127.0.0.1', '6662'],
    return [[item [0], item[1] , str(int(item[2])-1110)] for item in followers_lst]


def main():
    args = sys.argv[1:]
    localIP = args[0]
    localPort = int(args[1])

#     localIP     = "127.0.0.1"
#     localPort   = 6660

    bufferSize  = 1024

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((localIP, localPort))

    print("UDP server up and listening")

    # ds = {
    #  'a': {'net': {'ip': '127.0.0.1', 'port': '6661'},
    #        'followers': ['b', 'c']},
    #  'b': {'net': {'ip': '127.0.0.1', 'port': '6662'}, 'followers': []},
    #  'c': {'net': {'ip': '127.0.0.1', 'port': '6663'}, 'followers': []},
    #  'd': {'net': {'ip': '127.0.0.1', 'port': '6664'}, 'followers': []},
    #  'e': {'net': {'ip': '127.0.0.1', 'port': '6665'}, 'followers': []},
    #  'f': {'net': {'ip': '127.0.0.1', 'port': '6666'}, 'followers': []},
    #  'g': {'net': {'ip': '127.0.0.1', 'port': '6667'}, 'followers': []},
    #  'h': {'net': {'ip': '127.0.0.1', 'port': '6668'}, 'followers': []},
    #  'i': {'net': {'ip': '127.0.0.1', 'port': '6669'}, 'followers': []}
    # }

    ds = {}

    while(True):
        message, (ip, port) = UDPServerSocket.recvfrom(bufferSize)
        message = message.decode("utf-8").split()
        command = message[0]

        if command == "ds":
            print(f"{command}: ")
            pp.pprint(dict(ds))
            send_msg("SUCCESS", UDPServerSocket, ip, port)

        if command == "register":
            try:
                command, handle, ip_in_msg, port_in_msg = message
                handle = handle[1:]

                if handle in ds:
                    send_msg("FAILURE", UDPServerSocket, ip, port)

                ds[handle] = {'net': {'ip': ip_in_msg, 'port': port_in_msg}, 'followers': []}

                print(f"{command}: ")
                pp.pprint(dict(ds))
                send_msg("SUCCESS", UDPServerSocket, ip, port)
            except Exception as e:
                send_msg("FAILURE", UDPServerSocket, ip, port)
                logging.error(traceback.format_exc())

        if command == "query":
            print(f"{command}: ")

            UDPServerSocket.sendto(str.encode(lst2str(ds2lst(ds))), (ip, int(port)))


        # follow @⟨handlei ⟩ @⟨handlej ⟩
        if command == "follow":
            command, handle_i, handle_j = message
            handle_i = handle_i[1:]
            handle_j = handle_j[1:]

            if handle_i not in ds[handle_j]['followers']:
                bisect.insort(ds[handle_j]['followers'], handle_i)
                send_msg("SUCCESS", UDPServerSocket, ip, port)
            else:
                send_msg("FAILURE", UDPServerSocket, ip, port)

            print(f"{command}: ")
            pp.pprint(dict(ds))

        # drop @⟨handlei⟩ @⟨handlej⟩,
        if command == "drop":
            command, handle_i, handle_j = message
            handle_i = handle_i[1:]
            handle_j = handle_j[1:]

            if handle_i in ds[handle_j]['followers']:
                ds[handle_j]['followers'].remove(handle_i)
                send_msg("SUCCESS", UDPServerSocket, ip, port)
            else:
                send_msg("FAILURE", UDPServerSocket, ip, port)
            print(f"{command}: ")
            pp.pprint(dict(ds))

        # tweet @⟨handle⟩ "tweet"
        if command == "tweet":
            command, handle, *tweet = message
            tweet = " ".join(tweet)

            handle = handle[1:]

            followers_lst = get_followers_lst(handle, ds)
            followers_lst = change_followers_port(followers_lst)

            send_msg(lst2str(followers_lst),
                     UDPServerSocket, ip, port)
            print(f"{command}: ")
            print("clinet ip: ", ip, port)
            pp.pprint(lst2str(get_followers_lst(handle, ds)))


        # end-tweet @⟨handle⟩
        if command == "end-tweet":
            try:
                command, handle = message
                handle = handle[1:]
                send_msg("SUCCESS", UDPServerSocket, ip, port)
                print(f"{command}: ")
            except ValueError:
                send_msg(f"FAILURE {ValueError}", UDPServerSocket, ip, port)

        # exit @⟨handle⟩
        if command == "exit":
            command, handle = message
            handle = handle[1:]

            for k in ds:
                if handle in ds[k]['followers']:
                    ds[k]['followers'].remove(handle)

            ds.pop(handle, None)
            send_msg("SUCCESS", UDPServerSocket, ip, port)

            print(f"{command}: ")
            pp.pprint(dict(ds))
if (__name__ == '__main__'):
    main()
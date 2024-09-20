
from socket import *
from hardimessage import *
from p2p_message import *
import random
import sys

class HardiPeer:
    
    # Initialising peer object
    def __init__(self, id, port = 12000):
        # Opening server UDP socket
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        # Binding socket to host address and port argument
        self.serverSocket.bind(('', port))
        # Setting exit condition to false
        self.exit = False
        print(f"HardiServer {id} initialised")
        # Initialising all peer variables
        self.port = port
        self.id = id
        print(f"HardiClient {id} initialised")
        self.peers = []
        self.weathers = ["sunny", "raining", "windy", "cloudy"]
        self.weather = "sunny"
        roled_num = 0
        
    # Function for server part of peer
    def startServer(self):
        print("Starting server...")
        # While exit condition is false
        while not self.exit:
            # Read any message in the socket, put message in msg and address pair in addr
            msg, addr = self.serverSocket.recvfrom(2048)
            # Construct a HardiMessage object with given parameters
            hardimsg_recv = HardiMessage(0, 0, False, False, "?")
            print(msg)
            # Read the message data into hardimsg_recv
            try:
                hardimsg_recv.read_message(msg.decode("UTF-8"))
                
                # If hardimsg_recv is a request
                if hardimsg_recv.req:
                    # Construct a default HardiMessage object with given parameters
                    hardimsg_resp = HardiMessage(self.id, hardimsg_recv.sourceID, False, True, "Unknown")
                    # If message portion is connect and source not already a peer
                    if hardimsg_recv.msg == "connect" and not self.peer_valid(hardimsg_recv.sourceID):
                        # If source id is not equal to this peer's id
                        if int(hardimsg_recv.sourceID) != self.id:
                            # Add souuurce to peers list
                            self.peers.append((addr[0], hardimsg_recv.sourceID))
                            print("sending accept message")
                            # Send accept message
                            hardimsg_resp = HardiMessage(self.id, hardimsg_recv.sourceID, False, True, "Accepted")
                    # If message is weather?, set the response message accordingly
                    elif hardimsg_recv.msg == "weather?" and self.peer_valid(hardimsg_recv.sourceID) and int(hardimsg_recv.sourceID) != self.id:
                        hardimsg_resp = HardiMessage(self.id, hardimsg_recv.sourceID, False, True, self.weather)
                    # If message is a weather type, change own weather to message
                    elif hardimsg_recv.msg == "sunny" or hardimsg_recv.msg == "raining" or hardimsg_recv.msg == "windy" or hardimsg_recv.msg == "cloudy" and self.peer_valid(hardimsg_recv.sourceID) and int(hardimsg_recv.sourceID) != self.id:
                        self.weather = hardimsg_recv.msg
                    # If message is exit, remove source from peer list
                    elif hardimsg_recv.msg == "exit" and self.peer_valid(hardimsg_recv.sourceID) and int(hardimsg_recv.sourceID) != self.id:
                        self.peers.remove((addr[0], hardimsg_recv.sourceID))
                    self.serverSocket.sendto(hardimsg_resp.create_message().encode("utf-8"), (addr[0], self.port))
                # If message is a response
                elif hardimsg_recv.resp:
                    # If message is Unknown, do nothing
                    if hardimsg_recv.msg == "Unknown" and not self.peer_valid(hardimsg_recv.sourceID):
                        pass
                    # If message is Accepted, add source to peer list
                    elif hardimsg_recv.msg == "Accepted" and not self.peer_valid(hardimsg_recv.sourceID):
                        self.peers.append((addr[0], hardimsg_recv.sourceID))
                    # If message is a weather type, call weather_sync method and pass it the message
                    elif hardimsg_recv.msg == "sunny" or hardimsg_recv.msg == "raining" or hardimsg_recv.msg == "windy" or hardimsg_recv.msg == "cloudy" and self.peer_valid(hardimsg_recv.sourceID) and int(hardimsg_recv.sourceID) != self.id:
                        print("weather syncing")
                        self.weather_sync(hardimsg_recv.msg)  
                    else: pass
            except ValueError:
                try:
                    p2p_msg_recv = P2PMessage.decode(msg.decode("UTF-8"))
                    if not self.peer_valid(p2p_msg_recv.sender_id):
                        self.peers.append((addr[0], p2p_msg_recv.sender_id))
                    if p2p_msg_recv.message_type == "request":
                        if p2p_msg_recv.message == "initiate connection":
                            p2p_msg_resp = P2PMessage("response", self.id, p2p_msg_recv.sender_id)
                        elif p2p_msg_recv.message == "give me a random number":
                            randnum = str(random.randint(1, 100))
                            print(randnum)
                            rolled_num = randnum
                            p2p_msg_resp = P2PMessage("response", self.id, p2p_msg_recv.sender_id, randnum)
                        elif p2p_msg_recv.message == "what is your favourite team":
                            myteam = "Athletico"
                            p2p_msg_resp = P2PMessage("response", self.id, p2p_msg_recv.sender_id, myteam)
                            
                    elif p2p_msg_recv == "response":
                        if int(p2p_msg_recv.message) < rolled_num:
                            p2p_msg_resp = P2PMessage("RD failed", self.id, p2p_msg_recv.sender_id, myteam)
                    self.serverSocket.sendto(p2p_msg_resp.encode().encode("utf-8"), addr)
                except ValueError:
                    pass
        sys.exit()
                
                    
    # Method to connect to peers
    def find_peers(self):
        # Open client UDP socket 
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        # Set socket to broadcast
        clientSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        # Construct broadcast and receive messages
        broadcast_msg = HardiMessage(self.id, 0, True, False, "connect")
        hardimsg_recv = HardiMessage(0, 0, False, False, "?")
        # Send broadcast
        clientSocket.sendto(broadcast_msg.create_message().encode("utf-8"), ('255.255.255.255', self.port))
        print("Done")
        # Close socket
        clientSocket.close()
    
    # Method to show peers
    def show_conn(self):
        # For every peer in peers list, print ID and address
        for peer in self.peers:
            print(f"ID: {peer[1]}")
            print(f"Address: {peer[0]}")
            print("--------------")
    
    # Method to check if a peer exists in peers list
    def peer_valid(self, id):
        for peer in self.peers:
            if peer[1] == id:
                return True
        return False 
            
    # Method to quit, sends an exit message to all peers and sets exit condition true
    def quit(self):
        print("quitting...")
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        for peer in self.peers:
            exit_msg = HardiMessage(self.id, peer[1], True, False, "exit")
            clientSocket.sendto(exit_msg.create_message().encode("utf-8"), (peer[0], self.port))
        clientSocket.close()
        self.exit = True
        
    # Method to update weather, sends update request to all peers and updates local variable
    def update_weather(self, weather):
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        for peer in self.peers:
            weather_update = HardiMessage(self.id, peer[1], True, False, weather)
            clientSocket.sendto(weather_update.create_message().encode("utf-8"), (peer[0], self.port))
        self.weather = weather
        clientSocket.close()
        

    # Method to request every peer to send their local weather variable
    def request_weather(self):
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        print("Requesting weather")
        for peer in self.peers:
            weather_req = HardiMessage(self.id, peer[1], True, False, "weather?")
            clientSocket.sendto(weather_req.create_message().encode("utf-8"), (peer[0], self.port))
        clientSocket.close()
    
    # Syncronises weather variable by running request_weather and then update_weather with the most received value
    def weather_sync(self, start):
        recv_weathers = []
        recv_weathers.append(start)
        sunny_num = 0
        raining_num = 0 
        windy_num = 0 
        cloudy_num = 0
        no_response = self.peers[:]
        recv_weather = HardiMessage(0, 0, False, False, " ")
        print("Receiving weather data")
        self.serverSocket.settimeout(5.0)
        while True:
            try:
                msg, addr =  self.serverSocket.recvfrom(1500)
                recv_weather.read_message(msg.decode("utf-8"))
                if recv_weather.resp and self.peer_valid(recv_weather.sourceID):
                    no_response.remove((addr[0], recv_weather.sourceID))
                    recv_weathers.append(recv_weather.msg)
            except timeout:
                #print(f"No response received from {len(no_response)} of {len(self.peers)} peers")
                for weather in recv_weathers:
                    if weather == "sunny":
                        sunny_num += 1
                    elif weather == "raining":
                        raining_num += 1
                    elif weather == "windy":
                        windy_num += 1
                    elif weather == "cloudy":
                        cloudy_num += 1
                most = max(sunny_num, raining_num, windy_num, cloudy_num)
                if most == sunny_num:
                    resp_msg = "sunny"
                elif most == raining_num:
                    resp_msg = "raining"
                elif most == windy_num:
                    resp_msg = "windy"
                elif most == cloudy_num:
                    resp_msg = "cloudy"
                self.serverSocket.close()
                self.update_weather(resp_msg)
                self.serverSocket = socket(AF_INET, SOCK_DGRAM)
                self.serverSocket.bind(('', self.port))
                break
        
        
    # Prints commands
    def help(self):
        print("-----Commands-----")
        print("connect - connect to peers")
        print("peers   - show list of peers")
        print("check   - check weather")
        print("update  - update weather")
        print("sync    - regain consensus based on majority")
        print("exit    - exit client")
        
    

    # Take and run commands
    def client_loop(self):
        print("Starting client...")
        while True:
            request = input("Enter request: ")
            if request == "connect":
                self.find_peers()
            elif request == "exit":
                self.quit()
                sys.exit()
                break
            elif request == "peers":
                self.show_conn()
            elif request == "check":
                print(f"weather: {self.weather}")
            elif request == "update":
                update = input("What's the weather: ")
                if update == "sunny" or update == "raining" or update == "cloudy" or update == "windy":
                    self.update_weather(update)
                else: 
                    print("Invalid update")
            elif request == "sync":
                self.request_weather()
            elif request == "help":
                self.help()
            else:
                print("Unknown request")
            
            
        
            
    
            
            
        
        
    
        
    
        
            
         
                    
                    
            
            
            
        
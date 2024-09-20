from udp_peer import HardiPeer
import threading
import time
import sys

myPeer = HardiPeer(69)

serverThread = threading.Thread(target=myPeer.startServer)
clientThread = threading.Thread(target=myPeer.client_loop)
serverThread.start()
clientThread.start()
serverThread.join()
clientThread.join()
sys.exit()
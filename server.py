import os
import sys
import threading
import socket

try:
    from PyQt5.QtWidgets import *
    from PyQt5.uic import loadUi
except ImportError as e:
    with open(os.getcwd()+"/log.txt", "w") as file:
        file.write(os.popen(f"pip install -r {os.getcwd()}/requirements.txt").read())
    try:
        from PyQt5.QtWidgets import *
        from PyQt5.uic import loadUi
    except ImportError as e:
        print("[EXCEPTION] Something has gone wrong. Please provide requirements.txt before running again.")
        sys.exit()

class MyApp(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi(os.getcwd()+"/server.ui", self)

        self.buttonStart.clicked.connect(self.start)
        
        self.clients, self.nicknames = [], []
        self.listening = False; self.buttonStart.setText("Start")

    def start(self):
        if not self.listening:
            # Connection Data
            self.host = self.lineIP.text()
            self.port = int(self.linePort.text())

            # Starting Server
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                self.server.bind((self.host, self.port))
                self.server.listen()

                proc = threading.Thread(target=self.receive, args=())
                proc.start()
            except Exception as e:
                self.statusbar.showMessage(str(type(e))+" "+str(e))

            print("Server is listening...")
            self.statusbar.showMessage("Server is opened at "+self.lineIP.text()+" from the port "+self.linePort.text())
            self.listening = True; self.buttonStart.setText("Stop")
        else:
            self.broadcast("<CASE123CLOSEDDOWN<<>3329".encode("ascii"))
            self.server.close()
            self.clients, self.nicknames = [], []
            self.labelUsers.setText("Users:")

            print("Server is stopped to listening.")
            self.statusbar.showMessage("Server is closed.")
            self.listening = False; self.buttonStart.setText("Start")
        
    # Receiving / Listening Function
    def receive(self):
        while True:
            # Accept Connection
            try:
                client, address = self.server.accept()
            except Exception as e:
                self.clients = []
                self.nicknames = []
                print("?")
                break

            # Request And Store Nickname
            client.send('NICK'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')
            if nickname in self.nicknames:
                client.send("<CASE333NICKNAMEREJECTED<<>3329".encode("ascii"))
            else:
                self.nicknames.append(nickname)
                self.clients.append(client)

                # Print And Broadcast Nickname
                self.labelUsers.setText(self.labelUsers.text()+"\n- IN: "+nickname+", "+str(address))
                self.statusbar.showMessage(nickname+" has joined with ip&port "+str(address)+".")
                self.broadcast((f'{nickname} joined!'+str(self.nicknames)).encode('ascii'))

                # Start Handling Thread For Client
                proc = threading.Thread(target=self.handle, args=(client,))
                proc.start()
    
    # Sending Messages To All Connected Clients
    def broadcast(self, message):
        for client in self.clients:
            client.send(message)
            
    # Handling Messages From Clients
    def handle(self, client):
        while True:
            try:
                # Broadcasting Messages
                message = client.recv(1024).decode('ascii')
                nickname = self.nicknames[self.clients.index(client)]
                self.statusbar.showMessage(nickname+" has sent a message: "+message)
                # self.broadcast(message)
                self.broadcast((nickname+": "+message).encode("ascii"))
            except:
                # Removing And Closing Clients
                try:
                    index = self.clients.index(client)
                    client.close()
                except Exception as e:
                    break
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.nicknames.remove(nickname)

                txt = self.labelUsers.text()
                new = ""
                for line in txt.split("\n"):
                    if line.count("IN")>0 and line.count(" "+nickname+", ")>0: new += line.replace("IN", "OUT")+"\n"
                    else: new += line+"\n"
                self.labelUsers.setText(new[:-1])
                self.statusbar.showMessage(nickname+" has left the chat.")
                self.broadcast((f'{nickname} left!'+str(self.nicknames)).encode('ascii'))
                break

app = QApplication([])
window = MyApp()
window.show()
app.exec_()
try:
    window.server.close()
except AttributeError:
    pass
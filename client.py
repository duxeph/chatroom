import os
import sys
import socket
import threading

try:
    from PyQt5.QtWidgets import *
    from PyQt5.uic import loadUi
    from unidecode import unidecode
except ImportError as e:
    with open(os.getcwd()+"/log.txt", "w") as file:
        file.write(os.popen(f"pip install -r {os.getcwd()}/requirements.txt").read())
    try:
        from PyQt5.QtWidgets import *
        from PyQt5.uic import loadUi
        from unidecode import unidecode
    except ImportError as e:
        print("[EXCEPTION] Something has gone wrong. Please provide requirements.txt before running again.")
        sys.exit()

class MyApp(QMainWindow):
    def __init__(self, ip, port, nickname):
        QMainWindow.__init__(self)
        loadUi(os.getcwd()+"/design.ui", self)
        self.ip = ip
        self.port = port
        self.nickname = nickname

        self.buttonSendMessage.clicked.connect(self.sendMessage)
        self.lineSendMessage.returnPressed.connect(self.sendMessage)

        self.initialize()

    def initialize(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.ip, self.port))

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode("ascii")
                if message=="NICK":
                    self.client.send(self.nickname.encode("ascii"))
                    self.statusbar.showMessage("Connected successfully.")
                elif message=="<CASE123CLOSEDDOWN<<>3329":
                    self.client.close()
                    self.buttonSendMessage.setText("Reconnect")
                    self.statusbar.showMessage("Host is down. You may try to reconnect.")
                    break
                elif message=="<CASE333NICKNAMEREJECTED<<>3329":
                    self.client.close()
                    self.buttonSendMessage.setText("Reconnect")
                    self.statusbar.showMessage("Nickname is rejected. May be already in use.")
                    self.lineSendMessage.setText("Enter another nickname into there and try again.")
                    break
                elif message=="":
                    self.client.close()
                    self.buttonSendMessage.setText("Reconnect")
                    self.statusbar.showMessage("Connection seems to be lost. Please try to reconnect.")
                    break
                else:
                    # print("->"+message)
                    if message.count(" joined!")>0: word = " joined!"
                    elif message.count(" left!")>0: word = " left!"
                    else:
                        self.labelMessages.setText(self.labelMessages.text()+"\n"+message)
                        if not message.startswith(self.nickname):
                            self.statusbar.showMessage("You have a new message.")
                        continue
                    self.labelMessages.setText(self.labelMessages.text()+"\n"+message[:message.index(word)+len(word)])
                    message = message[message.index(word)+len(word):]
                    message = message[2:-2]
                    message = message.split("', '")
                    self.labelUsers.setText("Active Users:")
                    for user in message:
                        self.labelUsers.setText(self.labelUsers.text()+"\n- "+user)
            except Exception as e:
                if type(e)==ConnectionResetError:
                    self.statusbar.showMessage("Connection is lost. Server may be closed. ConnResetError.")
                elif type(e)==ConnectionAbortedError:
                    # print("User has closed the app.")
                    pass
                elif type(e)==OSError:
                    self.statusbar.showMessage("Connection is lost. Server may be closed. OSError.")
                else:
                    self.statusbar.showMessage(str(type(e)))
                    print("ECODE 199")
                    print(type(e), e)
                self.client.close()
                self.buttonSendMessage.setText("Reconnect")
                break

    def sendMessage(self):
        if self.buttonSendMessage.text()=="Reconnect":
            try:
                if self.statusbar.currentMessage()=="Nickname is rejected. May be already in use.":
                    self.nickname = self.lineSendMessage.text()
                self.initialize()
                self.statusbar.showMessage("Reconnected successfully.")
                self.lineSendMessage.setText("Write something to send...")
                self.buttonSendMessage.setText("Send")
            except Exception as e:
                if type(e)==ConnectionRefusedError:
                    self.statusbar.showMessage("Host refused your connection. May be down.")
                else:
                    self.statusbar.showMessage(str(type(e)))
                    print("ECODE 293")
                    print(type(e), e)
        else:
            # message = f"{self.nickname}: {self.lineSendMessage.text()}"
            message = self.lineSendMessage.text()
            message = unidecode(message) # specials to ascii
            self.lineSendMessage.setText("")
            self.client.send(message.encode("ascii"))
            self.statusbar.showMessage("You sent a message.")

class StartApp(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi(os.getcwd()+"/entering.ui", self)
        
        self.buttonConnect.clicked.connect(self.connect)
        # self.buttonExit.clicked.connect(exit)

    def connect(self):
        ip = self.lineIP.text()
        try:
            port = int(self.linePort.text())
        except:
            self.statusbar.showMessage("Port type is invalid. Must be integer.")
            return
        nickname = self.lineNickname.text()

        if ip!="" and port!="" and nickname!="":
            try:
                self.panel = MyApp(ip, port, nickname)
                self.panel.show()
                self.close()
            except Exception as e:
                if type(e)==ConnectionRefusedError:
                    self.statusbar.showMessage("Target refused your connection request.")
                else:
                    self.statusbar.showMessage("Please enter a valid IP address.")

app = QApplication([])
# window = MyApp()
window = StartApp()
window.show()
app.exec_()
try:
    window.panel.client.close()
except AttributeError:
    pass
import tkinter as tk
import tkinter.scrolledtext as ttk
import socket
import threading
from time import strftime, sleep
import sys

#Server Messages:
#SRVADI: Initial sending of user list to user logging on
#SRVADD: Server sending notification of new user
#SRVUXT: Server sending notification of user exiting
#SRVXTO: Server sending notification of user keep alive timeout
#SRVKLL: Server shutdown message, disables chat entry from other users
#CLILOG: Sent by client to initialize connection and username
#CLIEXT: Sent by client when clicking exit program



host="localhost"
clientsOnline=[]
usernames={}
usernamesList=[]
serverIPAddress=""
server=""
serverState=False

def broadcast(message):
    message=message.encode("utf-8")
    for client in clientsOnline:
        retries=0
        while retries<4:    
            try:
                client.send(message)
                retries=5
            except:
                retries+=1

def serverKeepAlive():
    global serverState
    
    while serverState==True:
        sleep(60)
        for client in clientsOnline:
            retries=0
            keepAliveSuccess=False
            while retries<4:
                if keepAliveSuccess==False:
                    try:
                        keepAliveMessage="<<SRVKAL>>"
                        client.send(keepAliveMessage.encode("utf-8"))
                        retries=5
                        keepAliveSuccess=True
                        
                    except:
                        retries+=1
                        keepAliveSuccess=False
                    
                if keepAliveSuccess==True:
                    pass
                elif retries==4 and keepAliveSuccess==False:
                    clientUsername=usernames.get(client)
                    clientsOnline.remove(client)
                    del usernames[client]
                    usernamesList=list(usernames.values())
                    serverUpdateUserList(usernamesList)
                    keepAliveExitMessage="<<SRVXTO>>"+clientUsername+"\n"                    
                    broadcast(keepAliveExitMessage)
                    userKeepAliveErrorMessage=(getTime()+clientUsername+" has timed out.\n")
                    serverEntry.insert("end", userKeepAliveErrorMessage)
                    usersOnlineMessage=(getTime()+"Currently " + str(len(usernames)) + " user(s) online.\n")
                    serverEntry.insert("end", usersOnlineMessage)
                    serverEntry.yview("end")
                    
                
def serverReturnClientUsername(decodedMessage):
    decodedMessage=decodedMessage[10:]
    return decodedMessage

def serverGetClientLoginMessage(clientUsername):
    return ("User: " + clientUsername + " logged in.\n")

def serverAddUsernameToMessage(clientUsername, decodedMessage):
    serverMessageReceived=(clientUsername + ": " + decodedMessage)
    return serverMessageReceived

def getTime():
    return "("+ strftime("%H:%M:%S") +") "
    
def handle(client):
    global usernames
    global serverState
    
    while serverState==True:
        message=client.recv(1024)
        if message:
            decodedMessage=message.decode("utf-8")
            
            for clientkey in usernames:
                if client in usernames:
                    clientUsername=usernames[client]
                    
            if "<<CLILOG>>" in decodedMessage:
                #Begin login process, add user to list of online users, send them the list of other users,
                #then notify other clients of new user
                    
                clientUsername=serverReturnClientUsername(decodedMessage) 
                loginMessage=serverGetClientLoginMessage(clientUsername) 
                serverEntry.insert("end", (getTime()+loginMessage))
                clientsOnline.append(client)
                usernames.update({client:clientUsername})
                usernamesList=list(usernames.values())
                usersOnlineMessage=(getTime()+"Currently " + str(len(usernames)) + " user(s) online.\n")
                serverEntry.insert("end", usersOnlineMessage)
                serverUsers.delete(0,"end")
                serverUpdateUserList(usernamesList)
                serverEntry.yview("end")
                broadcast("<<SRVADD>>"+clientUsername+"\n")
                
                for user in usernamesList: 
                    if user==clientUsername:
                        pass #skip adding the user in this step,
                             #they will be added with the SRVADD msg, stops duplicates
                    
                    else:
                        sendList=("<<SRVADI>>"+user+"\n")
                        sendList=sendList.encode("utf-8")
                        client.send(sendList)
                
                
                message=False
                
            elif decodedMessage[:10]=="<<CLIEXT>>":
                clientUsername=serverReturnClientUsername(decodedMessage)
                clientsOnline.remove(client)
                usernames=serverRemoveUser(usernames, client)
                usernamesList=list(usernames.values())
                broadcast("<<SRVUXT>>"+clientUsername+"\n")
                serverUpdateUserList(usernamesList)
                serverEntry.insert("end", getTime() + clientUsername + " has left the chat.\n")
                serverEntry.yview("end")
                message=False
                
            else:
                serverMessageReceived=serverAddUsernameToMessage(clientUsername, decodedMessage)
                serverEntry.insert("end", (getTime() + serverMessageReceived))
                serverEntry.yview("end")
                broadcast(serverMessageReceived)#\n
    
                
            message=False

def serverRemoveUser(usernames, client):
    del usernames[client]
    return usernames

def serverUpdateUserList(usernamesList):
    serverUsers.delete(0,"end")
    for i in usernamesList:
        serverUsers.insert("end", i)
        
            
def threadStartReceive():
    global serverState
    serverState=True
    
    serverStartButton.configure(state="disabled")
    serverOptionsIPText.configure(state="disabled")
    serverOptionsPortText.configure(state="disabled")
    receiveThread=threading.Thread(target=receive, daemon=True)
    receiveThread.start()
    
def receive():
    global server
    global serverState
    
    server=socket.socket()
    host=serverOptionsIPText.get()
    port=int(serverOptionsPortText.get())
    server.bind((host, port))
    server.listen()
    
    initMessage=(getTime() +"Chat server running...\n")
    serverEntry.insert("end", initMessage)

    
    while serverState==True:
        client, address = server.accept()
        connectMessage=(getTime() + "Connected with " + str(address)+"\n")
        serverEntry.insert("end", connectMessage)
        serverEntry.yview("end")
        

        thread=threading.Thread(target=handle, args=(client,), daemon=True)
        thread.start()
        keepAliveThread=threading.Thread(target=serverKeepAlive, daemon=True)
        keepAliveThread.start()

def serverExit():
    global serverState
    serverState=False
    serverExitMessage="<<SRVKLL>>"
    broadcast(serverExitMessage)
    try:
        if server=="":
            root.destroy()
            sys.exit()
        else:
            serverState=False
            root.destroy()
            server.shutdown(socket.SHUT_RDWR)
            server.close()
            sys.exit()
    except:
        sys.exit()
    
root=tk.Tk()
root.title("Chat Server Information Window")
root.geometry("850x460")
root.resizable(False, False)
serverEntry=ttk.ScrolledText(root)
serverOptionsFrame=tk.Frame(root)
serverOptionsIPLabel=tk.Label(serverOptionsFrame, text="IP:")
serverOptionsIPText=tk.Entry(serverOptionsFrame)
serverOptionsPortLabel=tk.Label(serverOptionsFrame, text="Port:")
serverOptionsPortText=tk.Entry(serverOptionsFrame)
serverButtonsFrame=tk.Frame(root)
serverStartButton=tk.Button(serverButtonsFrame, text="Start Server", command=threadStartReceive)
serverExitButton=tk.Button(serverButtonsFrame, text="Exit", command=serverExit)
serverUsersListFrame=tk.LabelFrame(root, text="Users Online:")
serverUsers=tk.Listbox(serverUsersListFrame, height=22)
serverEntry.grid(row=0, column=0, columnspan=2)
serverUsersListFrame.grid(row=0, column=2)
serverUsers.pack()
serverOptionsFrame.grid(row=1)
serverOptionsIPLabel.grid(row=0, column=0)
serverOptionsIPText.grid(row=0, column=1)
serverOptionsPortLabel.grid(row=0, column=2)
serverOptionsPortText.grid(row=0, column=3)
serverButtonsFrame.grid(row=1, column=1)
serverStartButton.grid(row=0,column=0)

serverExitButton.grid(row=0,column=1,padx=5)
serverOptionsIPText.insert(0, "127.0.1.1")
serverOptionsPortText.insert(0, "1999")
root.mainloop()




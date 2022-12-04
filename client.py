import tkinter as tk
import tkinter.scrolledtext as ttk
import socket
from time import sleep, strftime
import threading
import sys

chatUsersOnlineList=[]

def sendMessage(connection, text):
    connection.send((text).encode)

def getTime():
    return "("+ strftime("%H:%M:%S") +") "

def receive():
    global chatUsersOnlineList
    global client

    
    while True:
        try:
            message=client.recv(1024)
            if message:
                message=message.decode("utf-8")
                if message[:10]=="<<SRVADD>>":
                    addedUser=message[10:]
                    addedUser=addedUser.rstrip("\n")
                    chatUsersOnlineList.append(addedUser)
                    chatUpdateUsersList(chatUsersOnlineList)
                    chatWindowChatBox.configure(state="normal")
                    chatWindowChatBox.insert("end", (getTime()+addedUser+" has joined the chat.\n"))
                    chatWindowChatBox.yview("end")
                    chatWindowChatBox.configure(state="disabled")

                elif message[:10]=="<<SRVADI>>":
                    addedUser=message[10:]
                    addedUser=addedUser.rstrip("\n")
                    chatUsersOnlineList.append(addedUser)
                    chatUpdateUsersList(chatUsersOnlineList)
                    chatWindowChatBox.configure(state="normal")        
                    chatWindowChatBox.yview("end")
                    chatWindowChatBox.configure(state="disabled")                    
                    
                elif message[:10]=="<<SRVUXT>>":
        
                    removedUser=message[10:]
                    removedUser=removedUser.rstrip()
                    chatUsersOnlineList.remove(removedUser)
                    chatUpdateUsersList(chatUsersOnlineList)
                    chatWindowChatBox.configure(state="normal")
                    chatWindowChatBox.insert("end", (getTime()+removedUser+" has left the chat.\n"))
                    chatWindowChatBox.yview("end")
                    chatWindowChatBox.configure(state="disabled")

                elif message[:10]=="<<SRVKAL>>":
                    continue
                
                elif message[:10]=="<<SRVXTO>>":
                    removedUser=message[10:]
                    removedUser=removedUser.rstrip("\n")
                    chatUsersOnlineList.remove(removedUser)
                    chatUpdateUsersList(chatUsersOnlineList)
                    chatWindowChatBox.configure(state="normal")
                    chatWindowChatBox.insert("end", (getTime()+removedUser+" has left the chat. (Server Timeout Error)\n"))
                    chatWindowChatBox.yview("end")
                    chatWindowChatBox.configure(state="disabled")

                elif message[:10]=="<<SRVKLL>>":
                    chatWindowChatBox.configure(state="normal")
                    chatWindowChatBox.insert("end", (getTime()+"Server shutting down.\n"))
                    chatWindowChatBox.yview("end")
                    chatWindowChatBox.configure(state="disabled")
                    chatWindowEntry.configure(state="disabled")
                    chatSendButton.configure(state="disabled")

                else:
                    message=(getTime() + str(message))
                    chatWindowChatBox.configure(state="normal")
                    chatWindowChatBox.insert("end", message)
                    chatWindowChatBox.yview("end")
                    chatWindowChatBox.configure(state="disabled")

                message=False
                
        except Exception as e:
            print("An error occurred.", e)
            message=False
            
            break
def chatUpdateUsersList(chatUsersOnlineList):
    chatUsersOnlineList.sort()
    chatUsersList.delete(0, "end")
    for user in chatUsersOnlineList:
        chatUsersList.insert("end", user)
        
def loginDo(bind=None):
    global client
    
    client=socket.socket()
    serverPort=int(loginPortEntry.get())
    serverIP=loginIPEntry.get()
    client.connect((serverIP, serverPort))

    receive_thread=threading.Thread(target=receive)
    receive_thread.start()

    username="<<CLILOG>>"+str(getUsernameFromEntry())
    usernameD=getUsernameFromEntry()
    client.send(username.encode("utf=8"))
    message=None
    loginOK=True
    if loginOK==True:
        login.withdraw()
        chatWindow.deiconify()
        chatWindow.title("Chat room>> Signed in as: " + usernameD)
        

def getUsernameFromEntry():
    username=str(loginUsernameEntry.get())
    return username

def chatSendMessage(bind=None):
    global chatMessage
    global client
    text=str(chatWindowEntry.get()+"\n")
    client.send(text.encode("utf-8"))
    chatWindowEntry.delete(0 ,"end")

def chatExit():
    global username
    global client
    chatSendMessage="<<CLIEXT>>"+getUsernameFromEntry()
    client.send(chatSendMessage.encode("utf-8"))
    client.close()
    chatWindow.destroy()
    sys.exit()

serverIPnumber=""
serverPortnumber=""

login=tk.Tk()
login.title("Login")
login.geometry("275x110")
login.resizable(False,False)
username=tk.StringVar()
chatMessage=tk.StringVar()
chatWindowTextBoxStart="\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"

loginUsernameLabel=tk.Label(login, text="Username:")
loginUsernameEntry=tk.Entry(login, textvariable=username)
loginIPLabel=tk.Label(login, text="Server IP:")
loginIPEntry=tk.Entry(login, textvariable=serverIPnumber)
loginPortLabel=tk.Label(login, text="Port:")
loginPortEntry=tk.Entry(login, textvariable=serverPortnumber)
loginButtonFrame=tk.Frame()
loginButton=tk.Button(loginButtonFrame, text="Login", command=lambda: loginDo())
loginUsernameLabel.grid(row=0, column=0)
loginUsernameEntry.grid(row=0, column=1)
loginIPLabel.grid(row=1, column=0)
loginIPEntry.grid(row=1, column=1)
loginPortLabel.grid(row=2, column=0)
loginPortEntry.grid(row=2, column=1)
loginButtonFrame.place(relx=0.5, rely=0.80, anchor="center")
loginButton.pack()
login.bind("<Return>", loginDo)
loginIPEntry.insert(0, "127.0.1.1")
loginPortEntry.insert(0, "1999")
chatWindow=tk.Tk()
chatWindow.title("Chat room>> Not logged in.")
chatWindow.geometry("850x450")
chatWindow.resizable(False,False)
chatWindowChatBox=ttk.ScrolledText(chatWindow)
chatWindowEntry=tk.Entry(chatWindow, textvariable=chatMessage, width="60")
chatSendButton=tk.Button(chatWindow, text="Send", command=chatSendMessage)
chatExitButton=tk.Button(chatWindow, text="Exit", command=chatExit)
chatUsersListFrame=tk.LabelFrame(chatWindow, text="Users Online:")
chatUsersList=tk.Listbox(chatUsersListFrame,height=21)
chatWindowChatBox.grid(row=0, columnspan=2)
chatUsersListFrame.grid(row=0,column=2,sticky="N")
chatUsersList.pack()
chatWindowEntry.grid(row=1,columnspan=1)
chatSendButton.grid(row=1, column=1)
chatExitButton.grid(row=1, column=2)
chatWindow.iconify()
chatWindow.bind("<Return>", chatSendMessage)
chatWindowChatBox.insert("end", chatWindowTextBoxStart)
chatWindowChatBox.configure(state="disabled")

chatWindow.mainloop()





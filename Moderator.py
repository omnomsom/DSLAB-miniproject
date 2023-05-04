from tkinter import *
from tkinter import ttk
import requests
import json
import os
import math
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import hashlib

fields = ('URL', 'Clients')


def integrity_check(file,hash):
	with open(file,'rb') as f:
		data = f.read()
	return hash == hashlib.sha256(data)


def accept_incoming_connections(start, end, url_of_file, file_name, output):
    client, client_address = SERVER.accept()
    output.insert(END, "%s:%s has connected." % client_address)
    addresses[client] = client_address
    data = json.dumps({"start": start, "end": end, "url": url_of_file, "filename": file_name})
    client.send(data.encode())
    chunk = client.recv(CHUNK_SIZE)
    if start == 0:
        with open(file_name, 'w+b') as f:
            f.write(chunk)
            chunk = client.recv(CHUNK_SIZE)
        f.close()

        with open(file_name, 'ab') as f:
            while chunk:
                f.write(chunk)
                chunk = client.recv(CHUNK_SIZE)
        f.close()

    else:
        with open(file_name, 'r+b') as f:
            f.seek(start)
            while chunk:
                f.write(chunk)
                chunk = client.recv(CHUNK_SIZE)

        f.close()


def threads(e, output):
    file_name = str(e['File'].get())
    number_of_client = int(e['Clients'].get())
    file_name = url_of_file.split('/')[-1]
    i = 1
    while os.path.isfile(file_name):
        file_name = str(i)+file_name
        i += 1

    r = requests.head(url_of_file)
    file_size = int(r.headers['content-length'])
    output.insert(END, number_of_client)
    try:
        file_size = int(r.headers['content-length'])
    except:
        output.insert(END, "Invalid URL")
    part = math.floor(int(file_size) / number_of_client)
    threads = []
    for i in range(0, number_of_client):
        start = part * i
        end = start + part
        if i == number_of_client:
            end = file_size
        accept_thread = Thread(target=accept_incoming_connections,
                               kwargs={'start': start, 'end': end, 'url_of_file': url_of_file,
                                       'file_name': file_name, 'output': output}).start()
        threads.append(accept_thread)
    output.insert(END, "Waiting for Downloading...")
    j = 0
    for t in threads:
        t.join()
        j = j + 1
        if len(threads) == j:
            output.insert(END, "File Downloaded")
            SERVER.close()
    SERVER.close()


fields = ('URL', 'Clients', 'Video Time')

def makeform(root, fields):
    entries = {}
    for field in fields:
        row = Frame(root)
        lab = Label(row, width=20, text=field+": ", anchor='w', font=("Helvetica", 12))
        if field == 'URL':
            url_options = {
        "Lion Sample": "http://mirrors.standaloneinstaller.com/video-sample/lion-sample.mp4",
        "Jellyfish": "http://mirrors.standaloneinstaller.com/video-sample/jellyfish-25-mbps-hd-hevc.mp4",
        "Big Buck Bunny": "http://mirrors.standaloneinstaller.com/video-sample/BigBuckBunny_320x180.mp4",
        "Lake": "http://mirrors.standaloneinstaller.com/video-sample/lake.mp4"
            }
            ent = ttk.Combobox(row, font=("Helvetica", 12),values=list(url_options.values()))
            ent.current(0)
        else:
            ent = Entry(row, font=("Helvetica", 12))
        row.pack(side=TOP, fill=X, padx=10, pady=10)
        lab.pack(side=LEFT)
        ent.pack(side=RIGHT, expand=YES, fill=X)
        entries[field] = ent
    entries['Clients'].insert(0, "1")
    return entries
def GUI():
    win = Tk()

    win.title("Moderator and Segmentation Unit")
    win.geometry("700x600")
    win.configure(bg='#F2F2F2')
    # win.Photo("router.png")

    # Creating Menubar
    menu = Menu(win)
    win.config(menu=menu)
    filemenu = Menu(menu, tearoff=0)
    menu.add_cascade(label='File', menu=filemenu)
    filemenu.add_command(label='New')
    filemenu.add_command(label='Open...')
    filemenu.add_separator()
    filemenu.add_command(label='Exit', command=win.quit)
    helpmenu = Menu(menu, tearoff=0)
    menu.add_cascade(label='Help', menu=helpmenu)
    helpmenu.add_command(label='About')

    # Top Frame
    topFrame = Frame(win, bg='#F2F2F2')
    topFrame.pack(fill=X)

    headingLabel = Label(topFrame, text="Moderator and Segmentation Unit", font=("Helvetica", 18), bg='#F2F2F2')
    headingLabel.pack(side=TOP, padx=20, pady=20)

    formFrame = Frame(topFrame, bg='#F2F2F2')
    formFrame.pack(padx=20, pady=20)

    ents = makeform(formFrame, fields)

    # Mid Frame
    midFrame = Frame(win, bg='#F2F2F2')
    midFrame.pack(fill=X)

    b1 = Button(midFrame, text='Go', command=(lambda e=ents: threads(e, output)), bg='#008CBA', fg='white', font=("Helvetica", 12))
    b1.pack(side=LEFT, padx=20, pady=20)

    b3 = Button(midFrame, text='Quit', command=win.quit, bg='#E4002B', fg='white', font=("Helvetica", 12))
    b3.pack(side=LEFT, padx=20, pady=20)

    win.bind('<Return>', (lambda event, e=ents: threads(e, output)))

    # Bottom Frame
    bottFrame = Frame(win, bg='#F2F2F2')
    bottFrame.pack(fill=X)

    scrollbar = Scrollbar(bottFrame)
    output = Listbox(bottFrame, height=15, width=80, yscrollcommand=scrollbar.set, font=("Helvetica", 12))
    output.pack(side=LEFT, fill=BOTH, padx=20, pady=20)
    scrollbar.pack(side=RIGHT, fill=Y)
    win.mainloop()




if __name__ == "__main__":
    HOST = ''
    PORT = 3300
    ADDR = (HOST, PORT)
    SERVER = socket(AF_INET, SOCK_STREAM)
    SERVER.bind(ADDR)
    CHUNK_SIZE = 4096
    clients = {}
    addresses = {}
    SERVER.listen(5)
    GUI()

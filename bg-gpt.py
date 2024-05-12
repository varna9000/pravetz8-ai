import socket
import requests
from time import sleep

##################### MODEM COMMANDS ############################
# ATC"192.168.3.127:6502" #connect to model sockets
# ATQ1 # enter quiet mode
# ATR0 only CR?
# ATR2 # add /n/r end of the line
# ATT"ZDRASTI" # send msg
##################################################################

HOST = "192.168.3.127" 
PORT = 6502  # Port to listen on (non-privileged ports are > 1023)

mac2pravetz = {
    'А': 'A',
    'Б': 'B',
    'В': 'V',
    'Г': 'G',
    'Д': 'D',
    'Е': 'E',
    'Ж': 'V',
    'З': 'Z',
    'И': 'I',
    'Й': 'J',
    'К': 'K',
    'Л': 'L',
    'М': 'M',
    'Н': 'N',
    'О': 'O',
    'П': 'P',
    'Р': 'R',
    'С': 'S',
    'Т': 'T',
    'У': 'U',
    'Ф': 'F',
    'Х': 'H',
    'Ц': 'C',
    'Ч': '^',
    'Ш': '[',
    'Щ': ']',
    'Ъ': 'Y',
    'Ь': "X",
    'Ю': '@',
    'Я': 'Q',
}

pravetz2mac =  dict((v,k) for k,v in mac2pravetz.items())

def model_setup():
    prompt= "Ти си чатбот и трябва да отговаряш само по темата, по която те питат. Придържай се стриктно към нея. Всеки твой отговор не трябва да надвишава 254 символа."
    opts = {"stream": False, "model": "todorov/bggpt",  "prompt": prompt}
    result = requests.post("http://localhost:11434/api/generate", json=opts)

    if result.status_code == 200:
        print("Моделът е подкован с инструкции успешно.")
    else:
        print("Моделът не прие първоначалните инструкции. Спирам.")
        exit()

def to_pravetz(data):
    decoded =""

    for ch in data:
       if ch in mac2pravetz:
           decoded +=mac2pravetz[ch]
       else:
           decoded += ch

    return decoded.encode().decode('ascii','ignore')

def get_reply(query):
    decoded =""
    query=query.decode('ascii')

    for ch in query:
        if ch in pravetz2mac:
            decoded +=pravetz2mac[ch]
        else:
            decoded += ch

    opts = {"stream": False, "model": "todorov/bggpt",  "prompt": decoded}
    result = requests.post("http://localhost:11434/api/generate", json=opts)

    return result.json()['response']


model_setup()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            try:
                data = conn.recv(256)
                if not data:
                    break

                print(data)
                print("Responding ..")
                reply = to_pravetz(get_reply(data).upper())+"\n"
                print(reply)
                conn.send(reply.encode())

            except KeyboardInterrupt:
                print("Exiting ..")
                raise

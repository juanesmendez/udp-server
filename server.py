import socket
import os
import cv2
import pickle
import zlib
import struct
from os import walk

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

TCP_IP = "127.0.0.1"
TCP_PORT = 5014

BUFFER_SIZE = 4096
BUFFER_FILE = 8192

PAYLOAD_SIZE = struct.calcsize(">L")

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

def sendVideo(sock, addr, nombreVideo):

    cap = cv2.VideoCapture("./videos/" + nombreVideo)
    while True:
        print("Enviando frame...")
        ret, frame = cap.read()
        #print(frame)
        if ret == False:
            break
        bytesFrame = zlib.compress(pickle.dumps(frame))
        #print("Size frame comprimido(bytes):", len(bytesFrame))

        size = len(bytesFrame)
        print("Size:", size)
        size = struct.pack(">L", size)
        sock.sendto(size, addr) #Envio el tamaño del bytesFrame

        while len(bytesFrame) > BUFFER_SIZE:
            dataToSend = bytesFrame[0 : BUFFER_SIZE]
            #print(f"Sending data: {dataToSend}")
            sock.sendto(dataToSend, addr)
            bytesFrame = bytesFrame[BUFFER_SIZE : len(bytesFrame)]
            #print(f"Length bytesFrame: {len(bytesFrame)}")
        else:
            #print("Entering else...")
            dataToSend = bytesFrame[0: len(bytesFrame)]
            sock.sendto(dataToSend, addr)



        data, addr = sock.recvfrom(BUFFER_SIZE)  # Estoy reasignando la direccion
        if data.decode() == "stop": #Para saber si el cliente quiere parar la transmision
            break

    print("Terminando transmision")


def receiveVideo(sock, addr):
    #Enviar mensaje diciendo OK
    sock.sendto("ok".encode(), addr)
    message, addr = sock.recvfrom(BUFFER_SIZE)  # Estoy reasignando la direccion
    print(f"C: {message.decode()}")

    sock.sendto("ok".encode(), addr)

    #Conexion TCP para recibir archivo
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((TCP_IP, TCP_PORT))
    serverSocket.listen()
    clientSocket, clientAddress = serverSocket.accept()
    print(f"Conexion TCP: {clientAddress}")

    videoName = clientSocket.recv(BUFFER_SIZE)
    videoName = videoName.decode()
    print(f"Nombre del video: {videoName}")

    videoSize = clientSocket.recv(PAYLOAD_SIZE)
    videoSize = struct.unpack(">L", videoSize)
    print(f"Tamanio del video: {videoSize[0]}")

    data = b""

    while len(data) < videoSize[0]:
        newdata = clientSocket.recv(BUFFER_FILE)
        # print(f"Receiving video... {len(newdata)}")
        data = data + newdata
        print(f"Total video: {len(data)}")

    clientSocket.close()
    #serverSocket.shutdown(socket.SHUT_RD)
    serverSocket.close()
    # Se guarda el video en un nuevo archivo:
    path = './videos/' + videoName
    file = open(path, 'wb')
    file.write(data)


def sendPing(sock, addr):
    sock.sendto("alive".encode(), addr)


def grabVideosList(sock, addr):
    f = []
    for (dirpath, dirnames, filenames) in walk('./videos'):
        f.extend(filenames)
        break
    print(f)

    data = pickle.dumps(f)
    sock.sendto(data, addr)



sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    print("ENTERS LOOP")
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print ("received message:", data.decode())
    print(f"Client address: {addr}")

    #Aniadir logica de lo que toca hacer dependiendo del mensaje
    if data.decode() == 'Upload':
        receiveVideo(sock, addr)
    elif data.decode() == 'videos-list':
        grabVideosList(sock, addr)
    else:
        nombreVideo = data.decode()
        print(nombreVideo)
        sendVideo(sock, addr, nombreVideo)

    #sendVideo(sock, addr)

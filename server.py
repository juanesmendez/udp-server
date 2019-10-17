import socket
import os
import cv2
import pickle
import zlib
import struct
import numpy as np

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
BUFFER_SIZE = 8192

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

def sendVideo(sock, addr):

    cap = cv2.VideoCapture("./videos/video-5.mp4")
    while True:
        ret, frame = cap.read()
        #print(frame)
        if ret == False:
            break
        bytesFrame = zlib.compress(pickle.dumps(frame))
        #print("Size frame comprimido(bytes):", len(bytesFrame))

        size = len(bytesFrame)
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


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    print("ENTERS LOOP")
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print ("received message:", data.decode())
    print(f"Client address: {addr}")

    sendVideo(sock, addr)

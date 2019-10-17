import socket
import os

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
BUFFER_SIZE = 8192

def sendVideo(sock, addr):
    file = open("./videos/video-5.mp4", "rb")
    bytesArchivo = file.read(BUFFER_SIZE)
    bytesCounter = 0
    bytesLeft = os.stat("./videos/video-5.mp4").st_size
    while bytesArchivo:
        bytesCounter = bytesCounter + BUFFER_SIZE
        print(f"Bytes left: {bytesLeft}")
        sock.sendto(bytesArchivo, addr)
        bytesLeft = bytesLeft - BUFFER_SIZE
        bytesArchivo = file.read(BUFFER_SIZE)
        #receive message
        #if bytesArchivo:
        #'''
        data, addr = sock.recvfrom(BUFFER_SIZE) #Estoy reasignando la direccion
        #'''


    print(f"Bytes leidos: {bytesCounter}")
    print("Tamaño archivo (bytes):", os.stat("./videos/video-5.mp4").st_size)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    print("ENTERS LOOP")
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print ("received message:", data.decode())
    print(f"Client address: {addr}")

    sendVideo(sock, addr)

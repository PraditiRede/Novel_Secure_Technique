import socket
import math
import random
import re
import pickle
import os
import cv2
import Crypto
from Crypto import Random
from Crypto.Cipher import AES
import stego

def ServerPrivKey(p) :
    num = 0
    num = random.randint(0, 1000) + 1
    while (True) :
        if (num < p) :
            break
        else :
            num = random.randint(0, 1000) + 1
    return num

def ServerKey(a, p, g) :
    power = powerfunc(g, a)
    pub = power % p
    return pub

def powerfunc(b, e) :
    p = 1
    while (e != 1) :
        p = p * b
        e = e - 1
    return p

def decrypt(ciphertext, key):
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    return plaintext.rstrip(b"\0")

def genKey2 (Kb2) : 
    i = 0
    key = ""
    while (i < 10) : 
        if (i == len(Kb2)) :
            i = 0
        if (len(key) == 10) :
        	break
        key = key + Kb2[i]
        i = i + 1
    return key

def VignereDecrypt (v1, key) :
    pt = ""
    i = 0
    while (i < len(v1) and i < len(key)) : 
        j = ord(v1[i]) - 97
        x = (j - int(key[i]) + 26) % 26
        x = x + 97
        pt = pt + chr(x); 
        i = i + 1
    return pt

def org_v1_v2 (s1, s2) :
    v1 = s1
    v2 = ""
    for i in s2 :
        if (re.findall(r"[\d+]+", i)) :
            v2 = v2 + i
        else :
            v1 = v1 + i
    return v1, v2

def pos_v1 (pos, v1) :
    var = []
    i = 0
    k = 0
    while (i < len(pos) and k < len(v1)) :
        if (i % 2 == 0) :
            var.append(pos[i])
            pos[i] = str(12345)
            k = k + 1
        i = i + 1
    return var

def pos_v2 (pos, v2) :
    num = []
    i = 0
    k = 0
    while (i < len(pos) and k < len(v2)) :
        if (pos[i] != '12345') :
            num.append(pos[i])
            k = k + 1
        i = i + 1
    return num

def pos_list (var, num) :
    org_len = len(var) + len(num)
    org = [0] * org_len
    j = 0
    for i in var :
        if j < len(v1) :
            org[i] = v1[j]
            j = j + 1
    j = 0
    for i in num :
        if j < len(v2) :
            org[i] = v2[j]
            j = j + 1
    return org

def org_str (pos_list) :
    dec = ""
    c = 0
    for i in pos_list :
        if c < len(pos_list) :
            dec = dec + str(pos_list[c])
            c = c + 1
    return dec

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
IP_address = "127.0.0.1"
Port = 5000
server.bind((IP_address, Port))
server.listen(5)
print("Server Started")
print("Waiting for Client to accept")
conn, addr = server.accept()
print("Client accepted")

# Diffie Hellman Key Exchange (First)
print("\nDiffie Hellman First Key Exchange :-")
p1 = conn.recv(2048)
g1 = conn.recv(2048)
if p1 :
    p1 = int(p1.decode('utf-8'))
if g1 :
    g1 = int(g1.decode('utf-8'))
b1 = ServerPrivKey(p1)
B1 = ServerKey(b1, p1, g1)
conn.send(bytes(str(B1),'utf-8'))
A1 = conn.recv(2048)
if A1 :
    A1 = int(A1.decode('utf-8'))
Kb1 = ServerKey(b1, p1, A1)
print("Server Secret Key 1 : Kb1 = ", Kb1)

# Diffie Hellman Key Exchange (Second)
print("\nDiffie Hellman Second Key Exchange :-")
p2 = conn.recv(2048)
g2 = conn.recv(2048)
if p2 :
    p2 = int(p2.decode('utf-8'))
if g2 :
    g2 = int(g2.decode('utf-8'))
A2 = conn.recv(2048)
if A2 :
    A2 = int(A2.decode('utf-8'))
b2 = ServerPrivKey(p2)
B2 = ServerKey(b2, p2, g2)
conn.send(bytes(str(B2),'utf-8'))
Kb2 = ServerKey(b2, p2, A2)
print("Server Secret Key 2 : Kb2 = ", Kb2)

# Receiving stego image, encrypted v2 & positions of elements
file_stego = conn.recv(2048)
v2 = conn.recv(2048)
pos = conn.recv(2048)
print("\nStego Image, encrypted v2 & position of characters Received successfully")
if file_stego :
    file_stego = file_stego.decode('utf-8')
    print("Stego Image received from Client is : ", file_stego)
if v2 :
    v2 = v2.decode('utf-8')
    print("v2 data received from Client is : ", v2)
if pos :
    pos = pos.decode('utf-8')
    pos = eval(pos)
    print("Positions of alternate character and integer received from Client is : \n", pos)

# Steganography Image Decryption
print("\nSteganography Decryption :-")
stego_dct = cv2.imread(file_stego, cv2.IMREAD_UNCHANGED)
stego_dec = stego.decode_image(stego_dct)
print("Stego Decrypted message is : ", stego_dec)

# Vighnere Decryption
print("\nVighnere Decryption with Key Kb2 :-")
Kb2 = str(Kb2)
key = genKey2(Kb2)
v1 = VignereDecrypt(stego_dec, key)
print("Vighnere decrypted v1 message is : ", v1)

# Rejoining v1 v2 & positions
print("\nRejoining v1 v2 & positions :-")
v1, v2 = org_v1_v2(v1, v2)
print("Original v1 (alphabets) is : ", v1)
print("Original v2 (numbers) is : ", v2)
var = pos_v1(pos, v1) 
num = pos_v2(pos, v2)
pos_list = pos_list(var, num)
org_hex = org_str(pos_list)
print("Original decrypted message in hexadecimal format is : ", org_hex)

# Hexadecimal into Bytes
print("\nHexadecimal into Bytes Decryption :-")
org_bytes = bytearray.fromhex(org_hex)
org_bytes = bytes(org_bytes)
print("Decrypted message in bytes is : \n", org_bytes)

# AES Decryption into bytes
print("\nAES Decryption with Key Kb1 :-")
Kb1 = Kb1.to_bytes(32, 'big')
aes_dec = decrypt(org_bytes, Kb1)
aes_dec = aes_dec.decode('utf-8')
print("Decrypted original message : ", aes_dec)
 
conn.close() 
server.close()
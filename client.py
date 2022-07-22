import socket
import sympy
import random
import math
import re
import pickle
import os
import cv2
import Crypto
from Crypto import Random
from Crypto.Cipher import AES
import primitive as pr
import stego

def ClientPrivKey(p) :
    num = 0
    num = random.randint(0, 1000) + 1
    while (True) :
        if (num < p) :
            break
        else :
            num = random.randint(0, 1000) + 1
    return num

def ClientKey(a, p, g) :
    power = powerfunc(g, a)
    pub = power % p
    return pub

def powerfunc(b, e) :
    p = 1
    while (e != 1) :
        p = p * b
        e = e - 1
    return p

def pad(s):
    return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

def encrypt(message, key, key_size=256):
    message = pad(message)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(message)

def splitting (hex_ct) :
    enc_str = re.findall(r"[^\W\d_]+|\d+", hex_ct)
    v1 = ""
    v2 = ""
    for i in enc_str :
        if (re.findall(r"[^\W\d_]+", i)) :
            v1 = v1 + i
        else :
            v2 = v2 + i
    return v1, v2

def positions (hex_ct) :
    pos = []
    var = []
    num = []
    counter = 0
    for i in hex_ct :
        if (i >= 'a' and i <= 'f') :
            var.append(counter)
        counter = counter + 1
    counter = 0
    for i in hex_ct :
        if (i >= '0' and i <= '9') :
            num.append(counter)
        counter = counter + 1
    i = 0
    j = 0
    while (i < len(var) or j < len(num)) :
        if (i < len(var)) :
            pos.append(var[i])
            i = i + 1
        if (j < len(num)) :
            pos.append(num[j])
            j = j + 1
    return pos

def new_split(v1, v2) :
    s1 = ""
    s2 = ""
    for i in v2 :
        s2 = s2 + i
    c = 0
    while (c != 10) :
        s1 = s1 + v1[c]
        c = c + 1
    c = 10
    while (c >= 10 and c < len(v1)) :
        s2 = s2 + v1[c] 
        c = c + 1
    return s1, s2

def genKey2 (Ka2) : 
    i = 0
    key = ""
    while (i < 10) : 
        if (i == len(Ka2)) :
            i = 0
        if (len(key) == 10) :
        	break
        key = key + Ka2[i]
        i = i + 1
    return key

def VignereEncrypt (st, key) :
    ct = "" 
    i = 0
    for i in range (len(st)) : 
        j = int(ord(st[i])) - 97
        x = (j + int(key[i])) % 26 
        x = x + 97
        ct = ct + chr(x)
        i = i + 1
    return ct

client = socket.socket()
IP_address = "127.0.0.1"
Port = 5000
client.connect((IP_address, Port)) 
print("Server Connected")
 
# Diffie Hellman Key Exchange (First)
print("\nDiffie Hellman First Key Exchange :-")
p1 = sympy.randprime(3, 5000)
client.send(bytes(str(p1),'utf-8'))
g1 = pr.findPrimitive(p1)
client.send(bytes(str(g1),'utf-8'))
a1 = ClientPrivKey(p1)
B1 = client.recv(2048)
if B1 :
    B1 = int(B1.decode('utf-8'))
Ka1 = ClientKey(a1, p1, B1)
A1 = ClientKey(a1, p1, g1)
client.send(bytes(str(A1),'utf-8'))
print("Client Secret Key 1 : Ka1 = ", Ka1)

# Diffie Hellman Key Exchange (Second)
print("\nDiffie Hellman Second Key Exchange :-")
p2 = sympy.randprime(3, 5000)
client.send(bytes(str(p2),'utf-8'))
g2 = pr.findPrimitive(p2)
client.send(bytes(str(g2),'utf-8'))
a2 = ClientPrivKey(p2)
A2 = ClientKey(a2, p2, g2)
client.send(bytes(str(A2),'utf-8'))
B2 = client.recv(2048)
if B2 :
    B2 = int(B2.decode('utf-8'))
Ka2 = ClientKey(a2, p2, B2)
print("Client Secret Key 2 : Ka2 = ", Ka2)

msg = str(input("\nEnter the message to be encrypted : "))

# AES Encryption into hexadecimal
print("\nAES Encryption with Key Ka1 :-")
aes_enc = encrypt(bytes(msg, 'utf-8'), Ka1.to_bytes(32, 'big'))
print("Encrypted message in bytes is : ", aes_enc)

# Byte to Hexadecimal
print("\nByte to Hexadecimal Encryption :-")
hex_ct = aes_enc.hex()
print("Encrypted message in hexdecimal is : ", hex_ct)

# Splitting v1 and v2 & positions
print("\nSplitting into v1, v2 & storing positions of characters :-")
v1, v2 = splitting(hex_ct)
print("alphabets in encrypted message (v1) : ", v1)
print("numbers in encrypted message (v2) : ", v2)
pos = positions(hex_ct)
print("Positions of alternate character and integer from hexadecimal encrypted message : \n", pos)
v1, v2 = new_split(v1, v2)
print("first 10 alphabets (new v1) : ", v1)
print("numbers appended to remaining alphabets (new v2) : ", v2)

# Vighnere Encryption
print("\nVighnere Encryption with Key Ka2 :-")
Ka2 = str(Ka2)
key = genKey2(Ka2)
vig_enc = VignereEncrypt(v1, key)
print("Vighnere encrypted v1 message is : ", vig_enc)

# Steganography Image Encryption
file_enc = "pepper.png"
stego_dct = cv2.imread(file_enc, cv2.IMREAD_UNCHANGED)
stego_enc = stego.encode_image(stego_dct, vig_enc)
cv2.imwrite(file_enc, stego_enc)
print("\nSteganography Encryption Completed")

# Sending stego image, encrypted v2 & positions of elements
client.send(bytes(file_enc,'utf-8'))
client.send(bytes(v2,'utf-8'))
pos = str(pos)
pos = pos.encode()
client.send(pos)
print("\nStego Image, encrypted v2 & positions of characters Sent successfully")

# Closing the socket connection
client.close()
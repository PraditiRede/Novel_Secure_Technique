import cv2
from PIL import Image
import numpy as np
import itertools

quant = np.array([[16,11,10,16,24,40,51,61],      
                    [12,12,14,19,26,58,60,55],    
                    [14,13,16,24,40,57,69,56],
                    [14,17,22,29,51,87,80,62],
                    [18,22,37,56,68,109,103,77],
                    [24,35,55,64,81,104,113,92],
                    [49,64,78,87,103,121,120,101],
                    [72,92,95,98,112,100,103,99]])

def encode_image (img, msg):
    message = str(len(msg)) + '*' + msg
    bitMess = toBits(message)
    row,col = img.shape[:2]
    oriRow, oriCol = row, col  
    if (col / 8) * (row / 8) < len(message) :
        print("Error: Message too large to encode in image")
        return False
    if row % 8 != 0 or col % 8 != 0 :
        img = addPadd(img, row, col)
    row, col = img.shape[:2]
    bImg, gImg, rImg = cv2.split(img)
    bImg = np.float32(bImg)
    imgBlocks = [np.round(bImg[j:j+8, i:i+8] - 128) for (j, i) in itertools.product(range(0, row, 8), range(0, col, 8))]
    dctBlocks = [np.round(cv2.dct(img_Block)) for img_Block in imgBlocks]
    quantizedDCT = [np.round(dct_Block / quant) for dct_Block in dctBlocks]
    messIndex = 0
    letterIndex = 0
    for quantizedBlock in quantizedDCT :
        DC = quantizedBlock[0][0]
        DC = np.uint8(DC)
        DC = np.unpackbits(DC)
        DC[7] = bitMess[messIndex][letterIndex]
        DC = np.packbits(DC)
        DC = np.float32(DC)
        DC= DC - 255
        quantizedBlock[0][0] = DC
        letterIndex = letterIndex + 1
        if letterIndex == 8 :
            letterIndex = 0
            messIndex = messIndex + 1
            if messIndex == len(message) :
                break
    sImgBlocks = [quantizedBlock * quant + 128 for quantizedBlock in quantizedDCT]
    sImg = []
    for chunkRowBlocks in chunks(sImgBlocks, col / 8) :
        for rowBlockNum in range(8):
            for block in chunkRowBlocks:
                sImg.extend(block[rowBlockNum])
    sImg = np.array(sImg).reshape(row, col)
    sImg = np.uint8(sImg)
    sImg = cv2.merge((sImg, gImg, rImg))
    return sImg

def decode_image (img) :
    row,col = img.shape[:2]
    messSize = None
    messageBits = []
    buff = 0
    bImg, gImg, rImg = cv2.split(img)
    bImg = np.float32(bImg)
    imgBlocks = [bImg[j : j + 8, i : i + 8] - 128 for (j, i) in itertools.product(range(0, row, 8), range(0, col, 8))]    
    quantizedDCT = [img_Block / quant for img_Block in imgBlocks]
    i = 0
    for quantizedBlock in quantizedDCT :
        DC = quantizedBlock[0][0]
        DC = np.uint8(DC)
        DC = np.unpackbits(DC)
        if DC[7] == 1 :
            buff += (0 & 1) << (7 - i)
        elif DC[7] == 0 :
            buff += (1 & 1) << (7 - i)
        i = i + 1
        if i == 8 :
            messageBits.append(chr(buff))
            buff = 0
            i = 0
            if messageBits[-1] == '*' and messSize is None :
                try :
                    messSize = int(''.join(messageBits[:-1]))
                except:
                    pass
        if len(messageBits) - len(str(messSize)) - 1 == messSize:
            return ''.join(messageBits)[len(str(messSize)) + 1:]
    sImgBlocks = [quantizedBlock * quant + 128 for quantizedBlock in quantizedDCT]
    sImg = []
    for chunkRowBlocks in chunks(sImgBlocks, col / 8):
        for rowBlockNum in range(8):
            for block in chunkRowBlocks:
                sImg.extend(block[rowBlockNum])
    sImg = np.array(sImg).reshape(row, col)
    sImg = np.uint8(sImg)
    sImg = cv2.merge((sImg, gImg, rImg))
    return ''
      
def chunks(l, n) :
    m = int(n)
    for i in range(0, len(l), m) :
        yield l[i:i + m]
    
def addPadd(img, row, col) :
    img = cv2.resize(img, (col + (8 - col % 8), row + (8 - row % 8)))    
    return img
    
def toBits(message) :
    bits = []
    for char in message :
        binval = bin(ord(char))[2:].rjust(8, '0')
        bits.append(binval)
    numBits = bin(len(bits))[2:].rjust(8, '0')
    return bits

# m = input("To encode press '1', to decode press '2', press any other button to close: ")
# if m == "1":
# 	original_image_file = input("Enter the name of the file with extension : ")
# 	dct_img = cv2.imread(original_image_file, cv2.IMREAD_UNCHANGED)
# 	secret_msg = input("Enter the message you want to hide: ")
# 	print("The message length is: ",len(secret_msg))
# 	dct_img_encoded = DCT().encode_image(dct_img, secret_msg)
# 	dct_encoded_image_file = "dct_" + original_image_file
# 	cv2.imwrite(dct_encoded_image_file,dct_img_encoded)
# 	print("Encoded images were saved!")
# elif m == "2":
# 	decodeimage = input("Enter the name of the file with extension : ")
# 	dct_img = cv2.imread(decodeimage, cv2.IMREAD_UNCHANGED)
# 	dct_hidden_text = DCT().decode_image(dct_img)
# 	print("The message hidden in the image is: ")
# 	print(dct_hidden_text)
# else:
# 	print("Wrong input")
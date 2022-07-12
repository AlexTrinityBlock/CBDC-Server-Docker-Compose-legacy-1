import random

def randomBinaryString(binaryLength:int):
    binaryString = str()
    for i in range(binaryLength):
        binaryElement = str(random.randint(0, 1))
        binaryString += binaryElement
    return binaryString
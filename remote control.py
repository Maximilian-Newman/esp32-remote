import pyautogui
import hashlib
import time
import socket
import random
import time

mouseSensitivity = 0.6

def generate_salt():
    salt = ""
    for i in range(30):
        salt += random.choice("QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890")
        salt += str(time.time)
    return salt

lastMsgNum = 0

def sign(message, msgNum):
    message += "secret password 1234abcd"
    message += salt + str(msgNum)
    message += "\0"
    sha256_hash = hashlib.sha256(message.encode("utf-8"))
    return str(sha256_hash.hexdigest())


salt = generate_salt()
rewindMode = False

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(("192.168.4.1", 8080))
    s.sendall(b"salt=\n" + salt.encode("utf-8") + b"\n")
    while True:
        protocol = ""
        while protocol.count("\n") == 0:
            protocol += s.recv(1).decode("utf-8")
        protocol = protocol[:-1]

        
        if protocol == "remote-v0.1" or protocol == "remote-v0.2":
            print("Please update your remote firmware")
            print("It is using an old version of the communication protocol.")
            print("Support for the old protocol was dropped due to vulnerability to replay attacks")
            print()
        
        elif protocol == "remote-v1.0":
            mLength = int(s.recv(10).decode("utf-8"))
            msg = ""
            while len(msg) < mLength:
                msg += s.recv(mLength - len(msg)).decode("utf-8")

            msg = msg.split("\n")
            
            instruction = msg[0]
            msgNum = int(msg[1])
            recvSignature = msg[2]
            
            verifyHash = sign(instruction, msgNum)

            if verifyHash == recvSignature and msgNum > lastMsgNum:
                lastMsgNum = msgNum

                if instruction == "space press":
                    pyautogui.keyDown(" ")
                elif instruction == "space release":
                    pyautogui.keyUp(" ")

                elif instruction == "right press":
                    rewindMode = True
                elif instruction == "right release":
                    rewindMode = False

                elif instruction == "left press":
                    pyautogui.mouseDown();
                elif instruction == "left release":
                    pyautogui.mouseUp();

                elif instruction.startswith("mouse:"):
                    instruction = instruction.split(":")
                    pos = instruction[1].split(",")
                    vx = int(pos[0])
                    vy = int(pos[1])
                    if rewindMode:
                        if vx < -50:
                            pyautogui.press("left")
                        if vx > 50:
                            pyautogui.press("right")
                        if vy < -50:
                            pyautogui.press("volumedown") # not working for me
                        if vy > 50:
                            pyautogui.press("volumeup")
                    else:
                        vx *= mouseSensitivity
                        vy *= mouseSensitivity
                        pyautogui.move(vx, -vy)

                else:
                    print("unknown unstruction:")
                    print(instruction)

                s.sendall(b"OK\n")
                
            else:
                print("Failed signature check!")
                s.sendall(b"salt=\n" + salt.encode("utf-8") + b"\n")

        else:
            print("unknown protocol:", protocol)

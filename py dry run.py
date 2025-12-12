import hashlib
import time
import socket
import random
import time


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
                    print("pressed space")
                elif instruction == "space release":
                    print("released space")

                elif instruction == "right press":
                    print("pressed right click")
                elif instruction == "right release":
                    print("released right click")

                elif instruction == "left press":
                    print("pressed left click")
                elif instruction == "left release":
                    print("released left click")

                elif instruction.startswith("mouse:"):
                    instruction = instruction.split(":")
                    pos = instruction[1].split(",")
                    vx = pos[0]
                    vy = pos[1]
                    print("moved mouse x", vx, "y", vy)

                else:
                    print("unknown unstruction:")
                    print(instruction)

                s.sendall(b"OK\n")
                
            else:
                print("Failed signature check!")
                s.sendall(b"salt=\n" + salt.encode("utf-8") + b"\n")

        else:
            print("unknown protocol:", protocol)
        





print("Disconnected, attempting to reconnect...")
time.sleep(5)

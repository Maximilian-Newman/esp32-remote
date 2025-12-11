import hashlib
import time
import socket


def sign(message):
    message += "secret password 1234abcd"
    message += "\0"
    sha256_hash = hashlib.sha256(message.encode("utf-8"))
    return str(sha256_hash.hexdigest())


connected = True

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("192.168.4.1", 8080))
        while connected:
            msg = ""
            while msg.count("\n") < 3:
                msg += s.recv(4096).decode("utf-8")

            msg = msg.split("\n")
            
            if msg[0] == "remote-v0.1" or msg[0] == "remote-v0.2":
                instruction = msg[1]
                verifyHash = sign(instruction)

                if verifyHash == msg[2]:

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
                        print("moveed mouse x", vx, "y", vy)

                    else:
                        print("unknown unstruction:")
                        print(instruction)

                    if msg[0] == "remote-v0.2":
                        s.sendall(b"OK")
                    
                else:
                    print("Failed signature check!")
            





    print("Disconnected, attempting to reconnect...")
    time.sleep(5)

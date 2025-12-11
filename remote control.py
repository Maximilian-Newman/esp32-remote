import pyautogui
import hashlib
import time
import socket

mouseSensitivity = 0.6

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
                        #print("pressed space")
                        pyautogui.keyDown(" ")
                    elif instruction == "space release":
                        #print("released space")
                        pyautogui.keyUp(" ")

                    elif instruction == "right press":
                        #print("pressed right click")
                        pyautogui.mouseDown(button='right');
                    elif instruction == "right release":
                        #print("released right click")
                        pyautogui.mouseUp(button='right');

                    elif instruction == "left press":
                        #print("pressed left click")
                        pyautogui.mouseDown();
                    elif instruction == "left release":
                        #print("released left click")
                        pyautogui.mouseUp();

                    elif instruction.startswith("mouse:"):
                        instruction = instruction.split(":")
                        pos = instruction[1].split(",")
                        vx = int(int(pos[0]) * mouseSensitivity)
                        vy = int(int(pos[1]) * mouseSensitivity)
                        #print("moved mouse x", vx, "y", vy)
                        pyautogui.move(vx, -vy)

                    else:
                        print("unknown unstruction:")
                        print(instruction)

                    if msg[0] == "remote-v0.2":
                        s.sendall(b"OK")
                    
                else:
                    print("Failed signature check!")
                time.sleep(0.05)
            





    print("Disconnected, attempting to reconnect...")
    time.sleep(5)

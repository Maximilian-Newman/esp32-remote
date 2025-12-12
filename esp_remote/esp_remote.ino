#include <Hash.h>
#include <SHA256.h>
#include <WiFi.h>

#define HASH_SIZE 32
SHA256 sha256;
Hash *hash = &sha256;

const byte DNS_PORT = 53;

IPAddress apIP(192, 168, 4, 1);
IPAddress netMsk(255, 255, 255, 0);

WiFiServer tcpServer(8080);
WiFiClient client;


int BTN_TIMEOUT = 150; // prevent button signal bouncing


bool spaceIsClicked = false;
bool rightIsClicked = false;
bool leftIsClicked = false;
unsigned long lastNoSpace = 0;
unsigned long lastNoRight = 0;
unsigned long lastNoLeft = 0;
unsigned long lastSpace = 0;
unsigned long lastRight = 0;
unsigned long lastLeft = 0;

unsigned int messageNum = 0;
String salt = "";



String sign(String message){
  message += "secret password 1234abcd";
  message += salt;
  message += String(messageNum);

  int bufferSize = message.length() + 1;
  char charmsg[bufferSize];
  message.toCharArray(charmsg, bufferSize);

  uint8_t value[HASH_SIZE];

  hash->reset();
  hash->update(charmsg, bufferSize);
  hash->finalize(value, sizeof(value));

  String output = "";
  for (byte i=0; i<HASH_SIZE; i++){
    if (value[i] < 16) {output += "0";}
    output += String(value[i], HEX);
  }
  return output;
}


void transmit(String message, byte recursionNum = 0){
  messageNum += 1;
  if (client) {
    //Serial.println("Client connected!");
    if (client.connected()) {
      if (client.connected()) {
        String transmission = message + "\n";
        transmission += String(messageNum) + "\n";
        transmission += sign(message) + "\n";
        unsigned int len = transmission.length();
        String sLen = String(len);
        while (sLen.length() < 10){
          sLen = "0" + sLen;
        }
        client.print("remote-v1.0\n");
        client.print(sLen);
        client.print(transmission);
      }
      unsigned long giveUpTime = millis() + 1500;
      while (!client.available() and giveUpTime < millis()){
        if (!client.available() and recursionNum < 3){
          transmit(message, recursionNum + 1); // try again
        }
      }
    }
  }
  else{
    //Serial.println("not connected. couldn't transmit");
  }
}





void setup() {
  Serial.begin(115200);
  Serial.println("\n\n");

  pinMode(27, INPUT);
  pinMode(33, INPUT);
  pinMode(35, INPUT);
  pinMode(32, INPUT);
  pinMode(34, INPUT);

  uint8_t mac[6];
  WiFi.macAddress(mac);
  
  WiFi.softAPConfig(apIP, apIP, netMsk);
  WiFi.softAP("Max Remote Control", "passwordRC");
  
   tcpServer.begin();
}

unsigned long nextPing = 0;

void loop() {

  
  if (!client) {client = tcpServer.available();}
  else if (!client.connected()) {client.stop();}

  if (client.available()) {
    if (client.readStringUntil('\n') == "salt="){
      salt = client.readStringUntil('\n');
    }
  }

  int vx = map(analogRead(35), 0, 4095, -100, 100) + 12;
  int vy = map(analogRead(32), 0, 4095, -100, 100) + 12;

  if (vx > -15 and vx < 15) {vx = 0;}
  if (vy > -15 and vy < 15) {vy = 0;}

  if (digitalRead(34) == HIGH) {lastNoSpace = millis();}
  if (digitalRead(34) == LOW) {lastSpace = millis();}
  if (spaceIsClicked and millis() - lastSpace > BTN_TIMEOUT){
    spaceIsClicked = false;
    //Serial.println("space released");
    transmit("space release");
  }
  if (!spaceIsClicked and millis() - lastNoSpace > BTN_TIMEOUT){
    spaceIsClicked = true;
    //Serial.println("space pressed");
    transmit("space press");
  }

  if (digitalRead(33) == HIGH) {lastNoRight = millis();}
  if (digitalRead(33) == LOW) {lastRight = millis();}
  if (rightIsClicked and millis() - lastRight > BTN_TIMEOUT){
    rightIsClicked = false;
    //Serial.println("right click released");
    transmit("right release");
  }
  if (!rightIsClicked and millis() - lastNoRight > BTN_TIMEOUT){
    rightIsClicked = true;
    //Serial.println("right click pressed");
    transmit("right press");
  }

  if (digitalRead(27) == HIGH) {lastNoLeft = millis();}
  if (digitalRead(27) == LOW) {lastLeft = millis();}
  if (leftIsClicked and millis() - lastLeft > BTN_TIMEOUT){
    leftIsClicked = false;
    //Serial.println("left click released");
    transmit("left release");
  }
  if (!leftIsClicked and millis() - lastNoLeft > BTN_TIMEOUT){
    leftIsClicked = true;
    //Serial.println("left click pressed");
    transmit("left press");
  }

  //Serial.println(analogRead(35));

  if (vx !=0 or vy != 0){
    //Serial.print(vx);
    //Serial.print("\t");
    //Serial.println(vy);
    transmit("mouse:" + String(vx) + "," + String(vy));
    delay(100);
  }
}

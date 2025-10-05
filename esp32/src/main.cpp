#include <Arduino.h>
#include <LiquidCrystal_I2C.h>
#include <BluetoothSerial.h>
#include "DHT.h"

#define DHTPIN 15
#define DHTTYPE DHT11 

LiquidCrystal_I2C lcd(0x27,16,2);  
BluetoothSerial ESP_BT;

// Пины AD8232
#define OUT_PIN 36
#define MINUS_PIN 2
#define PLUS_PIN 4 
#define BUTTON_PIN 27

DHT dht(DHTPIN, DHTTYPE);

float lastHumidity = 0;
int threshold = 2700;
int beatCount = 0;
int averageBPM = 0;
unsigned long lastPeakTime = 0;
bool wasAboveThreshold = false;

void setup() {
  Serial.begin(9600);
  ESP_BT.begin("Cardioreg");

  lcd.init();                
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Calculating...");

  unsigned long startTime = millis();
  int mxValue = 0;
  while (millis() - startTime < 15000) {
    int egcValue = analogRead(OUT_PIN);
    mxValue = max(egcValue, mxValue);
    delay(10);
  }
  threshold = mxValue*0.8;
  dht.begin();
}

void loop() {
  float startH = dht.readHumidity();
  float h = startH;
  
  if (isnan(startH)) {
    Serial.println("Ошибка чтения с DHT");
    return;
  }
  unsigned long startTime = millis();
  beatCount = 0;
  int mxValue = 0;
  int i = 0;
  bool allWet = true;
  while (millis() - startTime < 15000) {
    i++;
    if (i == 100) {
      i = 0;
      h = dht.readHumidity();
      if (h <= 85) {
        allWet = false;
      } 
    }
    int egcValue = analogRead(OUT_PIN);
    mxValue = max(egcValue, mxValue);
    char buffer[20];
    ESP_BT.println(egcValue);
    Serial.println(egcValue);
    
    if (!wasAboveThreshold && egcValue > threshold) {
      beatCount++;
      wasAboveThreshold=true;
    }
    if (wasAboveThreshold && egcValue < threshold) {
      wasAboveThreshold=false;
    }
    delay(10);
  }

  if (allWet || h - startH > 1.0) {
    ESP_BT.println("breath");
    Serial.println("breath");
  }
  else {
    ESP_BT.println("noBreath");
    Serial.println("noBreath");
  }

  threshold = mxValue*0.7;
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("threshold: ");
  lcd.print(threshold);
  lcd.setCursor(0, 1);
  lcd.print("beatCount: ");
  lcd.print(beatCount*6);
  char buffer[20];
  sprintf(buffer,"bpm%d",beatCount*6);
  ESP_BT.println(buffer);
  Serial.println(buffer);
  beatCount=0;
} 
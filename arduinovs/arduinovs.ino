/* The true ESP32 chip ID is essentially its MAC address.
This sketch provides an alternate chip ID that matches 
the output of the ESP.getChipId() function on ESP8266 
(i.e. a 32-bit integer matching the last 3 bytes of 
the MAC address. This is less unique than the 
MAC address chip ID, but is helpful when you need 
an identifier that can be no more than a 32-bit integer 
(like for switch...case).

created 2020-06-07 by cweinhofer
with help from Cicicok */
	
uint32_t chipId = 0;

#include <Wire.h>
#include "Adafruit_MCP9808.h"

#include <Adafruit_INA219.h>

// Create the  temperature sensor object
Adafruit_MCP9808 tempsensor = Adafruit_MCP9808();

//Create current sensor objects
Adafruit_INA219 cs1(0x40);
Adafruit_INA219 cs2(0x41);
Adafruit_INA219 cs3(0x42);
Adafruit_INA219 cs4(0x4C);
Adafruit_INA219 cs5(0x44);
Adafruit_INA219 cs6(0x45);
Adafruit_INA219 cs7(0x46);
Adafruit_INA219 cs8(0x4D);
Adafruit_INA219 cs9(0x48);
Adafruit_INA219 cs10(0x49);
Adafruit_INA219 cs11(0x4A);



void setup() {
	Serial.begin(115200);

 if (!tempsensor.begin(0x18)) {
    Serial.println("Couldn't find MCP9808! Check your connections and verify the address is correct.");
    while (1);
  }
  if (! cs2.begin()) {
    Serial.println("Failed to fINA219ind cs1 chip");
    while (1) { delay(10); }
  }
  Serial.println("found all devices");
  cs2.setCalibration_16V_400mA();
  delay(2000);
}

void loop() {
	
  // Read and print out the temperature, also shows the resolution mode used for reading.
  Serial.print("Resolution in mode: ");
  Serial.println (tempsensor.getResolution());
  float c = tempsensor.readTempC();
 
  Serial.print("Temp: "); 
  Serial.print(c, 4); Serial.print("*C\t and "); 
  
  
  delay(2000);
  float shuntvoltage = 0;
  float busvoltage = 0;
  float current_mA = 0;
  float loadvoltage = 0;
  float power_mW = 0;

  shuntvoltage = cs2.getShuntVoltage_mV();
  busvoltage = cs2.getBusVoltage_V();
  current_mA = cs2.getCurrent_mA();
  power_mW = cs2.getPower_mW();
  loadvoltage = busvoltage + (shuntvoltage / 1000);
  
  Serial.print("Bus Voltage:   "); Serial.print(busvoltage); Serial.println(" V");
  Serial.print("Shunt Voltage: "); Serial.print(shuntvoltage); Serial.println(" mV");
  Serial.print("Load Voltage:  "); Serial.print(loadvoltage); Serial.println(" V");
  Serial.print("Current:       "); Serial.print(current_mA); Serial.println(" mA");
  Serial.print("Power:         "); Serial.print(power_mW); Serial.println(" mW");
  Serial.println("");
  delay(200);
  
}

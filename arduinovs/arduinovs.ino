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
void(* resetFunc) (void) = 0;//declare reset function at address 0

#include <Wire.h>
#include "Adafruit_MCP9808.h"

#include <Adafruit_INA219.h>

// Create the  temperature sensor object
Adafruit_MCP9808 tempsensor = Adafruit_MCP9808();

//Create current sensor objects
Adafruit_INA219 cs1(0x40); //U6
Adafruit_INA219 cs2(0x41); // U21
Adafruit_INA219 cs3(0x42); //U11
Adafruit_INA219 cs4(0x4C);//U18
Adafruit_INA219 cs5(0x44); //U10
Adafruit_INA219 cs6(0x45); //U23
Adafruit_INA219 cs7(0x46);//U15
Adafruit_INA219 cs8(0x4D);//U7
Adafruit_INA219 cs9(0x48);//U14
Adafruit_INA219 cs10(0x49);//U3
Adafruit_INA219 cs11(0x4A); //U19

Adafruit_INA219 currentSensors[]={cs1,cs2,cs3,cs4,cs5,cs6,cs7,cs8,cs9,cs10,cs11};

void setup() {
	Serial.begin(115200);

 if (!tempsensor.begin(0x18)) {
    Serial.println("Couldn't find MCP9808! Check your connections and verify the address is correct.");
    delay(200);
    resetFunc();
  }
  for (byte i=0 ; i < 12; i++){
  if (! currentSensors[i].begin()) {
    Serial.println("Failed to find INA219 cs chip:"+(i+1));
    delay(200);
    resetFunc();
    
  }
  currentSensors[i].setCalibration_16V_400mA();
  }
  Serial.println("found all devices");
  pinMode(23, OUTPUT);
  delay(2000);
}

void loop() {
	
  // Read and print out the temperature, also shows the resolution mode used for reading.
  
  float c = tempsensor.readTempC();
 
  Serial.print("Temp: "); 
  Serial.print(c, 4); 
  Serial.println("*C "); 
  float shuntvoltage = 0;
  float busvoltage = 0;
  float current_mA = 0;
  float loadvoltage = 0;
  float power_mW = 0;
  
  delay(4000);
  for (byte i=0 ; i < 11; i++){
   shuntvoltage = 0;
   busvoltage = 0;
   current_mA = 0;
  loadvoltage = 0;
   power_mW = 0;

  shuntvoltage = currentSensors[i].getShuntVoltage_mV();
  busvoltage = currentSensors[i].getBusVoltage_V();
  current_mA = currentSensors[i].getCurrent_mA();
  power_mW = currentSensors[i].getPower_mW();
  loadvoltage = busvoltage + (shuntvoltage / 1000);
  Serial.print("Current Sensor ");Serial.print(i+1); Serial.println(":");
  Serial.print("Bus Voltage:   "); Serial.print(busvoltage); Serial.println(" V");
  Serial.print("Shunt Voltage: "); Serial.print(shuntvoltage); Serial.println(" mV");
  Serial.print("Load Voltage:  "); Serial.print(loadvoltage); Serial.println(" V");
  Serial.print("Current:       "); Serial.print(current_mA); Serial.println(" mA");
  Serial.print("Power:         "); Serial.print(power_mW); Serial.println(" mW");
  Serial.println("");
  delay(4000);
 
  }
  busvoltage = currentSensors[3].getBusVoltage_V();
  if ( busvoltage < 4) {
    // turn LED on
    digitalWrite(23, HIGH);
    delay(5000);
    digitalWrite(23, LOW);
  } else {
    // turn LED off
    digitalWrite(23, LOW);
  }
  
}

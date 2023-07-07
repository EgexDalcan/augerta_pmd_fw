import serial
import pandas
import numpy as np
import time
from datetime import date

'''
This code receives data from arduinovs.ino and interprets it and saves it in files named Hourly.csv, Daily.csv, Weekly.csv
The variables below (baudrate, port, sensorAmount, dataInterval(sec)) should be set properly before running. Make sure to run this code
and after this run arduinovs.ino, or you will get an exception. If you change anything in arduinovs.ino, you may have to change same parts
of this code as well as it directly disects the data received from arduinovs.ino.
'''

baudrate = 115200                                                                                 #Baudrate from arduinovs.ino
port = "COM6"                                                                                     #The port that the transmitter in connected to
sensorAmount = 11                                                                                 #The amount of sensors connected to the transmitter
dataInterval = 60                                                                                 #The interval between data collections

'''
DataCollection class collects the data at that moment and saves it
'''
class DataCollector:
  data = []                                                                                       #Empty list to write momentary data
  sensorAmount = 0                                                                                #Amount of sensors in the system, set in __init__()
  ser = serial.Serial()                                                                           #The serial connection, set in __init__()

  #Initialize the serial port. Check if the port is correct
  def __init__(self, baudrate, port, sensorAmount):
    self.ser.baudrate = baudrate                                                                  #Sets the baudrate
    self.ser.port = port                                                                          #Sets the port for the connection. Make sure it is set correctly
    self.ser.open()                                                                               #Opens the connection
    self.sensorAmount = sensorAmount                                                              #Sets the amount of sensors connected. Make sure it is set correctly
    #Checking if the connection is established correctly
    frstLine = self.ser.readline().decode("UTF-8")
    if  frstLine == "found all devices\n":
      print("Connection established!")
    else:
      raise Exception("Couldn't find the device or the sensors, check if the port is correct or the connection of the sensors are done correctly!\n Make sure to run this code before sending the data.")

  #Gets the time/date for use
  def getTime(self):
    t = time.localtime()
    current_time = time.strftime("_%H%M%S", t)
    d = date.today()
    today = d.strftime("%B%d%y")
    daytime = today + current_time
    return daytime

  #Parses through each sensor's data to get the information
  def parseData(self):
    self.data = []
    readData = self.ser.readline().decode("UTF-8")
    readData = readData.split(": ")[1]
    self.data.append("")
    self.data.append(self.getTime())
    self.data.append(readData.split("\n")[0])
    j = 0
    while j < self.sensorAmount:
      i = 0
      while i < 6:
        readData = self.ser.readline().decode("UTF-8")
        if "Current Sensor" in readData:
          readData = readData.split(" ")[2]
          self.data.append("")
          self.data.append(readData.split(":")[0])
        else:
          readData = readData.split(": ")[1]
          self.data.append(readData.split("\n")[0])
        i = i + 1
      j = j + 1
    print("Parsed Through Data!")
    return self.data

'''
DataInterpreter class takes the data from the DataCollector and saves it in different intervals and calculates the statistics then
writes the files.
'''
class DataInterpreter:
  dataInterval = 60                                                                               #Interval between all data points
  hourData = []                                                                                   #Data library for an hour
  hourptr = 0                                                                                     #Index for hour library
  dayData = []                                                                                    #Data library for a day
  dayptr = 0                                                                                      #Index for day library
  weekData = []                                                                                   #Data library for a week
  weekptr = 0                                                                                     #Index for week library
  #Statistic Lists for hourly record
  hourBusVoltAv = []
  hourShuntVoltAv = []
  hourLoadVoltAv = []
  hourCurrAv = []
  hourPowAv = []
  #Statistic Lists for daily record
  dayBusVoltAv = []
  dayShuntVoltAv = []
  dayLoadVoltAv = []
  dayCurrAv = []
  dayPowAv = []
  #Statistic Lists for weekly record
  weekBusVoltAv = []
  weekShuntVoltAv = []
  weekLoadVoltAv = []
  weekCurrAv = []
  weekPowAv = []
  #Statistic Types
  dataTypeOne = ["", "Current sensor: ", "Bus voltage: ", "Shunt Voltage: ", "Load Voltage: ",
                  "Current: ", "Power: "]                                                         #All repeating statistics types
  dataType = ["", "Time: ", "Temperature: "]                                                      #The rest of the statistics types

  def __init__(self, baudrate, port, sensorAmount, intervalSec):
    self.dataCollector = DataCollector(baudrate, port, sensorAmount)
    self.dataInterval = intervalSec
    
  #writes the data for week-day-hour data lists
  def writeData(self, data):
    #writes for an hour
    if(len(self.hourData) < 3600/self.dataInterval):
      self.hourData.append(data)
      self.createFile(self.hourData, "Hourly")
    else:
      if(self.hourptr < len(self.hourData)-1):
        self.hourData[self.hourptr] = data
        self.hourptr = self.hourptr + 1
        self.createFile(self.hourData, "Hourly")
      else:
        self.hourData[self.hourptr] = data
        self.hourptr = 0
        self.createFile(self.hourData, "Hourly")
    
    #writes for a day
    if(len(self.dayData) < 86400/self.dataInterval):
      self.dayData.append(data)
      self.createFile(self.dayData, "Daily")
    else:
      if(self.dayptr < len(self.dayData)-1):
        self.dayData[self.dayptr] = data
        self.dayptr = self.dayptr + 1
        self.createFile(self.dayData, "Daily")
      else:
        self.dayData[self.dayptr] = data
        self.dayptr = 0
        self.createFile(self.dayData, "Daily")

    #writes for a week
    if(len(self.weekData) < 604800/self.dataInterval):
      self.weekData.append(data)
      self.createFile(self.weekData, "Weekly")
    else:
      if(self.weekptr < len(self.weekData)-1):
        self.weekData[self.weekptr] = data
        self.weekptr = self.weekptr + 1
        self.createFile(self.weekData, "Weekly")
      else:
        self.weekData[self.weekptr] = data
        self.weekptr = 0
        self.createFile(self.weekData, "Weekly")
      

  #Creates and writes the .csv file
  def createFile(self, data, intervalType):
    #Prepares the data types for .csv file
    self.dataType = ["", "Time: ", "Temperature: "]
    statDataType = ["Save Type: "]
    statData = [intervalType]
    calcAverages = self.getAverages(intervalType)
    calcRanges = self.getRanges(intervalType)
    j = 0
    rangeIndex = 0
    while j < self.dataCollector.sensorAmount:
      statDataType.append("")
      statDataType.append("Sensor" + str(j + 1) + ": ")
      statDataType.append("Bus Voltage Average: ")
      statDataType.append("Shunt Voltage Average: ")
      statDataType.append("Load Voltage Average: ")
      statDataType.append("Current Average: ")
      statDataType.append("Power Average: ")
      statDataType.append("Bus Voltage Range: ")
      statDataType.append("Bus Voltage Max: ")
      statDataType.append("Bus Voltage Min: ")
      statDataType.append("Shunt Voltage Range: ")
      statDataType.append("Shunt Voltage Max: ")
      statDataType.append("Shunt Voltage Min: ")
      statDataType.append("Load Voltage Range: ")
      statDataType.append("Load Voltage Max: ")
      statDataType.append("Load Voltage Min: ")
      statDataType.append("Current Range: ")
      statDataType.append("Current Max: ")
      statDataType.append("Current Min: ")
      statDataType.append("Power Range: ")
      statDataType.append("Power Max: ")
      statDataType.append("Power Min: ")
      statData.append("")
      statData.append("")
      k = 0
      while k < len(calcAverages):
        statData.append(calcAverages[k][j])
        k = k + 1
      h = 0
      while h < len(calcRanges):
        statData.append(calcRanges[h][rangeIndex])
        statData.append(calcRanges[h][rangeIndex+1])
        statData.append(calcRanges[h][rangeIndex+2])
        h = h + 1
      rangeIndex = rangeIndex + 3
      j = j + 1
    i = 0
    while i < self.dataCollector.sensorAmount:
      self.dataType.extend(self.dataTypeOne)
      i = i + 1
    #Writes the .csv file
    dataFrame = pandas.DataFrame({"Data Type" : statDataType, "Value" : statData})
    for j in range(len(data)):
      #Writes the data frame
      dataAll = {"Data Type" : self.dataType, "Value" : data[j]}
      df = pandas.DataFrame(data = dataAll)
      #Merge the old and the new data frame
      df_list = []
      df_list.append(dataFrame)
      df_list.append(df)
      dataFrame = pandas.concat(df_list)
    dataFrame.to_csv(intervalType + ".csv")
    print("Created .csv file!")

  #Calculates and returns the average of the given data in each sensor and returns as a list
  def getAverages(self, intervalType):
    allAverages = []
    if(intervalType == "Hourly"):
      data = self.hourData
    elif(intervalType == "Daily"):
      data = self.dayData
    elif(intervalType == "Weekly"):
      data = self.weekData
    else:
      raise Exception("getAverages() function does not have a valid interval type set!")
    k = 0
    while k < 5:
      averages = []
      i = 0
      while i < self.dataCollector.sensorAmount:
        sensorData = []
        for j in range(len(data)):
          readData = data[j][5 + k + i * 7]
          sensorData.append(int(readData.split(" ")[0]))
        averages.append(np.average(sensorData))
        i = i + 1
      allAverages.append(averages)
      k = k + 1
    return allAverages
  
  #Calculates and returns the range of the given data in each sensor and returns a list
  def getRanges(self, intervalType):
    allRanges = []
    if(intervalType == "Hourly"):
      data = self.hourData
    elif(intervalType == "Daily"):
      data = self.dayData
    elif(intervalType == "Weekly"):
      data = self.weekData
    else:
      raise Exception("getRanges() function does not have a valid interval type set!")
    k = 0
    while k < 5:
      ranges = []
      i = 0
      while i < self.dataCollector.sensorAmount:
        sensorData = []
        for j in range(len(data)):
          readData = data[j][5 + k + i * 7]
          sensorData.append(int(readData.split(" ")[0]))
          localMax = max(sensorData)
          localMin = min(sensorData)
          localRange = localMax - localMin
        ranges.append(localRange)
        ranges.append(localMax)
        ranges.append(localMin)
        i = i + 1
      allRanges.append(ranges)
      k = k + 1
    return allRanges
  
  #Function to run all other functions
  def getData(self):
    data = self.dataCollector.parseData()
    self.writeData(data)

#Run
d = DataInterpreter(baudrate, port, sensorAmount, dataInterval)
while True:
  startTime = time.time()
  d.getData()
  #Makes sure the saved data is up to date
  while True:
    endTime = time.time()
    if(endTime - startTime < dataInterval):
      d.dataCollector.ser.readline()
    else:
      if("Temp: ".encode("UTF-8") in d.dataCollector.ser.readline()):
        i = 0
        while i < (sensorAmount * 6):
          d.dataCollector.ser.readline()
          i = i + 1
        break
      else:
        d.dataCollector.ser.readline()
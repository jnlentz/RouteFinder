# -*- coding: utf-8 -*-
"""
Created on Thu May  9 13:39:29 2019

@author: Jesse
"""

import csv
# Imports destination data into 2d list
distanceSheet = "distancetable.csv"
distanceTable = []

with open(distanceSheet, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        distanceTable.append(row)
#------------------------------------------------------------

# Imports package data into 2d list      
packageSheet = "packagetable.csv"
packageTable = []

with open(packageSheet, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        packageTable.append(row)
#------------------------------------------------------------
        
# Hash table uses packageID%40 as a key
class HashTable:
    index = []
    def __init__(self, size):        
        for i in range(0, size):  # Initializes N elements to 0 to allow for indexed insertion
            self.index.append(0)
            
    def insert(self, package):
        key = hash(package.ID)        
        if (self.index[key%40] == 0):
            self.index[key%40] = package
        
            
    def retrieve(self, ID):
        key = hash(ID)%40
        return self.index[key]
    
    def printAll(self):
        for i in range(1, 41):
            temp = self.retrieve(i)
            temp.printStatus()
#------------------------------------------------------------

# Stores address of location, as well as its spreadsheet index to allow for quick distance lookups
class Location:    
    # 'index' parameter refers to the index of the address in the spreadsheet
    def __init__(self, index):
        self.address = distanceTable[0][index]
        self.tableIndex = index
#------------------------------------------------------------
        
# Package objects contain all package information, as well as  a 'location' object    
class Package:    
    def __init__(self, index):        
        self.ID = int(packageTable[index][0])
        self.address = packageTable[index][1]
        self.city = packageTable[index][2]
        self.state = packageTable[index][3]
        self.azip = packageTable[index][4]
        self.dtime = packageTable[index][5] # stores expected delivery time while package is en route, then is updated with time of delivery when package is delivered
        self.mass = packageTable[index][6]        
        self.status = "Not Delivered"
        self.destinationIndex = int(packageTable[index][8]) 
        self.rawTime = 0
        
    def printStatus(self):
        print("Package ID: " + str(int(self.ID)))
        print("Destination address: " + str(self.address))
        print("Status: " + str(self.status))
        if (self.status == "Not Delivered"):
            print("ETA: " + str(self.dtime))
        else:
            print("Arrived at: " + str(self.dtime))
        print("--------------------------------------")
        
    def deliver(self, time, rawTime):
        key = hash(self.ID)%40
        packageLookup.index[key].status = "Delivered"
        packageLookup.index[key].dtime = time
        packageLookup.index[key].rawTime = rawTime
        
    def printAll(self):
        print("Package ID: " + str(int(self.ID)))
        print("Destination address: " + str(self.address))
        print("City: " + self.city)
        print("State: " + self.state)
        print("Zip code: " + self.azip)        
        print("Weight: " + self.mass)
        print(self.status)
        print("Arrived at: " + str(self.dtime))
#------------------------------------------------------------

# Converts distance travelled by trucks into time   
class Clock:
    hours = 0
    minutes = 0
    displayTime = None

    def __init__(self):
        self.hours = int(8)
        self.displayTime = str(self.hours) + ":00"       

    def tick(self, distance):
        temp = float(distance)/18
        self.minutes += int(temp*60)
        self.tock()
        if (self.minutes < 10):
            self.displayTime = str(self.hours) + ":0" + str(self.minutes)
        else:
            self.displayTime = str(self.hours) + ":" + str(self.minutes)
            
    def tock(self):        
        if (self.minutes >= 60):
            self.hours += 1
            self.minutes -= 60
        if (self.hours > 12):
            self.hours = 1
    
    def rawTime(self):
        rawTime = self.hours*60 + self.minutes
        return rawTime
#------------------------------------------------------------

# Constructor takes a list of location indexes as input, buildRoute() outputs an ordered list of location objects to be followed by the truck
class RouteBuilder:
    def __init__(self, destinations):
        temp = list(set(destinations)) # 'destinations' input list is cast to set in order to remove duplicates, then cast back to list to allow iteration
        self.hubRef = 1
        self.currentRef = 1
        self.inputLocations = temp
        self.route = []
        self.distances = []
        
    def nextLoc(self):
        nearest = self.inputLocations[0]
        index = 0
        for i in range(len(self.inputLocations)):
            if (float(distanceTable[self.inputLocations[i]][self.currentRef]) < float(distanceTable[nearest][self.currentRef])):
                nearest = self.inputLocations[i]
                index = i
        
        del self.inputLocations[index]
        self.distances.append(float(distanceTable[nearest][self.currentRef]))
        self.currentRef = nearest
        self.route.append(Location(nearest))
        
    def buildRoute(self):
        for i in range(len(self.inputLocations)):
            self.nextLoc()
        # Adds distance from last location in route to hub
        self.route.append(Location(self.hubRef))
        self.distances.append(distanceTable[self.currentRef][self.hubRef])
#        self.mileage += distanceTable[self.currentRef][self.hubRef]
        return self.route
#------------------------------------------------------------

# Truck objects contain a list of packages,  a list of destinations, and a list of distances between those packages.  Contains a clock object to keep track of each truck's time
class Truck:
    def __init__(self):
        self.packages = []
        self.destinations = [] # holds unordered list of destination indexes when object is initialized.  After route() is called, holds the sorted route
        self.distances = [] # holds an ordered list of distances between points in route, order should match that of destinations list
        self.currentLocation = Location(1)
        self.mileage = 0
        self.clock = Clock()
        self.routeBuilder = None
                
    def loadPackage(self, package):
        self.packages.append(package)
        self.destinations.append(int(package.destinationIndex))
        
    def route(self):
        self.routeBuilder = RouteBuilder(self.destinations)
        temp = self.routeBuilder.buildRoute()
        self.distances = self.routeBuilder.distances
        self.destinations = temp
    
    def deliver(self):
        self.clock.tick(self.distances[0])        
        self.currentLocation = self.destinations[0].address
        self.mileage += float(self.distances[0])
        for i in range(len(self.packages)):
            if (self.packages[i].address == self.currentLocation):
                self.packages[i].deliver(self.clock.displayTime, self.clock.rawTime())                
        
        del self.destinations[0]
        del self.distances[0]
        
    def beginRoute(self):
        for i in range(len(self.destinations)):
            self.deliver()
        self.currentLocation = Location(1)
        self.packages = []
        self.destinations = []
#------------------------------------------------------------ 

# Stores delivery information for scheduled reports
class Report:
    def __init__(self):
        self.report1 = []
        self.report2 = []
        self.report3 = []
        
    def addPackage(self, package):
        temp = package
        self.report1.append(temp)
        self.report2.append(temp)
        self.report3.append(temp)
        
    def update(self, package):
        if (package.rawTime < 565 and package.rawTime > 0):
            self.report1[package.ID-1] = package
            self.report2[package.ID-1] = package
            self.report3[package.ID-1] = package
        elif (package.rawTime < 625):
            self.report2[package.ID-1] = package
            self.report3[package.ID-1] = package 
        else:
            self.report3[package.ID-1] = package   
    
    def printReport1(self):
        for i in self.report1:
            i.printStatus()
    
    def printReport2(self):
        for i in self.report2:
            i.printStatus()
    
    def printReport3(self):
        for i in self.report3:
            i.printStatus()
#------------------------------------------------------------
        
# Inputs package data into hash table
packageLookup = HashTable(40)

for i in range(1,41):
    temp = Package(i)   
    packageLookup.insert(temp)
#------------------------------------------------------------

reportBuilder = Report()
for i in range(1, 41):
    temp = Package(i)
    reportBuilder.addPackage(temp)



# Loads lists of packages onto each truck and begins deliveries
truck1 = Truck()
truck1Packages = [4, 13, 14, 15, 16, 19, 24, 27, 31, 33, 34, 35, 36, 39]
for i in truck1Packages:
    truck1.loadPackage(packageLookup.retrieve(i))

truck1.route()
truck1.beginRoute()

truck2 = Truck()
truck2Packages = [1, 2, 3, 5, 7, 8, 10, 11, 12, 18, 23, 29, 30, 36, 37, 38]
for i in truck2Packages:
    truck2.loadPackage(packageLookup.retrieve(i))
 
truck2.route()
truck2.beginRoute()


truck1hold = [6, 9, 17, 20, 21, 28, 32, 40]
for i in truck1hold:
    truck1.loadPackage(packageLookup.retrieve(i))

truck1.route()
truck1.beginRoute()

truck2hold = [22, 25, 26]
for i in truck2hold:
    truck2.loadPackage(packageLookup.retrieve(i))

truck2.route()
truck2.beginRoute()
#------------------------------------------------------------

# Updates reports with timed delivery information
for i in range(1, 41):
    temp = packageLookup.retrieve(i)
    reportBuilder.update(temp)
reportBuilder.printReport1()
reportBuilder.printReport2()
reportBuilder.printReport3()
#------------------------------------------------------------

lookUp = input("ID # of package: ")
packageLookup.retrieve(lookUp).printAll()
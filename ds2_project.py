# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 13:41:50 2019

@author: Jesse
"""

import xlrd # This library allows python to access excel files directly
# Reads package data from spreadsheet
loc = ("C:/Users/Jesse/Documents/DS2 project/packagefile.xls")
packageFile = xlrd.open_workbook(loc)
packageList = packageFile.sheet_by_index(0)
#------------------------------------------------------------

# Reads destination data from spreadsheet
loc2 = ("C:/Users/Jesse/Documents/DS2 project/distancetable.xls")
destinations = xlrd.open_workbook(loc2)
destinationTable = destinations.sheet_by_index(0)
#------------------------------------------------------------

class HashTable:
    index = []
    def __init__(self, size):        
        for i in range(0, size):
            self.index.append(0)
            
    def insert(self, package):
        key = hash(package.packageID)        
        if (self.index[key%40] == 0):
            self.index[key%40] = package
        
            
    def retrieve(self, ID):
        key = hash(ID)%40
        return self.index[key]

    
class Package:
    destination = None
    packageID = None
    address = None
    city = None
    state = None
    azip = None
    dtime = None
    mass = None
    status = None
    
    def __init__(self, packageID, address, city, state, azip, dtime, mass, status, destination):
        self.destination = Location(destination)
        self.packageID = packageID
        self.address = address
        self.city = city
        self.state = state
        self.azip = azip
        self.dtime = dtime
        self.mass = mass        
        
            
    def printStatus(self):
        print("Package ID: " + str(int(self.packageID)))
        print("Address: " + str(self.address))
        print("Status: " + str(self.status))
        print(self.dtime)
        print("--------------------------------------")
        
    def deliver(self, time):
        key = hash(self.packageID)%40
        packageTable.index[key].status = "Delivered"
        packageTable.index[key].dtime = time

class Location:
    address = None
    hubDistance = None
    tableIndex = None
    
    # 'index' parameter refers to the index of the address in the spreadsheet
    def __init__(self, index):
        self.address = destinationTable.cell_value(0, index)
        self.hubDistance = destinationTable.cell_value(1, index)
        self.tableIndex = index

    

# Inputs package data into hash table
packageTable = HashTable(40)

for i in range(8,48):
    temp = Package(packageList.cell_value(i,0), packageList.cell_value(i,1), packageList.cell_value(i,2), packageList.cell_value(i,3), packageList.cell_value(i,4), packageList.cell_value(i,5), packageList.cell_value(i,6), packageList.cell_value(i, 7), int(packageList.cell_value(i, 8)))   
    packageTable.insert(temp)


#-------------------------------------
   
class Clock:
    hours = 0
    minutes = 0
    displayTime = None

    def __init__(self):
        self.hours = int(8)
        self.displayTime = str(self.hours) + ":00"       

    def tick(self, distance):
        temp = distance/18
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

class RouteBuilder:
    hub = Location(1) 
    currentLoc = Location(1)
    inputLocations = []
    route = []
    distances = []
    mileage = 0
    
    def __init__(self, destinations):
        temp = list(set(destinations)) # 'destinations' input list is cast to set in order to remove duplicates, then cast back to list to allow iteration
        for i in temp:
            self.inputLocations.append(Location(i))

        
    def nextLoc(self):
        nearest = self.inputLocations[0]
        index = 0
        for i in range(len(self.inputLocations)):
            if (destinationTable.cell_value(self.inputLocations[i].tableIndex, self.currentLoc.tableIndex) < destinationTable.cell_value(nearest.tableIndex, self.currentLoc.tableIndex)):
                nearest = self.inputLocations[i]
                index = i
        
        del self.inputLocations[index]
        self.route.append(nearest)
        self.distances.append(destinationTable.cell_value(nearest.tableIndex, self.currentLoc.tableIndex))
        self.mileage += destinationTable.cell_value(nearest.tableIndex, self.currentLoc.tableIndex)
        self.currentLoc = nearest
        
    def buildRoute(self):
        for i in range(len(self.inputLocations)):
            self.nextLoc()
        # Adds distance from last location in route to hub
        self.route.append(self.hub)
        self.distances.append(destinationTable.cell_value(self.currentLoc.tableIndex, self.hub.tableIndex))
        self.mileage += destinationTable.cell_value(self.currentLoc.tableIndex, self.hub.tableIndex)
        return self.route
  
class Truck:
    packages = []
    destinations = [] # holds unordered list of destination indexes when object is initialized.  After route() is called, holds the sorted route
    distances = [] # holds an ordered list of distances between points in route, order should match that of destinations list
    currentLocation = None
    mileage = 0
    _clock = None
    rb = None
    def __init__(self):
        self.packages = []
        self.destinations = []
        self.currentLocation = Location(1)
        self.mileage = 0
        self._clock = Clock()
                
    def loadPackage(self, package):
        self.packages.append(package)
        self.destinations.append(package.destination.tableIndex)
        
    def route(self):
        self.rb = RouteBuilder(self.destinations)
        temp = self.rb.buildRoute()
        self.distances = self.rb.distances
        self.destinations = temp
    
    def deliver(self):
        self._clock.tick(self.distances[0])        
        self.currentLocation = self.destinations[0].address
        self.mileage += self.distances[0]
        for i in range(len(self.packages)):
            if (self.packages[i].address == self.currentLocation):
                self.packages[i].deliver(self._clock.displayTime)                
        
        del self.destinations[0]
        del self.distances[0]
        
    def beginRoute(self):
        for i in range(len(self.destinations)):
            self.deliver()
        self.currentLocation = Location(1)
        self.packages = []
        self.destinations = []
            
 

truck1 = Truck()
truck1Packages = [4, 13, 14, 15, 16, 19, 20, 21, 24, 27, 31, 34, 35, 36, 39]
for i in truck1Packages:
    truck1.loadPackage(packageTable.retrieve(i))

truck1.route()
truck1.beginRoute()


truck2 = Truck()
truck2Packages = [1, 3, 5, 7, 8, 9, 10, 11, 12, 18, 23, 29, 30, 36, 37, 38]
for i in truck2Packages:
    truck2.loadPackage(packageTable.retrieve(i))
 
truck2.route()
truck2.beginRoute()


holdPackages = [2, 6, 17, 22, 25, 26, 28, 32, 33, 40]
for i in holdPackages:
    for i in holdPackages:
        truck1.loadPackage(packageTable.retrieve(i))

truck1.route()
truck1.beginRoute()

for i in range(1, 41):
    packageTable.retrieve(i).printStatus()

print(truck1.mileage)
print(truck2.mileage)




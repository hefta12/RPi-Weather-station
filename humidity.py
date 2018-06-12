#!/usr/bin/python
import sys
import Adafruit_DHT
import httplib, urllib
import subprocess 
import re 
import os 
import time 
import MySQLdb as mdb 
import datetime

databaseUsername="dbusrname"
databasePassword="dbpw" 
databaseName="dbname" 
key = 'thingspeak key'

sensor=Adafruit_DHT.DHT11 
pinNum=4 

def save(humidity):
	params = urllib.urlencode({'field': humidity, 'key': key})
	headers = {"Content-typZZe": "application/x-www-form-urlencoded", "Accept": "text/plain"}
	conn = httplib.HTTPConnection("api.thingspeak.com:80")
	try:
		conn.request("POST", "/update", params, headers)
		response = conn.getresponse()
		print response.status, response.reason
		data = response.read()
		conn.close()

	except:
		print "connection failed"


def saveToDatabase(temperature,humidity):

	con=mdb.connect("localhost", databaseUsername, databasePassword, databaseName)
        currentDate=datetime.datetime.now().date()

        now=datetime.datetime.now()
        ti=datetime.datetime.now().time()

	
        with con:
                cur=con.cursor()
		
                cur.execute("INSERT INTO dht11 (temperatura,wilgotnosc,data,czas) VALUES (%s,%s,%s,%s)",(temperature,humidity,currentDate, ti))

		print "Saved temperature"
		return "true"


def readInfo():

	humidity, temperature = Adafruit_DHT.read_retry(sensor, pinNum)

	print "Temperature: %.1f C" % temperature
	print "Humidity:    %s %%" % humidity

	if humidity is not None and temperature is not None:
		return saveToDatabase(temperature,humidity),save(humidity)
	else:
		print 'nie udalo sie sprobuj ponownie!'
		sys.exit(1)


#sprawdzenie czy tabela istnieje
try:
	queryFile=file("createTable.sql","r")

	con=mdb.connect("localhost", databaseUsername,databasePassword,databaseName)
        currentDate=datetime.datetime.now().date()

        with con:
		line=queryFile.readline()
		query=""
		while(line!=""):
			query+=line
			line=queryFile.readline()
		
		cur=con.cursor()
		cur.execute(query)	


		queryFile.close()
        	os.rename("createTable.sql","createTable.sql.bkp")
	

except IOError:
	pass #tabela stworzona
	

status=readInfo() #pomiary


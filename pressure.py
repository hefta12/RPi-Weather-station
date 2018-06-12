#!/usr/bin/python
import sys
import httplib, urllib
import subprocess 
import re 
import os 
import time 
import MySQLdb as mdb 
import datetime
import bmp180 as bmp180

databaseUsername="dbusrname"
databasePassword="dbpw" 
databaseName="dbname" 
key = 'thingspeak key'


def save(pressure):
	params = urllib.urlencode({'field': pressure, 'key': key})
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



def saveToDatabase(temperature,pressure):

	con=mdb.connect("localhost", databaseUsername, databasePassword, databaseName)
        currentDate=datetime.datetime.now().date()

        now=datetime.datetime.now()
        ti=datetime.datetime.now().time()
	
        with con:
                cur=con.cursor()
		
                cur.execute("INSERT INTO bmp180 (temperatura,cisnienie, data,czas) VALUES (%s,%s,%s,%s)",(temperature,pressure,currentDate, ti))

		print "saved"
		return "true"


def readInfo():


        (temperature,pressure) = bmp180.readBmp180()

      
        print "Temperatura : {0} C".format(temperature)
        print "Cisnienie    : {0} HPa".format(pressure)

	if temperature is not None and pressure is not None:
		return saveToDatabase(temperature,pressure),save(pressure)
	else:
		print 'nie udalo sie sprobuj ponownie!'
		sys.exit(1)


try:
	queryFile=file("createTable1.sql","r")

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
        	os.rename("createTable1.sql","createTable1.sql.bkp")
	

except IOError:
	pass 

status=readInfo() #get the readings


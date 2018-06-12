import os
import glob
import sys
import re
import time
import subprocess
import MySQLdb as mdb 
import datetime
import httplib, urllib
 
databaseUsername="dbusrname"
databasePassword="dbpw" 
databaseName="dbname" 
key = 'thingspeak key'

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'



def save(temperature):
	params = urllib.urlencode({'field': temperature, 'key': key})
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

def saveToDatabase(temperature):

	con=mdb.connect("localhost", databaseUsername, databasePassword, databaseName)
        currentDate=datetime.datetime.now().date()

        now=datetime.datetime.now()
        ti=datetime.datetime.now().time()


        with con:
                cur=con.cursor()

                cur.execute("INSERT INTO ds18b20 (temperatura,data,czas) VALUES (%s,%s,%s)",(temperature,currentDate,ti))

                print 'temperatura ds18b20 : %s C'%temperature
		print "saved"
		return temperature




def read_temp_raw():
	catdata = subprocess.Popen(['cat',device_file], 
	stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out,err = catdata.communicate()
	out_decode = out.decode('utf-8')
	lines = out_decode.split('\n')
	return lines

 
def read_temp():
    lines = read_temp_raw()
  
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
#        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return saveToDatabase(temp_c), save(temp_c)
	


try:
	queryFile=file("createTable2.sql","r")

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
		
        	os.rename("createTable2.sql","createTable2.sql.bkp")
       

except IOError:

        pass

save(read_temp())



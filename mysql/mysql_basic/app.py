import mysql.connector
import datetime

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="!1234Asdf",
    database="3elda"
)

mycursor = mydb.cursor()

print("Connected..")

sql = "INSERT INTO sensor(verdi,tid) VALUES (%s,%s)"

verdi = 5.0
tid = datetime.datetime.now()

val = (verdi, tid)

print("Executing...")

mycursor.execute(sql, val)
mydb.commit()

print("Done")

'''
    Inserting to database:
    
    
'''
#
# sql = "INSERT INTO sensors (name) VALUES ute_temp"
# val = ("ute_temp")
#
# mycursor.execute(sql)
# mydb.commit()
#
# print(mycursor.rowcount, "record inserted")

'''
    Show tables:------------------
    
    mycursor = mydb.cursor()

    mycursor.execute("SHOW TABLES")
    
    for x in mycursor:
        print(x)
'''


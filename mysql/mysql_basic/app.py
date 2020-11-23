import mysql.connector


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="test"
)

print(mydb)


mycursor = mydb.cursor()

'''
    Inserting to database:
    
    
'''

sql = "INSERT INTO sensors (name) VALUES ute_temp"
val = ("ute_temp")

mycursor.execute(sql)
mydb.commit()

print(mycursor.rowcount, "record inserted")

'''
    Show tables:------------------
    
    mycursor = mydb.cursor()

    mycursor.execute("SHOW TABLES")
    
    for x in mycursor:
        print(x)
'''


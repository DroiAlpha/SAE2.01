import psycopg2

connection = psycopg2.connect(database="eaufrance", user="postgres", password="postgres", host="yuri", port=5432)

cursor = connection.cursor()

cursor.execute("SELECT * from commune;")

# Fetch all rows from database
record = cursor.fetchall()

print("Data from Database:- ", record)
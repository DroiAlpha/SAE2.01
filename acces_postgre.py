import psycopg2

connection = psycopg2.connect(database="eaufrance", user="yuri", password="yuri",host='10.10.47.80' , port=5432)

cursor = connection.cursor()

cursor.execute("SELECT * from commune;")

record = cursor.fetchall()

print("Data from Database:- ", record)
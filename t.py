import pandas as pd
from sqlalchemy import create_engine
import pymysql
import pyodbc

server = 'tcp:sqlserver.cannoba.de' 
database = 'buntebluete' 
username = 'SA' 
password = 'Service0!' 

#x=[{"a":1,"b":"abc","c":"xyz"},{"a":55,"b":"hjk","c":"iutritu"},{"a":678,"b":"uzuzu","c":"ewewe"}]
#df=pd.DataFrame(x)
#print(df.loc[0:2]['b'])

#engine = create_engine("mysql+pymysql://{user}:{pw}@sqlserver.cannoba.de/{db}".format(user="root",pw="Service0",db="employee"))
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password, autocommit = True)

#engine = create_engine("mssql+pyodbc://{user}:{pw}@sqlserver.cannoba.de/{db}".format(user="root",pw="Service0",db="employee"))
engine = create_engine("mssql+pyodbc://sa:Service0!@sqlserver.cannoba.de:1433/employee?driver=ODBC+Driver+17+for+SQL+Server")

data = pd.DataFrame({
    'book_id':[12345, 12346, 12347],
    'title':['Python Programming', 'Learn MySQL', 'Data Science Cookbook'],
    'price':[29, 23, 27]
})

print(data)
data.to_sql('book_details', con = engine, if_exists = 'append', chunksize = 1000, index = False)
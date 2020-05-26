import pandas as pd
import json
import pyodbc
import logging
import itertools
import string
import datetime
from sqlalchemy import create_engine
import pymysql

server = 'tcp:sqlserver.cannoba.de' 
database = 'buntebluete' 
username = 'SA' 
password = 'Service0!' 

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password, autocommit = True)
mycursor = conn.cursor()

mysqleng = create_engine("mysql+pymysql://{user}:{pw}@sqlserver.cannoba.de/{db}".format(user="root",pw="Service0",db="employee"))
mssqleng = create_engine("mssql+pyodbc://sa:Service0!@sqlserver.cannoba.de:1433/buntebluete?driver=ODBC+Driver+17+for+SQL+Server")

#logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(asctime)s %(name)s %(funcName)s() %(lineno)i %(levelname)s %(message)s')
log = logging.getLogger(__name__)

def db_truncate(table):
    try:
        sql = "truncate table " + table
        mycursor.execute(sql)
    except Exception as ex:
        log.error(f'{ex}')
    log.info(f'table {table}: truncated')
    print(f'table {table}: truncated')


def db_select(sql):
    start = datetime.datetime.now()
    try:
        df = pd.read_sql(sql, conn)
    except Exception as ex:
        log.error(f'{ex}')
    end = datetime.datetime.now()
    log.info(f'query {sql} in {(end-start).seconds} seconds processed')
    print(f'query {sql} in {(end-start).seconds} seconds processed')
    return(df.to_dict('records'))


def db_copy(table):
    try:
        db_truncate(table+'_')
        mycursor.execute('insert into ' + table + '_ select * from '+table)
    except Exception as ex:
        log.error(f'{ex}')
    log.info(f'table {table}: copied to {table}_')
    print(f'table {table}: copied to {table}_')


def db_get(table):
    start = datetime.datetime.now()
    try:
        df = pd.read_sql_table(table, mssqleng)
    except Exception as ex:
        log.error(f'{ex}')
    end = datetime.datetime.now()
    log.info(f'table {table}: {len(df.index)} records read in {(end-start).seconds} seconds')
    print(f'table {table}: {len(df.index)} records read in {(end-start).seconds} seconds')
    return df.to_dict('records')

# inserts records into tables from a given list of dictionaries where key=column-name
def db_put(table, data):
    start = datetime.datetime.now()
    try:
        df = pd.DataFrame(data)
        df.to_sql(table, con = mysqleng, if_exists = 'replace', index = False)
    except Exception as ex:
        log.error(f'{ex}')
    end = datetime.datetime.now()
    log.info(f'table {table}: {len(df.index)} records written in {(end-start).seconds} seconds')
    print(f'table {table}: {len(df.index)} records written in {(end-start).seconds} seconds')


#x=[{"a":1,"b":"abc","c":"xyz"},{"a":55,"b":"hjk","c":"iutritu"},{"a":678,"b":"uzuzu","c":"ewewe"}]
#df=pd.DataFrame(x)
#print(df.loc[0:2]['b'])


x = db_get('b_order')
##x = df.to_dict('records')
#print(x)
db_put('b_orderx',x)

#data = pd.DataFrame({
#    'book_id':[12345, 12346, 12347],
#    'title':['Python Programming', 'Learn MySQL', 'Data Science Cookbook'],
#    'price':[29, 23, 27]
#})

#print(data)


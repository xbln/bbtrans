import json
import pyodbc
import logging
import itertools
import string
import datetime

#logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(asctime)s %(name)s %(funcName)s() %(lineno)i %(levelname)s %(message)s')
log = logging.getLogger(__name__)

server = 'tcp:sqlserver.cannoba.de' 
database = 'buntebluete' 
username = 'SA' 
password = 'Service0!' 

def db_init():
	try:
		global mydb
		myconnection = pyodbc.connect(
			'DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password, autocommit = True
		)

		global mycursor
		mycursor = myconnection.cursor()
	except Exception as ex:
		log.error(f'{ex}')
		
# get a list of columns from a view or table
def get_collist(view):
	try:
		sql = "select top 1 * from " + view
		mycursor.execute(sql)
		collist = []
		for row in mycursor.description:
			collist.append(row[0])
		log.debug(f'collist: {collist} length {len(collist)} sql: {sql}')
	except Exception as ex:
		log.error(f'{ex}')
	return collist
		

def db_truncate(table):
	try:
		sql = "truncate table " + table
		mycursor.execute(sql)
		log.debug(f'sql {sql}')
		result = 1
	except Exception as ex:
		log.error(f'{ex}')
		result = 0
	log.info(f'table {table}: truncated')
	print(f'table {table}: truncated')
	return result

def db_select(sql):
	start = datetime.datetime.now()
	result = []
	try:
		mycursor.execute(sql)
		result = mycursor.fetchall()
	except Exception as ex:
		log.error(f'{ex}')
	end = datetime.datetime.now()
	log.info(f'query {sql} processed')
	print(f'query {sql} processed')
	return(result)

def db_copy(table):
	try:
		db_truncate(table+'_')
		mycursor.execute('insert into ' + table +'_ select * from '+table)
	except Exception as ex:
		log.error(f'{ex}')
	log.info(f'table {table}: copied to {table}_')
	print(f'table {table}: copied to {table}_')

def db_get(view):
	start = datetime.datetime.now()
	try:
		sql = "select * from " + view
		mycursor.execute(sql)
		# get a list of columns
		collist = []
		for row in mycursor.description:
			collist.append(row[0])
		# get the result as list of dict {fieldname : value}
		result = [dict(zip(collist, row)) for row in mycursor.fetchall()]
		log.debug(f'collist: {collist} from {len(result)} results, sql {sql}')
	except Exception as ex:
		log.error(f'{ex}')
	end = datetime.datetime.now()
	log.info(f'table {view}: {len(result)} records read in {(end-start).seconds} seconds')
	print(f'table {view}: {len(result)} records read in {(end-start).seconds} seconds')
	return result
		
# inserts records into tables from a given list of dictionaries where key=column-name
def db_put(table,data,where='id'):
	start = datetime.datetime.now()
	inserts = 0
	errors = 0
	updates = 0
	numrec = len(data)
	try:
		collist = get_collist(table)
		log.debug(f'table: {table} collist: {collist} data: {data}')
		for mydict in data:
			z = mydict.copy()
			for x in z: 		#check, if dictionary-item has a corresponding db-column
				if x not in collist: # if no corresponding column
					mydict.pop(x) 	# delete item
			try:
				placeholders = ', '.join(['?'] * len(mydict))
				columns = ', '.join(mydict.keys())
				sql = 'INSERT INTO %s ( %s ) VALUES ( %s )' % (table, columns, placeholders)
				log.debug(f'sql: {sql}  mydict: {mydict}')
				mycursor.execute(sql,list(mydict.values()))
				inserts = inserts + 1
			except pyodbc.Error as ex:
				sqlstate = ex.args[0]
				# sqlstate 23000 means primary key violation
				if sqlstate == '23000':
					try:
						columns = ' = ?, '.join(mydict.keys()) + ' = ? '
						sql = 'UPDATE %s SET %s WHERE %s = %s' % (table, columns, where, mydict[where])
						log.debug(f'sql: {sql} --- {list(mydict.values())}')
						mycursor.execute(sql,list(mydict.values()))
						updates = updates + 1
					except Exception as ex:	
						log.error(f'error on updating: sql: {sql} \ex: {ex} \nvalues: {list(mydict.values())}')
						errors = errors + 1
				else:
					log.error(f'error on inserting sql: {sql} \nex: {ex} \values: {list(mydict.values())}')
			if (inserts + updates) % 100 == 0:
				print(inserts,' inserts ',updates, ' updates from ',numrec,' processed')
	except Exception as ex:
		log.error(f'{ex}')
	end = datetime.datetime.now()
	log.info(f'table {table}: {inserts} records written {updates} updated in {(end-start).seconds} seconds')
	print(f'table {table}: {inserts} records written {updates} updated in {(end-start).seconds} seconds')
	return {inserts,updates}

db_init()
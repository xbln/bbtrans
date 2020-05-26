import requests
import json
import logging
import datetime
import time

#logging.basicConfig(level=logging.debug, filename='app.log', filemode='w', format='%(asctime)s %(name)s %(funcName)s() %(lineno)i %(levelname)s %(message)s')
log = logging.getLogger(__name__)

url='https://app01.billbee.de/api/v1/'
header = {'X-Billbee-Api-Key':'FE617A20-5A4D-4FFD-85E3-828B88185C37'}
aut=('martin.esche@gmx.de','ServiceB7')

def get(modul, fromTime='2000-01-01T00:00:00',id='Id',maxpages=0):
	start = datetime.datetime.now()
	page = 0
	totalpage = 1
	success = 0
	error = 0
	try:
		lis = []
		while (page < totalpage) and ((maxpages==0) or (page<maxpages)):
			try:
				page = page + 1
				parms = {'pageSize':'250','modifiedAtMin':fromTime,'page':str(page)}
				r = requests.get(url+modul, headers=header, auth=aut, params=parms)
				if page == 1:
					totalpage = json.loads(r.text)['Paging']['TotalPages']
				lis = lis + json.loads(r.text)['Data']
				time.sleep(0.5)
				print(f'Executing Page {page} of {totalpage} in module {modul} records {len(lis)}')
				#log.fine(f'page {page} processed')
				success = success + 1
				log.debug(f'request: {r.text}')
				# billbee allows only 2 transactions per second
			except Exception as ex:
				error = error + 1
				log.error(f'Read error: {ex}')
	except Exception as ex:
		log.error(f'General error: {ex}')
	end = datetime.datetime.now()
	print(f'module {modul}: {len(lis)} records from {totalpage} pages success {success} errors {error} in {(end-start).seconds} seconds read')
	log.info(f'module {modul}: {len(lis)} records from {totalpage} pages success {success} errors {error} in {(end-start).seconds} seconds read')
	return lis

def get_specific(modul, data, id):
	start = datetime.datetime.now()
	error = 0
	success = 0
	for x in data:
		try:
			u = url + modul + '/' + str(x[id])
			r = requests.get(u, headers=header, auth=aut)
			#if i == 1: logging.debug(f'{module}: r.text: {r.text}')
			j = json.loads(r.text)['Data']
			success = success + 1
			log.debug(f'processing id {id} in {modul} len(result): {len(x)}')
		except Exception as ex:
			error = error + 1
			log.info(f'{ex}')
		# billbee allows only 2 transactions per second
		if (error + success) % 100 == 0:
			print(f'module {modul}: updating success {success} errors {error} from {len(data)}')
			log.info(f'module {modul}: updating success {success} errors {error} from {len(data)}')
			time.sleep(0.5)
	end = datetime.datetime.now()
	log.info(f'module {modul}: {len(data)} records with id {id} success {success} errors {error} in {(end-start).seconds} seconds read')
	print(f'module {modul}: {len(data)} records with id {id} success {success} errors {error} in {(end-start).seconds} seconds read')
	return j

def update_by_id(modul,data):
	start = datetime.datetime.now()
	error = 0
	success = 0
	for x in data:
		try:
			id = x['id']
			u = url + modul + '/' + str(id)
			x.pop('id')
			r = requests.put(u,headers=header, auth=aut, data=x)
			#log.fine(f'id processed {id}')
			success = success + 1
			log.info(f'processed put request: {r.text} \n\n')
		except Exception as ex:
			error = error + 1
			log.error(f'{ex}')
		if (error + success) % 100 == 0:
			print(f'module {modul}: updating success {success} errors {error} from {len(data)}')
			log.info(f'module {modul}: updating success {success} errors {error} from {len(data)}')
			time.sleep(0.5)
	end = datetime.datetime.now()
	log.info(f'module {modul}: {len(data)} records success {success} errors {error} in {(end-start).seconds} seconds updated')
	print(f'module {modul}: {len(data)} records success {success} errors {error} in {(end-start).seconds} seconds updated')

def insert(modul,data):
	start = datetime.datetime.now()
	error = 0
	success = 0
	for x in data:
		try:
			u = url + modul
			r = requests.post(u,headers=header, auth=aut, data=x)
			#log.fine(f'id processed {id}')
			success = success + 1
			log.info(f'processed put request: {r.text} \n\n')
		except Exception as ex:
			error = error + 1
			log.error(f'{ex}')
		if (error + success) % 100 == 0:
			print(f'module {modul}: insert success {success} errors {error} from {len(data)}')
			log.info(f'module {modul}: insert success {success} errors {error} from {len(data)}')
			time.sleep(0.5)
	end = datetime.datetime.now()
	log.info(f'module {modul}: {len(data)} records success {success} errors {error} in {(end-start).seconds} seconds inserted')
	print(f'module {modul}: {len(data)} records success {success} errors {error} in {(end-start).seconds} seconds inserted')
	
	
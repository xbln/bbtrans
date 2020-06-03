import logging
import requests
import json
import datetime
import time

#logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(asctime)s %(name)s %(funcName)s() %(lineno)i %(levelname)s %(message)s')
log = logging.getLogger(__name__)

url='https://www.zohoapis.com/crm/v2/'
request_url = 'https://accounts.zoho.com/oauth/v2/token'
client_id = '1000.JFWITJPS5GFGIHI07CFMJWRDH7MW6H'
client_secret = 'bbe580d99c56f682128d818f6f87a13334f17c99d5'
refresh_token = '1000.98a3c8a0be6e31a02fa63b38b890fe40.fca9ac5a11fec9673e7c855523390687'

def init():
	try:
		r = requests.post(request_url + '?client_id=' + client_id + '&client_secret=' + client_secret + '&grant_type=refresh_token&refresh_token=' + refresh_token)
		j_obj = json.loads(r.text)
		global header
		header = {'Authorization':'Zoho-oauthtoken ' + j_obj["access_token"]}
		print(f'zoho token {j_obj["access_token"]} created')
		log.info(f'zoho token {j_obj["access_token"]} created')
	except Exception as ex:
		log.error(f'Error with zoho token request: {ex}')
		print(f'zoho token creation failure')


def update_by_id(modul,data):
	start = datetime.datetime.now()
	error = 0
	success = 0
	for x in data:
		try:
			id = x['id']
			u = url + modul + '/' + str(id)
			log.debug(f'url created {u}')
			x.pop("id")
			x = {"data":[x]}
			r = requests.put(u, headers=header,json=x)
			j = json.loads(r.text)
			for d in j["data"]:
				if d["code"] == 'SUCCESS':
					success = success + 1
				else:
					error = error + 1
					log.info(f'{r.text}')
		except Exception as ex:
			error = error + 1
			log.error(f'{ex}')
	end = datetime.datetime.now()
	log.info(f'module {modul}: {len(data)} records success {success} errors {error} in {(end-start).seconds} seconds updated')
	print(f'module {modul}: {len(data)} records with id {id} success {success} errors {error} in {(end-start).seconds} seconds updated')
	
def delete_by_id(modul,data):
	start = datetime.datetime.now()
	error = 0
	success = 0
	for x in data:
		try:
			id = x['id']
			u = url + modul + '?ids=' + str(id)
			log.debug(f'url created {u}')
			r = requests.delete(u, headers=header)
			success = success + 1
			log.debug(f'deleted r: {r.text}')
		except Exception as ex:
			error = error + 1
			log.error(f'{ex}')
		#log.fine(f'id processed {id}')
	log.info(f'module {modul}: {len(data)} records success {success} errors {error} in {(end-start).seconds} seconds deleted')
	print(f'module {modul}: {len(data)} records with id {id} success {success} errors {error} in {(end-start).seconds} seconds deleted')

def upsert(modul,data):
	start = datetime.datetime.now()
	success = 0
	error = 0
	n = 0
	maxwrite = 100
	page = 0
	u = url + modul + '/upsert'
	log.debug(f'url created {u} data: {data}')
	while n<len(data):
		page = page + 1
		try:
			z = data[n:n+maxwrite]
			z = {"data":z}
			r = requests.post(u, headers=header,json=z)
			j = json.loads(r.text)
			for d in j["data"]:
				if d["code"] == 'SUCCESS':
					success = success + 1
				else:
					error = error + 1
					log.info(f'{r.text}')
			n= n + maxwrite
		except Exception as ex:
			error = error + 1
			log.error(f'{ex}')
			log.debug(f'data: {d}')
		print(f'module {modul}: upserting page {page} of {len(data)} records success {success} errors {error}')
	end = datetime.datetime.now()
	log.info(f'module {modul}: {len(data)} records success {success} errors {error} in {(end-start).seconds} seconds inserted / updated')
	print(f'module {modul}: {len(data)} records success {success} errors {error} in {(end-start).seconds} seconds inserted / updated')
	return(len(data))

def get(modul,fromTime='2000-01-01T00:00:00',maxpages=0):
	start = datetime.datetime.now()
	try:
		page = 0
		lis = []
		more_records = True
		header['If-Modified-Since'] = str(fromTime)
		while more_records == True and ((maxpages==0) or (page<maxpages)):
			page = page + 1
			r = requests.get(url+modul, headers=header, params={'page':str(page)})
			if r.text != '':
				# check if more pages exist 
				more_records = json.loads(r.text)['info']['more_records']
				lis = lis + json.loads(r.text)['data']
				print(f'module {modul}: reading page {page} of records {len(lis)}')
			else:
				more_records = False
			log.debug(f'request: {r.text}')
	except Exception as ex:
		log.error(f'{ex}')
	end = datetime.datetime.now()
	print(f'module {modul}: {len(lis)} records read from {page} pages in {(end-start).seconds} seconds')
	log.info(f'module {modul}: {len(lis)} records read from {page} pages in {(end-start).seconds} seconds')
	return(lis)

def get_config(modul='Modules'):
	try:
		if modul == 'Modules':
			u = url + 'settings/modules'
		else:
			u = url + 'settings/fields?module=' + modul
		r = requests.get(u, headers=header)
		log.debug(f'processed get request: {r.text}')
		t = r.text
	except Exception as ex:
		log.error(f'Error with token request: {ex}')
	log.info(f'ready processing')
	return(t)

init()
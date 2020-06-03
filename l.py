import requests
import logging
import zoho
import bill
import db
import flatten_dict
import json
import datetime
import pandas as pd



logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(asctime)s %(name)s %(funcName)s() %(lineno)i %(levelname)s %(message)s')
#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(name)s %(levelname)s %(message)s') 
log = logging.getLogger(__name__)

def make_orderitems(lis):
	new_lis = []
	for dict in lis:
		try:
			log.debug(f": Orderitems : {dict['OrderItems']}")
			new_dict = json.loads(dict['OrderItems'])
			for d in new_dict:
				d['xOrderRefId'] = dict['BillBeeOrderId']
				new_lis.append(d)
			log.debug(f": JSON Orderitems : {new_dict}")
		except Exception as ex:
			log.error(f": {ex}")
	log.info(f": processed {len(new_lis)} records")
	return new_lis

def flatten_list(lis):
	l_result = []
	try:
		for d in lis:
			d = flatten_dict.flatten(d,'underscore',False,(list,))
			l_result.append(d)
	except Exception as ex:
		log.error(f": {ex}")
	return l_result

def last_modified(table):
	result = db.db_select('select max(timestamp) from ' + table)
	if result is None:
		result = '2000-05-19T00:00:00'
	else:
		result = str(result[0][0]).replace(' ','T')[:19]
	log.info(f'table {table} was last modified at {result}')
	print(f'table {table} was last modified at {result}')
	return(result)

def get_zoho_accounts():
	t = last_modified('z_accounts_')
	x = zoho.get('Accounts',t)
	if len(x) > 0:
		x = flatten_list(x)
		db.db_put('z_accounts',x)

def get_all_zoho_accounts():
	x = zoho.get('Accounts')
	if len(x) > 0:
		x = flatten_list(x)
		db.db_truncate('z_accounts')
		db.db_put('z_accounts',x)

def get_zoho_contacts():
	t = last_modified('z_contacts_')
	x = zoho.get('Contacts',t)
	if len(x) > 0:
		x = flatten_list(x)
		db.db_put('z_contacts',x)

def get_all_zoho_contacts():
	x = zoho.get('Contacts')
	if len(x) > 0:
		x = flatten_list(x)
		db.db_truncate('z_contacts')
		db.db_put('z_contacts',x)

def get_zoho_deals():
	t = last_modified('z_deals_')
	x = zoho.get('deals',t)
	if len(x) > 0:
		x = flatten_list(x)
		db.db_put('z_deals',x)

def get_all_zoho_deals():
	t = last_modified('z_deals')
	x = zoho.get('deals')
	if len(x) > 0:
		x = flatten_list(x)
		db.db_truncate('z_deals')
		db.db_put('z_deals',x)

def eliminate_z_accounts_doublettes():
	x=db.db_get('v_z_accounts_doublettes')
	if len(x) > 0:
		zoho.update_by_id('Accounts',x)
		get_zoho_accounts()

def reset_change_in_billbee():
	x=db.db_get('v_reset_accounts_change_in_billbee')
	if len(x) > 0:
		zoho.update_by_id('Accounts',x)
	x=db.db_get('v_reset_contacts_change_in_billbee')
	if len(x) > 0:
		zoho.update_by_id('Contacts',x)

def update_bill():
	x = db.db_get('v_update_customer_addresses')
	if len(x) > 0:
		bill.update_by_id('customer-addresses',x)
	x = db.db_get('v_update_customers')
	if len(x) > 0:
		bill.update_by_id('customers',x)
	x=db.db_get('v_insert_customers')
	x_neu = []
	for y in x:
		y["Address"] = {"Company":y["Name"],"Email":y["Email"],"Tel1":y["Tel1"],"Tel2":y["Tel2"],"AddressType":y["A_AddressType"],
			"PriceGroupId":y["A_PriceGroupId"],"Zip":y["A_Zip"],"City":y["A_City"],"CountryCode":y["A_CountryCode"],"State":y["A_State"],
			"Street":y["A_Street"],"Housenumber":y["A_Housenumber"],"AddressType":y["A_AddressType"]}
		y.pop("A_Zip")
		y.pop("A_City")
		y.pop("A_CountryCode")
		y.pop("A_State")
		y.pop("A_Street")
		y.pop("A_Housenumber")
		y.pop("A_PriceGroupId")
		y.pop("A_AddressType")
		x_neu.append(y)
	if len(x_neu) > 0:
		bill.insert('customers',x_neu)

def get_all_bill_customer():
	x = bill.get('customers')
	if len(x) > 0:
		db.db_truncate('b_customer')
		db.db_put('b_customer',x)

def get_all_bill_address():
	x = bill.get('customer-addresses')
	if len(x) > 0:
		db.db_truncate('b_address')
		db.db_put('b_address',x)

def get_bill_order():
	t = last_modified('b_order_')
	x = bill.get('orders',t,'BillBeeOrderId')
	if len(x) > 0:
		x = flatten_list(x)
		db.db_put('b_order',x)
		x = make_orderitems(x)
		if len(x) > 0:
			x = flatten_list(x)
			db.db_put('b_orderitem',x)

def get_all_bill_order():
	x = bill.get('orders','2000-01-01T00:00:00','BillBeeOrderId')
	if len(x) > 0:
		x = flatten_list(x)
		db.db_truncate('b_order')
		db.db_put('b_order',x)
		x = make_orderitems(x)
		if len(x) > 0:
			x = flatten_list(x)
			db.db_truncate('b_orderitem')
			db.db_put('b_orderitem',x)

def update_zoho_accounts():
	x=db.db_get('v_update_accounts')
	if len(x) > 0:
		x = flatten_list(x)
		zoho.upsert('Accounts',x)
		get_zoho_accounts()

def update_all_zoho_accounts():
	x=db.db_get('v_update_accounts')
	if len(x) > 0:
		x = flatten_list(x)
		zoho.upsert('Accounts',x)
		get_all_zoho_accounts()

def update_zoho_contacts():
	x=db.db_get('v_update_contacts')
	if len(x) > 0:
		x = flatten_list(x)
		zoho.upsert('Contacts',x)
		get_zoho_contacts()

def update_all_zoho_contacts():
	x=db.db_get('v_update_contacts')
	if len(x) > 0:
		x = flatten_list(x)
		zoho.upsert('Contacts',x)
		get_all_zoho_contacts()

def update_zoho_deals():
	x=db.db_get('v_update_deals')
	if len(x) > 0:
		x = flatten_list(x)
		zoho.upsert('Deals',x)
		get_zoho_deals()

def update_all_zoho_deals():
	x=db.db_get('v_update_deals')
	if len(x) > 0:
		x = flatten_list(x)
		zoho.upsert('Deals',x)
		get_all_zoho_deals()

def get_zoho_data():
	get_zoho_accounts()
	get_zoho_contacts()
	get_zoho_deals()

def get_all_zoho_data():
	get_all_zoho_accounts()
	get_all_zoho_contacts()
	get_all_zoho_deals()

def update_zoho_data():
	update_zoho_accounts()
	update_zoho_contacts()
	update_zoho_deals()

def update_all_zoho_data():
	update_all_zoho_accounts()
	update_all_zoho_contacts()
	update_all_zoho_deals()

def get_bill_data():
	get_all_bill_customer()
	get_all_bill_address()
	get_bill_order()

def get_all_bill_data():
	get_all_bill_customer()
	get_all_bill_address()
	get_all_bill_order()

def backup_tables():
	db.db_copy('b_customer')
	db.db_copy('b_address')
	db.db_copy('b_order')
	db.db_copy('b_orderitem')
	db.db_copy('z_accounts')
	db.db_copy('z_contacts')
	db.db_copy('z_deals')

def update_all():
	get_all_zoho_data()
	update_bill()
	get_all_bill_data()
	update_all_zoho_data()
	reset_change_in_billbee()
	backup_tables()

def update():
	get_zoho_data()
	update_bill()
	get_bill_data()
	update_zoho_data()
	reset_change_in_billbee()
	backup_tables()

update_all()
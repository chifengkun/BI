#-*- encoding: utf-8 -*-
'''
Created on 2022-03-31 12:10:32

@author: chifeng
'''
import time
import yagmail
from tempfile import TemporaryDirectory
from django.core.cache import cache
from datetime import datetime
import pandas as pd

def send_email(data):
	
	cache_data = cache.get(data['sid'])
	orders_df = pd.read_json(cache_data,orient='table')
	dt = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
	file_path = f'D:/{dt}.csv'

	orders_df.to_csv(file_path,encoding='gbk')
	yag = yagmail.SMTP(user='2471033989@qq.com',host='smtp.qq.com')
	content = ['订单数据见附件',file_path]
	yag.send(data['email'],data['subject'],content)

	return True

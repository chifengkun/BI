import json
import uuid
import pandas as pd
from django.utils.timezone import datetime
from django.core.paginator import Paginator
from django.core.cache import cache
from django.shortcuts import render
from django.utils.timezone import zoneinfo
from django.http import JsonResponse
from django_pandas.io import read_frame
from .models import Order,Course, SearchRecord
from django_q.tasks import async_task

from . import df_analysis


STATUS_TYPE_CHOICES = dict([
		('PE','未支付'),
		('SU','支付成功'),
		('CA','取消'),
		('OV','过期'),
		('RE','退款')
	])
op_to_lookup = {
	'equal' : 'exact',
	'not_equal' : 'exact',
	'like' : 'contains',
	'starts_with': 'startswith',
	'ends_with' : 'endswith',
	'less' : 'lt',
	'less_or_equal' : 'lte',
	'greater' : 'gt',
	'greater_or_equal':'gte',
	'between' : 'range',
	'not_between' : 'range',
	'select_equals' : 'exact',
	'select_not_equals' : 'exact',
	'select_any_in' : 'in',
	'select_not_any_in':'in',
}

df_analysis_function_map ={
	'pie': df_analysis.pie_analyse_df,
	'bar': df_analysis.bar_analyse_df,
	'line': df_analysis.line_analyse_df,
	'total_income':df_analysis.total_income
}

def index(request):
	Order_fields = [{'name':field.name,'label':field.verbose_name} for field in Order._meta.fields]
	return render(request,'dashboard/index.html',{'Order_fields': Order_fields})

def post_order(request):
	data = json.loads(request.body.decode())
	page = data.get('page',1)
	per_page = data.get('per_page',10)

	conditions = data.get('conditions',{})
	orders = analyse_conditions(conditions) if len(conditions) >0 else Order.objects.all()#取数据
	orders = orders.order_by('id')

	paginator = Paginator(orders,per_page)#分页
	page_obj = paginator.get_page(page)
	items = list(page_obj.object_list.values())
	for item in items:#对数据进行调整
		item['course'] = Course.objects.get(id=item['course_id']).title
		item['creat_time'] = item['creat_time'].astimezone(zoneinfo.ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
		if item['pay_time'] is not None:
			item['pay_time'] = item['pay_time'].astimezone(zoneinfo.ZoneInfo('Asia/shanghai')).strftime("%Y-%m-%d %H:%M:%S")
		item['status'] = STATUS_TYPE_CHOICES[item['status']]

	data={
		'status':0,
		'msg':'ok',
		'data': {
			'total':orders.count(),
			'items':items
		}
	}
	if len(conditions)>0:
		# searchrecord = SearchRecord.objects.create(conditions=json.dumps(conditions))
		# searchrecord.objs.add(*orders)
		sid = str(uuid.uuid4())
		data['data']['sid'] = sid

		orders_df = read_frame(orders,coerce_float=True)
		orders_df["creat_time"] = orders_df["creat_time"].apply(lambda t: t.timestamp())
		# if not orders_df["pay_time"].all():
		try: #pay_time =NoneType 
			orders_df["pay_time"] = orders_df["pay_time"].apply(lambda t: t.timestamp())
		except:
			pass
		orders_json = orders_df.to_json(orient='table')
		cache.set(sid,orders_json,600)

	return JsonResponse(data)

def analyse_conditions(conditions):#分析写入条件
	final_query = None
	for child in conditions['children']:
		if 'children' in child:
			child_query = analyse_conditions(child)
		else:
			model,field = child['left']['field'].split('.')
			lookup = op_to_lookup[child['op']]
			right = child['right']

			if field.endswith('time'):
				if isinstance(right,list):
					start_dt, end_dt = right
					start_dt = datetime.strptime(start_dt,'%Y-%m-%dT%H:%M:%S%z')
					end_dt = datetime.strptime(end_dt,'%Y-%m-%dT%H:%M:%S%z')
					right = (start_dt,end_dt)
				else:
					right = datetime.strptime(right,'%Y-%m-%dT%H:%M:%S%z')

			if model == 'order':
				params = {f'{field}__{lookup}':right}
			else:
				params = {f'{model}__{field}__{lookup}':right}

			if 'not' in child['op']:
				child_query = Order.objects.exclude(**params)
			else:
				child_query = Order.objects.filter(**params)

		if final_query is None:
			final_query = child_query
		elif conditions['conjunction'] == 'and':
			final_query = final_query & child_query
		else:
			final_query = final_query | child_query

	return final_query

def post_chart(request):#更新数据填充图表
	data_type = request.GET['type']
	data = {
		'status':0,
		'msg':"ok",
		"data":{}
	}
	sid = request.GET.get('sid','')
	if len(sid) == 0:
		return JsonResponse(data)

	# orders = SearchRecord.objects.get(id=sid).objs.all()#取manytomanyfield（objs）的外键链接的数据库数据写法
	# orders_df = read_frame(orders,coerce_float=True)
	cache_data = cache.get(sid)
	orders_df = pd.read_json(cache_data,orient='table')
	data['data'] = df_analysis_function_map[data_type](orders_df)#不同的类型图表，不同的分析方式，不同的字典key
	return JsonResponse(data)

def send_email_api(request):
	sid=request.GET.get('sid')
	body_data = json.loads(request.body.decode())
	email =body_data.get('email')
	email_data = {
		'sid':sid,
		'email':email,
		'subject':'您的订单数据已生成'
	}
	async_task('dashboard.tasks.send_email',email_data)
	data = {
		'status':0,
		'msg':'邮件发送中',
		'data' : {}
	}
	return JsonResponse(data)
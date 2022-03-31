import pandas as pd

def pie_analyse_df(dataframe):
	counts = dataframe['out_vendor'].value_counts()
	platform_data = [{'name':name,'value':value} for name,value in counts.items()]
	return {'platform_data':platform_data}

def line_analyse_df(dataframe):
	orders_df = dataframe[dataframe['pay_time'].notna()]
	if not orders_df.index.to_list():#如果是未支付datetime全部为空直接返回空的内容，防止报错
		return {
			"x_data":'',
			"y_data":''
		}
	orders_df['pay_time'] = orders_df['pay_time'].dt.tz_localize('Asia/shanghai')
	orders_df['pay_time'] = orders_df['pay_time'].dt.date
	startd , endd = orders_df['pay_time'].min(),orders_df['pay_time'].max()
	dates_index = pd.date_range(startd,endd)
	daily_income = pd.Series(index=dates_index,dtype='float64').fillna(0.0)
	groupby_pay_time_df = orders_df[['pay_time','price']].groupby('pay_time').sum()
	daily_income += groupby_pay_time_df['price']
	daily_income = daily_income.fillna(0.0)
	x_data = [dt.strftime("%Y-%m-%d") for dt in daily_income.index]
	y_data = daily_income.values.tolist()
	return {"x_data":x_data,"y_data":y_data}

def bar_analyse_df(dataframe):
	product_line_income = dataframe[['product_line','price']].groupby('product_line').sum()
	product_line_income = product_line_income.sort_values(by='price',ascending=False)
	data = {
		'x_data':product_line_income.index.to_list(),
		'y_data':product_line_income['price'].to_list()
	}
	return data

def total_income(dataframe):
	total = dataframe['price'].sum()
	return {'total_income':total}
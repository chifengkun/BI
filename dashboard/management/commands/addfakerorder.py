import random
import pytz
from datetime import timedelta

from decimal import Decimal
from django.core.management.base import BaseCommand,CommandError
from faker import Faker
import uuid
from dashboard.models import Order,Course

fake = Faker('zh_CN')
class Command(BaseCommand):
	help = '添加虚构数据'

	def add_arguments(self,parser):
		parser.add_argument('number',type=int)

	def handle(self,*args,**options):
		number = options['number']
		courses = Course.objects.all()
		for i in range(number):
			if i %50 ==0:
				self.stdout.write(self.style.SUCCESS(f'正在添加第{i+1}条数据!'))
			course = random.choice(courses)
			creat_time = fake.date_time_between(start_date='-1y',tzinfo=pytz.timezone('Asia/shanghai'))
			product_line = random.choice(['A产品线','B产品线','C产品线','D产品线'])
			user_id = str(uuid.uuid4().int)
			user_mobile = str(fake.phone_number())
			user_address = fake.address()
			price = course.price
			status = random.choice(['PE']*10+['SU']*50+['CA']*3+['OV']*3+['RE']*3)
			if status == 'SU':
				pay_time = creat_time + timedelta(minutes=random.randint(2,60*24))
				pay_channel = random.choice(['wechat','alipay'])
				transaction_serial_number = str(uuid.uuid4().int)
				fee_price = price * Decimal(0.03)
			else:
				pay_time = None
				pay_channel = None
				transaction = None
				fee_price = Decimal(0)

			refund_price = course.price if status == 'RE' else Decimal(0)
			out_vendor = random.choice(['web','ios','android'])

			oid = creat_time.strftime('%y%m%d%H%M%S') + str(course.cid)[-3:] + user_id[-3:]
			oid += f'{random.randint(0,99):02d}'
			order = Order(
				oid=oid,
				product_line=product_line,
				course=course,
				creat_time=creat_time,
				user_id=user_id,
				user_mobile=user_mobile,
				user_address=user_address,
				pay_time=pay_time,
				pay_channel=pay_channel,
				status=status,
				transaction_serial_number=transaction_serial_number,
				price=price,
				fee_price=fee_price,
				refund_price=refund_price,
				out_vendor=out_vendor
				)
			order.save()
		self.stdout.write(self.style.SUCCESS(f'成功添加{number}个数据！'))
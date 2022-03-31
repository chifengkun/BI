from django.db import models

class Order(models.Model):
	oid = models.CharField('订单ID',max_length=20,editable=False)
	product_line = models.CharField('产品线',max_length=20)
	course = models.ForeignKey('Course',verbose_name='课程',on_delete=models.SET_NULL,blank=True,null=True)
	creat_time = models.DateTimeField('下单时间')
	user_id = models.CharField('用户ID',max_length=40)
	user_mobile = models.CharField('手机号',max_length=20)
	user_address = models.CharField('地址',max_length=200,blank=True,null=True)
	pay_time = models.DateTimeField('支付时间',blank=True,null=True)
	pay_channel = models.CharField('支付方式',max_length=20,blank=True,null=True)
	STATUS_TYPE_CHOICES = [
		('PE','未支付'),
		('SU','支付成功'),
		('CA','取消'),
		('OV','过期'),
		('RE','退款')
	]
	status = models.CharField('订单状态',max_length=2,choices=STATUS_TYPE_CHOICES,default='PE')
	transaction_serial_number = models.CharField('交易流水号',max_length=40,editable=False,blank=True,null=True)
	price = models.DecimalField('金额',max_digits=10,decimal_places=2)
	fee_price = models.DecimalField('手续费',max_digits=10,decimal_places=2,blank=True,null=True)
	refund_price = models.DecimalField('退款金额',max_digits=10,decimal_places=2,blank=True,null=True)
	out_vendor = models.CharField('来源',max_length=20,blank=True,null=True)

	def __str__(self):
		return self.oid

	class Meta:
		verbose_name = '订单'

class Course(models.Model):
	cid = models.IntegerField('课程ID')
	title = models.CharField('课程名称',max_length=30)
	price = models.DecimalField('金额',max_digits=10,decimal_places=2)
	COURSE_TYPE_CHOICES = [
	('F','免费课'),
	('P','付费课')
	]
	course_type = models.CharField('付费类型',max_length=1,choices=COURSE_TYPE_CHOICES,default='F')
	def __str__(self):
		return str(self.title)

	class Meta:
		verbose_name = '课程'

class SearchRecord(models.Model):
	conditions = models.TextField('查询条件',blank=True,null=True)
	objs = models.ManyToManyField('Order',blank=True)

	class Meta:
		verbose_name='搜索记录'
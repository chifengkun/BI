from django.urls import path
from . import views

urlpatterns =[
	path('',views.index),
	path('api/post_order',views.post_order),
	path('api/post_chart',views.post_chart),
	path('api/send_email',views.send_email_api)
]
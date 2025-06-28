from django.urls import path
from mainapp import views

app_name = 'mainapp'

urlpatterns = [
    path('signin/',views.signin,name='signin'),
    path('',views.web_page,name='web_page')
]

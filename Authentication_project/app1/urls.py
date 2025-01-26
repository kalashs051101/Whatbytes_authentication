from django.contrib import admin
from django.urls import path
from app1.views import *

urlpatterns = [
    path('',home_view,name='home'),
    path('change_password/',change_password_view,name='change_password'),
    path('dashboard/',dashboard_view,name='dashboard'),
    path('login/',login_view,name='login'),
    path('profile/',profile_view,name='profile'),
    path('signup/',signup_view,name='signup'),
    path('logout/', logout_view, name='logout'),
    path('forgot_password/', forgot_password_view, name='forgot_password'),
    path('reset-password/<str:token>/', reset_password_view, name='reset_password'),
]

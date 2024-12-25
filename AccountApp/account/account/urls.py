from django.contrib import admin
from django.urls import path
from app_account01 import views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('enroll/', views.enroll),
    path('login/', views.login_user),
    path('index/', views.index),
    path('forget/', views.forget),
    path('forget/<str:name>/', views.forget_reset),
    path('history/', views.history),
    path('chart/', views.chart),
    path('chart/type/', views.chart_type),
    path('chart/month/', views.chart_month),

]

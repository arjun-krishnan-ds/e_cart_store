from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create_account/', views.signup_view, name='signup'),
    path('log_in/', views.login_view, name='signin'),
    path('logged_in/', views.dashboard_view, name='dashboard'),
    path('log_out/', views.logout_view, name='logout'),
    
]

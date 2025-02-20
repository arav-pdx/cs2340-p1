from django.urls import path
from . import views
urlpatterns = [
    path('signup', views.signup, name='accounts.signup'),
    path('login/', views.login, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
    path('orders/', views.orders, name='accounts.orders'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),

    path('reset_password/<uuid:token>/', views.reset_password, name='reset_password_confirm'),

    path('forgot_password/confirmation/', views.forgot_password_confirmation, name='forgot_password_confirmation'),
]
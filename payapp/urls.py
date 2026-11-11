from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.send_money, name='send_money'),
    path('request/', views.request_money, name='request_money'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('request/pay/<int:request_id>/', views.pay_request, name='pay_request'),
    path('request/reject/<int:request_id>/', views.reject_request, name='reject_request'),
    path('admin/accounts/', views.admin_accounts, name='admin_accounts'),
    path('admin/transactions/', views.admin_transactions, name='admin_transactions'),
    path('admin/create-admin/', views.admin_create_admin, name='admin_create_admin'),
]

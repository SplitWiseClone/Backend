from django.urls import re_path, path
from . import views

urlpatterns = [
    # re_path(r'^(?P<transaction_id>\w+)/$', views.detail, name='detail'),
    # path('addExpense/', views.addExpense, name='addExpense'),
    # path('listAllTransactions/', views.listAllTransactions, name='list_all_transactions'),
    path('', views.index, name='index'),
]

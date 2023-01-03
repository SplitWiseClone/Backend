"""splitwise URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, re_path, path
from django.views.generic import TemplateView

import MoneyTransact.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include("django.contrib.auth.urls")),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    # path('balance/', include('MoneyTransact.urls'), name='balance'),
    path('addExpense/', MoneyTransact.views.addExpense, name='addExpense'),
    path('listAllTransactions/', MoneyTransact.views.listAllTransactions, name='list_all_transactions'),
    path('listAllTransactions/deleteTransaction/<int:transaction_id>', MoneyTransact.views.deleteTransaction, name='deleteTransaction'),
    path('listAllTransactions/editTransaction/<int:transaction_id>', MoneyTransact.views.editTransaction, name='editTransaction'),
    path('overAllBalance/', MoneyTransact.views.overAllBalance, name='over_all_balance'),
]

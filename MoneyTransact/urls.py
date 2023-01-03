from django.urls import re_path, path
from . import views
from .views import UserListView, AddExpenseView, ListAllTransactionsView, DeleteTransactionView, UpdateTransactionView, \
    OverAllBalanceView, GetTransactionView, FilterTransactionsOnCategoryView

urlpatterns = [
    path('', views.index, name='index'),
    path('users/list/', UserListView.as_view(), name='user_list'),
    path('addExpense/', AddExpenseView.as_view(), name='addExpense'),
    path('listAllTransactions/', ListAllTransactionsView.as_view(), name='list_all_transactions'),
    path('filterTransactions/<str:category>', FilterTransactionsOnCategoryView.as_view(), name='filter_transactions'),
    path('deleteTransaction/<int:transaction_id>', DeleteTransactionView.as_view(), name='deleteTransaction'),
    path('getTransaction/<int:transaction_id>', GetTransactionView.as_view(), name='getTransaction'),
    path('editTransaction/<int:transaction_id>', UpdateTransactionView.as_view(), name='editTransaction'),
    path('overAllBalance/', OverAllBalanceView.as_view(), name='over_all_balance'),
]

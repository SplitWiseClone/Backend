import json

import jsonpickle
from django.shortcuts import render

from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.renderers import UserRenderer
from .forms import TransactionForm
from django.http import HttpResponse, HttpResponseRedirect
from .models import Transaction
from django.contrib.auth.models import User
from .serializers import UserSerializer, TransactionSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status


def index(request):
    return HttpResponse("<h1> Your Balance sheet </h1> ")


class UserListView(APIView):
    """
    List all users, or create a new user.
    """
    renderer_classes = (UserRenderer,)

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class AddExpenseView(APIView):
    """
    Add a new expense.
    """
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (UserRenderer,)

    def post(self, request, format=None):
        print("request.data ", request.data)
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class ListAllTransactionsView(APIView):
    """
    List all transactions, or create a new transaction.
    """
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (UserRenderer,)

    def get(self, request, format=None):
        my_transactions = (Transaction.objects.filter(taker=str(request.user.id), active=True)
                           | Transaction.objects.filter(giver=str(request.user.id), active=True)).distinct()
        transactions_details = list()
        for transaction in my_transactions:
            print("transaction ", transaction)
            takers_set = set()
            for takers in transaction.taker.all():
                takers_set.add(takers.username)
            print("takers_set ", takers_set)
            individual_transactions = {
                "id": transaction.id,
                "giver": transaction.giver.username,
                "takers": takers_set,
                "amount": transaction.amount,
                "lent": 0,
                "borrowed": 0,
                "num_people": len(takers_set),
                "description": transaction.description,
                "active": transaction.active,
                "category": transaction.category,
                "date": transaction.date.__str__(),
            }
            if request.user.username == transaction.giver.username:
                if request.user.username in takers_set:
                    individual_transactions['lent'] = transaction.amount - (transaction.amount / (len(takers_set)))
                    individual_transactions['borrowed'] = transaction.amount / (len(takers_set))
                else:
                    individual_transactions['lent'] = transaction.amount
            elif request.user.username in takers_set:
                individual_transactions['borrowed'] = (transaction.amount / (len(takers_set)))

            transactions_details.append(individual_transactions)
            # print("transaction dictionary ", transactions_details)
        print("My Transactions:: ", transactions_details)
        return JsonResponse(json.dumps(transactions_details, cls=SetEncoder), safe=False)


class DeleteTransactionView(APIView):
    """
    Delete a transaction.
    """
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (UserRenderer,)

    def delete(self, request, transaction_id, format=None):
        transaction = Transaction.objects.get(id=transaction_id)
        print("transaction ", transaction)
        transaction.active = False
        transaction.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateTransactionView(APIView):
    """
    Update a transaction.
    """
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (UserRenderer,)

    def put(self, request, transaction_id, format=None):
        transaction = Transaction.objects.get(id=transaction_id)
        print("transaction ", transaction)
        serializer = TransactionSerializer(transaction, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OverAllBalanceView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (UserRenderer,)

    def get(self, request, format=None):
        borrowed_from = dict()
        lent_to = dict()
        borrowed_transactions = (Transaction.objects.filter(taker=str(request.user.id), active=True)).distinct()
        lent_transactions = (Transaction.objects.filter(giver=str(request.user.id), active=True)).distinct()
        for transaction in borrowed_transactions:
            if transaction.giver.username != request.user.username:
                if transaction.giver.username not in borrowed_from:
                    borrowed_from[transaction.giver.username] = transaction.amount / len(transaction.taker.all())
                else:
                    borrowed_from[transaction.giver.username] += (transaction.amount / len(transaction.taker.all()))
        for transaction in lent_transactions:
            for taker in transaction.taker.all():
                if taker.username != request.user.username:
                    if taker.username not in lent_to:
                        lent_to[taker.username] = transaction.amount / len(transaction.taker.all())
                    else:
                        lent_to[taker.username] += (transaction.amount / len(transaction.taker.all()))
                    if taker.username in borrowed_from:
                        if lent_to[taker.username] > borrowed_from[taker.username]:
                            lent_to[taker.username] -= borrowed_from[taker.username]
                            borrowed_from[taker.username] = 0
                        else:
                            borrowed_from[taker.username] -= lent_to[taker.username]
                            lent_to[taker.username] = 0
        return JsonResponse({'borrowed_from': borrowed_from, 'lent_to': lent_to})


# def overAllBalance(request):
#     if request.user.id is None:
#         return render(request, '../templates/MoneyTransact/overAllBalance.html', {
#             'borrowed_from': {},
#             'lent_to': {}
#         })
#     borrowed_from = dict()
#     lent_to = dict()
#     borrowed_transactions = (Transaction.objects.filter(taker=str(request.user.id), active=True)).distinct()
#     lent_transactions = (Transaction.objects.filter(giver=str(request.user.id), active=True)).distinct()
#     for transaction in borrowed_transactions:
#         if transaction.giver.username != request.user.username:
#             if transaction.giver.username not in borrowed_from:
#                 borrowed_from[transaction.giver.username] = transaction.amount / len(transaction.taker.all())
#             else:
#                 borrowed_from[transaction.giver.username] += (transaction.amount / len(transaction.taker.all()))
#     for transaction in lent_transactions:
#         for taker in transaction.taker.all():
#             if taker.username != request.user.username:
#                 if taker.username not in lent_to:
#                     lent_to[taker.username] = transaction.amount / len(transaction.taker.all())
#                 else:
#                     lent_to[taker.username] += (transaction.amount / len(transaction.taker.all()))
#                 if taker.username in borrowed_from:
#                     if lent_to[taker.username] > borrowed_from[taker.username]:
#                         lent_to[taker.username] -= borrowed_from[taker.username]
#                         borrowed_from[taker.username] = 0
#                     else:
#                         borrowed_from[taker.username] -= lent_to[taker.username]
#                         lent_to[taker.username] = 0
#
#     return render(request, '../templates/MoneyTransact/overAllBalance.html', {
#         'borrowed_from': borrowed_from,
#         'lent_to': lent_to
#     })

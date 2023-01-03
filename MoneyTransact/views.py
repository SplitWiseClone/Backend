from django.shortcuts import render

from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import TransactionForm
from django.http import HttpResponse, HttpResponseRedirect
from .models import Transaction


def index(request):
    return HttpResponse("<h1> Your Balance sheet </h1> ")


def addExpense(request):
    print(request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES)
        # get the data from request from frontend
        if form.is_valid():
            # form.giver = request.user
            # print("form ", form.fields)
            transaction = form.save()
            # transaction.giver = request.user
            transaction.save()
            print("transaction ", transaction)
            return redirect('list_all_transactions')
    else:
        form = TransactionForm()
    return render(request, '../templates/MoneyTransact/addExpense.html', {
        'form': form
    })


def listAllTransactions(request):
    if request.user.id is None:
        return render(request, '../templates/MoneyTransact/listAllTransactions.html', {
            'transactions': {}
        })
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
            "active": transaction.active
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
    return render(request, '../templates/MoneyTransact/listAllTransactions.html', {
        'transactions': transactions_details
    })


def deleteTransaction(request, transaction_id):
    # if request.method == 'POST':
    transaction = Transaction.objects.get(id=transaction_id)
    print("transaction ", transaction)
    transaction.active = False
    transaction.save()
    return HttpResponseRedirect(reverse('list_all_transactions'))


def editTransaction(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, instance=transaction)
        if form.is_valid():
            transaction = form.save()
            transaction.save()
            return redirect('list_all_transactions')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, '../templates/MoneyTransact/editTransaction.html', {
        'form': form
    })


def overAllBalance(request):
    if request.user.id is None:
        return render(request, '../templates/MoneyTransact/overAllBalance.html', {
            'borrowed_from': {},
            'lent_to': {}
        })
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

    return render(request, '../templates/MoneyTransact/overAllBalance.html', {
        'borrowed_from': borrowed_from,
        'lent_to': lent_to
    })

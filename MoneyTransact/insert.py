from .models import Transaction


def simplify(giver, taker, amount_given, amount_taken):
    No_giver = len(giver)
    No_taker = len(taker)
    factor = sum(amount_taken)
    ratio = [float(x) / factor for x in amount_taken]
    for i in range(No_giver):
        amount_sofar = 0
        # print "---" , amount_given[i]
        for j in range(No_taker):
            if j != No_taker - 1:
                amount = ratio[j] * amount_given[i]
                amount_sofar = amount_sofar + amount
            else:
                amount = amount_given[i] - amount_sofar
            print(giver[i], "-->", taker[j], ':', amount)
            if giver[i] != taker[j]:
                a = Transaction(currency="Rs", taker=taker[j], giver=giver[i], amount=amount, description="asdas");
                a.clean()
                a.save()

# def specified_insert():

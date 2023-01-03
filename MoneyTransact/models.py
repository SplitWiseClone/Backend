from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from datetime import date


# Create your models here.

class Transaction(models.Model):
    RUPEES = 'Rs'
    DOLLAR = '$'
    OTHERS = 'o/w'
    currency_options = (
        (RUPEES, 'Rupees'),
        (DOLLAR, 'Dollar'),
        (OTHERS, 'Others'),
    )
    category_options = (
        ('Food', 'Food'),
        ('Travel', 'Travel'),
        ('Shopping', 'Shopping'),
        ('Entertainment', 'Entertainment'),
        ('Others', 'Others'),
    )
    currency = models.CharField(max_length=3,
                                choices=currency_options,
                                default=RUPEES,
                                )
    giver = models.ForeignKey('auth.User', related_name='giver', on_delete=models.CASCADE)
    taker = models.ManyToManyField('auth.User', related_name='taker')
    amount = models.IntegerField(
        default=0,
    )
    description = models.CharField(max_length=250)
    active = models.BooleanField(default=True)
    date = models.DateField(default=date.today, blank=True)
    category = models.CharField(max_length=20,
                                choices=category_options,
                                default='Others',
                                )

    def __str__(self):
        return "giver : " + self.giver.username + " taker : " + [x.username for x in
                                                                 self.taker.all()].__str__() + " amount:  " + str(
            self.amount) + " description: " + self.description + " date: " + self.date.__str__()
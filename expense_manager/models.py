from django.db import models

class Expense(models.Model):
    merchant = models.CharField(max_length=255)
    expense = models.DecimalField(max_digits=10, decimal_places=2)

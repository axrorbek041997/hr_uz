from django.db import models
from app.models import Company
    
class PaymentAmount(models.Model):
    amount = models.DecimalField(max_digits=14, decimal_places=2)

    def __str__(self):
        return f'{self.amount}'

class FreeTrial(models.Model):
    days = models.IntegerField(default=7)

    def __str__(self):
        return f'{self.days}'
    
class PaymeToken(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='payme_tokens')
    token = models.TextField(blank=True)
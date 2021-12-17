from django.contrib import admin

from .models import *

@admin.register(PaymentAmount)
class PaymentAmount(admin.ModelAdmin):
    list_display = ('amount',)
    
@admin.register(FreeTrial)
class FreeTrial(admin.ModelAdmin):
    list_display = ('days',)
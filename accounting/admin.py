from django.contrib import admin
from .models import Deposite, Subscriptionof, Earning, Expenditure

class DepositeAdmin(admin.ModelAdmin):
    list_display = ('member_name','sub_of', 'amount')
# Register your models here.
admin.site.register(Deposite,DepositeAdmin)
admin.site.register(Subscriptionof)
admin.site.register(Earning)
admin.site.register(Expenditure)
from django.contrib import admin
from .models import  Book, OrderedBook, Order

# Register your models here.

admin.site.register(Book)
admin.site.register(OrderedBook)
admin.site.register(Order)

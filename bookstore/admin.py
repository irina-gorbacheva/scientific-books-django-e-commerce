from django.contrib import admin
from .models import  Book, OrderedBook, Order, Payment, Promocode

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted', 'billing_info', 'payment', 'promocode']
    list_display_links = ['user', 'billing_info', 'payment', 'promocode']
    list_filter = ['ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted']
    search_fields = ['user__username', 'ref_code']

admin.site.register(Book)
admin.site.register(OrderedBook)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Promocode)
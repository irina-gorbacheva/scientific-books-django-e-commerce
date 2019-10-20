from django.contrib import admin
from .models import  Book, OrderedBook, Order, Payment, Promocode, OrderInfo

# Register your models here.
#TODO:
#def accept_refund(modeladmin, request, queryset):
def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)

make_refund_accepted.short_description = 'Grant a refund for the order'

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted', 'shipping_info', 'payment', 'promocode']
    list_display_links = ['user', 'shipping_info', 'payment', 'promocode']
    list_filter = ['ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted']
    search_fields = ['user__username', 'ref_code']
    actions = [make_refund_accepted]

class OrderInfoAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'first_name',
        'last_name',
        'address',
        'country',
        'city',
        'zip',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'first_name', 'last_name', 'zip', 'address', 'city']

admin.site.register(Book)
admin.site.register(OrderedBook)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Promocode)
admin.site.register(OrderInfo)
"""ScientificBooks URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.urls import path
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from bookstore import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),

    path('category/<subject>/', views.CategoryView.as_view(), name='category'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('error', views.error, name='error'),

    path('book_details/<slug>/', views.BookDetailView.as_view(), name='book_details'),

    path('cart', views.cart, name='cart'),
    path('checkout', views.CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_option>/', views.PaymentView.as_view(), name='payment'),
    path('add_promocode', views.add_promocode, name='add_promocode'),
    path('order_received/<ref_code>/', views.order_received, name='order_received'),
    path('refund/<ref_code>/', views.RefundView.as_view(), name='refund'),
    path('orders', views.orders, name='orders'),

    path('add_to_cart/<slug>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<slug>/', views.remove_from_cart, name='remove_from_cart'),
    path('add_single_item_to_cart/<slug>/', views.add_single_item_to_cart, name='add_single_item_to_cart'),
    path('remove_single_item_from_cart/<slug>/', views.remove_single_item_from_cart,
        name='remove_single_item_from_cart'),

   ## url(r'^book_details/(\d+)/', views.book_details, name='book_details'),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
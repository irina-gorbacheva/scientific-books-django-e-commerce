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
from django.conf.urls import url, include
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from bookstore import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),

    url(r'^category/(?P<subject>[\w\-]+)/$', views.CategoryView.as_view(), name='category'),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),

    url(r'^book_details/(?P<slug>[-\w]+)/$', views.BookDetailView.as_view(), name='book_details'),

    url(r'^cart', views.cart, name='cart'),
    url(r'^checkout', views.CheckoutView.as_view(), name='checkout'),
    url(r'^payment/(?P<payment_option>[\w\-]+)/$', views.PaymentView.as_view(), name='payment'),

    url(r'^add_to_cart/(?P<slug>[-\w]+)/$', views.add_to_cart, name='add_to_cart'),
    url(r'^remove_from_cart/(?P<slug>[-\w]+)/$', views.remove_from_cart, name='remove_from_cart'),
    url(r'^add_single_item_to_cart/(?P<slug>[-\w]+)/$', views.add_single_item_to_cart, name='add_single_item_to_cart'),
    url(r'^remove_single_item_from_cart/(?P<slug>[-\w]+)/$', views.remove_single_item_from_cart,
        name='remove_single_item_from_cart'),

   ## url(r'^book_details/(\d+)/', views.book_details, name='book_details'),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
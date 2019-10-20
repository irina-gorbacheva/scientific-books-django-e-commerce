from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.conf import settings

from django.views.generic import ListView, DetailView, View, TemplateView
from .models import Book, OrderedBook, Order, OrderInfo, Payment, Promocode, Refund, UserProfile
from .forms import CheckoutForm, PromocodeForm, RefundForm

import datetime
import stripe
import random
import string

stripe.api_key = settings.STRIPE_SECRET_KEY

def generate_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits + string.ascii_uppercase, k=20))

class HomeView(View):
    def get(self, *args, **kwargs):

        return render(self.request, 'index.html')

def error(request):
    return render(request, 'error.html')

def no_books_found(request):
    return render(request, 'no_books_found.html')

class CategoryView(View):
    CATEGORY_CHOICES = [("AS", "astronomy"), ("PH", "physics"), ("MA", "mathematics"),
                        ("EN", "engineering"), ("CS", "computer_science"), ("BI", "biology")]

    def get(self, *args, **kwargs):
        subject = self.kwargs['subject']
        shortcut = ''

        for pair in self.CATEGORY_CHOICES:
            if subject in pair:
                shortcut = pair[0]
                break
        # unknown subject
        if shortcut == '':
            return redirect('error')

        books_list = Book.objects.filter(category=shortcut)
        if not books_list:
            return redirect('no_books_found')

        paginator = Paginator(books_list, 8)

        page = self.request.GET.get('page')
        books = paginator.get_page(page)
        context = {
            'books': books_list,
            'category': books_list[0].get_category_display(),
            'range': range(1, books.paginator.num_pages + 1),
        }
        return render(self.request, 'category_books.html', context)

class BookDetailView(DetailView):
    def get(self, *args, **kwargs):
        slug = kwargs['slug']
        print(slug)
        book = get_object_or_404(Book, slug=slug)

        context = {
            'book': book
        }

        return render(self.request, 'book_details.html', context)

# !!!! CART !!!!
@login_required(login_url='/accounts/login/')
def cart(request):
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        context = {
            'order': order
        }
        return render(request, "cart.html", context)
    except Order.DoesNotExist:
        messages.warning(request, "You do not have an active order")
        return redirect("home")

def orders(request):
    orders = Order.objects.filter(user=request.user, ordered=True)
    if not orders:
        messages.warning(request, "You do not have any orders")
        return redirect("home")
    context = {
        'orders': orders
    }
    return render(request, "orders.html", context)

def order_received(request, ref_code):
    try:
        order = Order.objects.filter(user=request.user, ordered=True, ref_code=ref_code)
        order.received = True
        order.save()

        messages.success(request, "You confirmed receiving of the order, thank you!")
        return redirect("orders")
    except Order.DoesNotExist:
        messages.error(request, "Order does not exist")
        return redirect("orders")

@login_required
def add_to_cart(request, slug):
    book = get_object_or_404(Book, slug=slug)

    # book which a user has ordered
    ordered_book, created = OrderedBook.objects.get_or_create(
        book=book,
        user=request.user,
        ordered=False
    )

    # check if specific user has an active order
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        # if not, then create one and add an ordered book
    except Order.DoesNotExist:
        order = Order.objects.create(user=request.user, creation_date=timezone.now())
        order.books.add(ordered_book)
        messages.info(request, "This book was added to your cart")
        return redirect("book_details", slug=slug)

    # if the book a user wants to add is already in the order, then update its quantity
    if ordered_book in order.books.all():
        ordered_book.quantity += 1
        ordered_book.save()
        messages.info(request, "Book's quantity was updated")
    else:
        order.books.add(ordered_book)
        messages.info(request, "This book was added to your cart")

    return redirect("book_details", slug=slug)


# !!!!! EDIT THIS SECTION !!!! ????????????
@login_required
def remove_from_cart(request, slug):
    book = get_object_or_404(Book, slug=slug)

    # find order of the specific user
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        # if it does not exist, user doesn't have one
    except Order.DoesNotExist:
        messages.info(request, "You do not have an active order")
        return redirect("book_details", slug=slug)

    if order.books.filter(book__slug=book.slug).exists():
        ordered_book = OrderedBook.objects.filter(
            book=book,
            user=request.user,
            ordered=False
        )[0]
        # book is in user's cart
        order.books.remove(ordered_book)
        ordered_book.delete()
        messages.info(request, "This book was removed from your cart")

    # order doesn't contain item to remove
    else:
        messages.info(request, "This book was not in your cart")

    return redirect("book_details", slug=slug)


def add_single_item_to_cart(request, slug):
    book = get_object_or_404(Book, slug=slug)
    ordered_book, created = OrderedBook.objects.get_or_create(
        book=book,
        user=request.user,
        ordered=False
    )

    ordered_book.quantity += 1
    ordered_book.save()
    messages.info(request, "Book's quantity was updated")

    return redirect('cart')


def remove_single_item_from_cart(request, slug):
    book = get_object_or_404(Book, slug=slug)
    order = Order.objects.get(user=request.user, ordered=False)
    ordered_book = OrderedBook.objects.filter(
        book=book,
        user=request.user,
        ordered=False
    )[0]
    # there is a single instance of a book
    if (ordered_book.quantity == 1):
        order.books.remove(ordered_book)
        ordered_book.delete()
        messages.info(request, "This book was removed from your cart")
    # more than 1 instance of the book
    else:
        ordered_book.quantity -= 1
        ordered_book.save()
        messages.info(request, "Book's quantity was updated")

    return redirect('cart')

def is_valid_form(values):
    for field in values:
        if field == '' or field == ' ':
            return False
    return True

# !!! CHECKOUT !!!
class CheckoutView(View):
    PAYMENT_CHOICES = (
        ('P', 'paypal'),
        ('S', 'stripe')
    )

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm
            context = {
                'form': form,
                'promocodeform': PromocodeForm(),
                'order': order,
                'DISPLAY_PROMO_FORM': True,
            }

            shipping_info_qs = OrderInfo.objects.filter(user=self.request.user, default=True)

            if shipping_info_qs.exists():
                context.update({'default_shipping_info': shipping_info_qs[0]})

            return render(self.request, 'checkout.html', context)
        except Order.DoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect('cart')


    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        VALID_FORM = form.is_valid()
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            use_default_info = form.cleaned_data.get('use_default_info')
            # user wants to use previously stored shipping info
            if use_default_info:
                shipping_info_qs = OrderInfo.objects.filter(user=self.request.user, default=True)
                if shipping_info_qs.exists():
                    shipping_info = shipping_info_qs[0]
                    payment_option = form.cleaned_data.get('payment_option')
                    if not payment_option:
                        messages.info(self.request, "Please select payment option")
                        return redirect('checkout')
                    VALID_FORM = True
                else:
                    messages.info(self.request, "No default info available")
                    return redirect('checkout')

            if VALID_FORM:
                if not use_default_info:
                # user enters a new shipping address
                    first_name = form.cleaned_data.get('first_name')
                    last_name = form.cleaned_data.get('last_name')
                    address = form.cleaned_data.get('address')
                    country = form.cleaned_data.get('country')
                    city = form.cleaned_data.get('city')
                    zip = form.cleaned_data.get('zip')

                    if is_valid_form([first_name, last_name, address, country, city, zip]):
                        shipping_info = OrderInfo()
                        shipping_info.new_info(self.request.user, first_name, last_name, address, country, city, zip)
                        shipping_info.save()
                    else:
                        messages.info(self.request, "Please enter valid parameters")
                        return redirect('checkout')

                save_info = form.cleaned_data.get('save_info')
                if save_info:
                    shipping_info.default = True
                    shipping_info.save()

                order.shipping_info = shipping_info
                order.save()

                payment_option = form.cleaned_data.get('payment_option')

                for pair in self.PAYMENT_CHOICES:
                    if payment_option in pair:
                        payment_option = pair[1]
                        break

                messages.info(self.request, "The form is valid")
                return redirect('payment', payment_option)

            # if it does not exist, user doesn't have one
        except Order.DoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect('cart')

        messages.warning(self.request, "Failed checkout")
        return redirect('checkout')


class PaymentView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'payment_option': self.kwargs['payment_option'],
                'order': order,
                'DISPLAY_PROMO_FORM': False,
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    context.update({
                        'card': card_list[0]
                    })
        except Order.DoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect('cart')
        except Exception:
            return redirect('error')

        return render(self.request, "payment.html", context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST['stripeToken']

        userprofile = UserProfile.objects.get(user=self.request.user)
        save = self.request.POST['save']
        use_default = self.request.POST['use_default']
        amount = int(order.get_total_price() * 100) # cents
        # = self.request.user

        if save:
            if not userprofile.stripe_customer_id:
                customer = stripe.Customer.create(
                    email = self.request.user.email,
                    source = token
                )
                userprofile.stripe_customer_id = customer['id']
                userprofile.one_click_purchasing = True
                userprofile.save()
            else:
                stripe.Customer.create_source(
                    userprofile.stripe_customer_id,
                    source=token
                )

        try:
            if use_default:
                charge = stripe.Charge.create(
                    amount=amount,
                    currency='usd',
                    customer=userprofile.stripe_customer_id
                )
            else:
                charge = stripe.Charge.create(
                    amount=amount,
                    currency='usd',
                    source=token,
                )

            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total_price()
            payment.save()

            ordered_books = order.books.all()
            ordered_books.update(ordered=True)

            for book in ordered_books:
                book.save()

            order.ordered = True
            order.ordered_date = datetime.datetime.now().date()
            order.payment = payment
            order.ref_code = generate_ref_code()
            order.save()

            messages.success(self.request, "Your order was successful")
            return redirect("home")
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("home")
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Time limit error")
            return redirect("home")
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid parameters")
            return redirect("home")
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Failed authentication")
            return redirect("home")
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Failed network communication")
            return redirect("home")
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "Oops! something went wrong, we were notified. You were not charged. Please try again")
            return redirect("home")
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.error(self.request, "Oops! something went wrong, you were not charged. Please try again")
            return redirect("home")


def add_promocode(request):
    if request.method == 'POST':
        form = PromocodeForm(request.POST or None)
        if form.is_valid():
            try:
                order = Order.objects.get(user=request.user, ordered=False)
                if order.promocode:
                    messages.error(request, "You can use only 1 promo code per order")
                    return redirect('checkout')

                code = form.cleaned_data.get('code')
                promocode = Promocode.objects.get(code=code)
                order.promocode = promocode
                order.save()
                messages.success(request, "Promo code is successfully added to your order")
                return redirect('checkout')
            except Order.DoesNotExist:
                messages.error(request, "You do not have an active order")
                return redirect('checkout')
            except Promocode.DoesNotExist:
                messages.error(request, "Promo code does not exist")
                return redirect('checkout')
        else:
            messages.error(request, "Invalid promo code form")
            return redirect('checkout')

class RefundView(View):
    def get(self, *args, **kwargs):
        try:
            ref_code = self.kwargs['ref_code']
            order = Order.objects.get(user=self.request.user, ref_code=ref_code)
            form = RefundForm
            form.ref_code = ref_code

            context = {
                'order': order,
                'form': form,
            }
            return render(self.request, "refund.html", context)
        except Order.DoesNotExist:
            messages.error(self.request, "Order does not exist")
    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST or None)
        if form.is_valid():
            ref_code = self.kwargs['ref_code']
            reason = form.cleaned_data.get('reason')

            try:
                order = Order.objects.get(user=self.request.user, ref_code=ref_code)
                order.refund_requested = True
                order.save()

                refund = Refund()
                refund.order = order
                refund.reason = reason
                refund.email = self.request.user.email
                refund.save()

                messages.success(self.request, "You requested a refund")
                return redirect('orders')

            except Order.DoesNotExist:
                messages.error(self.request, "This order does not exist")
                return redirect('refund')

        messages.error(self.request, "Invalid form")
        return redirect("refund")
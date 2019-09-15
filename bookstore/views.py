from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.conf import settings

from django.views.generic import ListView, DetailView, View, TemplateView
from .models import Book, OrderedBook, Order, BillingInfo, Payment
from .forms import CheckoutForm

import datetime
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

class HomeView(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'index.html')



def login_register(request):
    return render(request, 'login_register.html')


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
            return render(self.request, 'error.html')

        books_list = Book.objects.filter(category=shortcut)
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
        return redirect("/")


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
        order = Order.objects.create(user=request.user, ordered_date=timezone.now())
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
        messages.info(request, "This book was removed from your cart")
    # more than 1 instance of the book
    else:
        ordered_book.quantity -= 1
        ordered_book.save()
        messages.info(request, "Book's quantity was updated")

    return redirect('cart')


# !!! CHECKOUT !!!
class CheckoutView(View):
    PAYMENT_CHOICES = (
        ('P', 'Paypal'),
        ('S', 'Stripe')
    )

    def get(self, *args, **kwargs):
        form = CheckoutForm
        context = {
            'form': form
        }
        return render(self.request, 'checkout.html')

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                address = form.cleaned_data.get('address')
                country = form.cleaned_data.get('country')
                city = form.cleaned_data.get('city')
                zip = form.cleaned_data.get('zip')
                print(zip)
                # ADD FUNCTIONALITY TO THESE FIELS
                same_shipping_address = form.cleaned_data.get('same_shipping_address')
                save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')

                for pair in self.PAYMENT_CHOICES:
                    if payment_option in pair:
                        payment_option = pair[1]
                        break

                billing_info = BillingInfo()
                billing_info.new_info(self.request.user, first_name, last_name, address, country, city, zip)
                billing_info.save()

                order.billing_info = billing_info
                order.save()

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
        except Order.DoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect('cart')

        context = {
            'payment_option': self.kwargs['payment_option']
        }
        return render(self.request, "payment2.html", context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST['stripeToken']
        amount = int(order.get_total_price() * 100) # cents
        user = self.request.user

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency='usd',
                description='Checkout charge',
                source=token,
            ) 

            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total_price()
            payment.save()

            order.ordered = True
            order.ordered_date = datetime.datetime.now().date()
            order.payment = payment
            order.save()

            messages.success(self.request, "Your order was successful")
            return redirect("/")
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Time limit error")
            return redirect("/")
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid parameters")
            return redirect("/")
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Failed authentication")
            return redirect("/")
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Failed network communication")
            return redirect("/")
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "Oops! something went wrong, we were notified. You were not charged. Please try again")
            return redirect("/")
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.error(self.request, "Oops! something went wrong, you were not charged. Please try again")
            return redirect("/")




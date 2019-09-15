from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Book(models.Model):
    CATEGORY_CHOICES=[("AS", "Astronomy"), ("PH", "Physics"), ("MA", "Mathematics"),
                      ("EN", "Engineering"), ("CS", "Computer Science"), ("BI", "Biology")]

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    price = models.FloatField()
    pages = models.IntegerField()
    rating = models.FloatField()
    publisher = models.CharField(max_length=100)
    language = models.CharField(max_length=20)
    shipping_weight = models.FloatField()
    product_dimensions = models.CharField(max_length=50)
    image = models.ImageField(upload_to='books_images/', blank='false')
    slug = models.SlugField(default="book")

    def __str__(self):
        return self.title

class OrderedBook(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} {self.book.title} by {self.book.author} ordered by {self.user}"

    def get_final_price(self):
        return self.quantity * self.book.price

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    books = models.ManyToManyField(OrderedBook)
    ordered = models.BooleanField(default=False)
    creation_date = models.DateField(auto_now_add=True)
    ordered_date = models.DateField()
    billing_info = models.ForeignKey('BillingInfo', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"Order by {self.user}"

    def get_total_price(self):
        total = 0
        for ordered_book in self.books.all():
            total += ordered_book.get_final_price()
        return total

class BillingInfo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    country = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    zip = models.CharField(max_length=20)

    def new_info(self, user, first_name, last_name, address, country, city, zip):
        self.user = user
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.country = country
        self.city = city
        self.zip = zip


    def __str__(self):
        return self.country + ", " +  self.city + ", " + self.address + ", " + self.zip

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


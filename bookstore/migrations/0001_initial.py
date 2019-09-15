# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-07-12 12:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('author', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('AS', 'Astronomy'), ('PH', 'Physics'), ('MA', 'Mathematics'), ('EN', 'Engineering'), ('CS', 'Computer Science'), ('BI', 'Biology')], max_length=2)),
                ('price', models.FloatField()),
                ('pages', models.IntegerField()),
                ('rating', models.FloatField()),
                ('publisher', models.CharField(max_length=100)),
                ('language', models.CharField(max_length=20)),
                ('shipping_weight', models.FloatField()),
                ('product_dimensions', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordered', models.BooleanField(default=False)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('ordered_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='OrderedBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookstore.Book')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='books',
            field=models.ManyToManyField(to='bookstore.OrderedBook'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

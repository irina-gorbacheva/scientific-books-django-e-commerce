# Generated by Django 2.2.3 on 2019-07-28 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookstore', '0007_auto_20190713_1457'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='image',
            field=models.ImageField(blank='true', upload_to='books_images/'),
        ),
    ]

from django.db import models

# Create your models here. After you create a model, you need to run `python3 manage.py makemigrations`
# and `python3 manage.py migrate` to create the table in the database.

# sample model
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    published_date = models.DateField()
    isbn = models.CharField(max_length=13)
    pages = models.IntegerField()
    cover = models.CharField(max_length=100)

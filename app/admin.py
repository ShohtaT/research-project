# 管理画面 http://127.0.0.1:8000/admin/

from django.contrib import admin
from .models import Book

# Register your models here.
admin.site.register(Book)

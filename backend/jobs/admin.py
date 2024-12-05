from django.contrib import admin

from jobs.models import HNLink, Post

admin.site.register(Post)
admin.site.register(HNLink)

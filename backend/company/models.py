from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=99, unique=True)
    link = models.CharField(max_length=99)

    class Meta:
        def __str__(self):
            return f"{self.name}"


class Company(models.Model):
    name = models.CharField(max_length=99, unique=True)
    link = models.CharField(max_length=99, null=True, blank=True)

    class Meta:
        def __str__(self):
            return f"{self.name}"



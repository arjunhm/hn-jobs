from django.db import models


class HNLink(models.Model):
    month = models.CharField(max_length=99)
    year = models.CharField(max_length=99)

    link = models.CharField(max_length=99)
    count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("year", "month")
        ordering = ["-year", "-month"]

        def __str__(self):
            return f"{self.year}-{self.month}"


class Post(models.Model):
    STATUS_TYPES = [
        ("not_applied", "Not Applied"),
        ("applied", "Applied"),
        ("skipped", "Skipped"),
        ("bookmarked", "Bookmarked"),
        ("manual_review", "Manual Review"),
    ]

    month = models.CharField(max_length=99)
    year = models.CharField(max_length=99)

    company = models.ForeignKey(
        "company.Company", related_name="posts", on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        "company.Author", related_name="posts", on_delete=models.CASCADE
    )

    role = models.TextField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)

    post_link = models.CharField(max_length=99)
    external_links = models.JSONField(default=list, null=True, blank=True)

    status = models.CharField(
        max_length=99, choices=STATUS_TYPES, default="not_applied"
    )
    extra_status = models.CharField(max_length=99, null=True, blank=True)

    class Meta:
        unique_together = ("year", "month", "company", "author")
        ordering = ["-year", "-month", "company__name"]

        def __str__(self):
            return f"{self.company}__{self.month}-{self.year}"

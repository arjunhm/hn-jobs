# Generated by Django 5.1.3 on 2024-12-05 01:23

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0003_alter_post_options"),
    ]

    operations = [
        migrations.RenameField(
            model_name="post",
            old_name="links",
            new_name="external_links",
        ),
        migrations.RenameField(
            model_name="post",
            old_name="link",
            new_name="post_link",
        ),
    ]

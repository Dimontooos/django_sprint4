# Generated by Django 4.2.21 on 2025-05-09 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_post_image_comment"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="text",
            field=models.TextField(
                default="text", verbose_name="Текст комментария"
            ),
        ),
    ]

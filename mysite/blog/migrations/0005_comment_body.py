# Generated by Django 5.1.4 on 2024-12-22 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_rename_emai_comment_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='body',
            field=models.TextField(default='No comment'),
            preserve_default=False,
        ),
    ]
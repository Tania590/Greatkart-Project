# Generated by Django 4.1 on 2022-08-31 00:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_variation_variation_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='variation',
            options={'ordering': ('date_modified',)},
        ),
    ]

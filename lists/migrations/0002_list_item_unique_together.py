# Generated by Django 3.0.2 on 2020-02-10 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='item',
            options={'ordering': ('id',)},
        ),
        migrations.AlterUniqueTogether(
            name='item',
            unique_together={('list', 'text')},
        ),
    ]
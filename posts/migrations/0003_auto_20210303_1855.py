# Generated by Django 2.2.9 on 2021-03-03 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20210216_2143'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date']},
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(max_length=200),
        ),
    ]

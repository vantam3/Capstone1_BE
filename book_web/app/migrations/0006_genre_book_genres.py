# Generated by Django 5.1.1 on 2024-11-18 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_delete_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='book',
            name='genres',
            field=models.ManyToManyField(related_name='books', to='app.genre'),
        ),
    ]

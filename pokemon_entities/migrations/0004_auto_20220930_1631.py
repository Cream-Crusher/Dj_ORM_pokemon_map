# Generated by Django 3.1.14 on 2022-09-30 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokemon_entities', '0003_auto_20220930_1612'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pokemon',
            name='test_1',
        ),
        migrations.AddField(
            model_name='pokemonentity',
            name='test_1',
            field=models.ManyToManyField(to='pokemon_entities.Pokemon'),
        ),
    ]

# Generated by Django 3.1.14 on 2022-09-30 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokemon_entities', '0004_auto_20220930_1631'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pokemonentity',
            name='test_1',
        ),
        migrations.AddField(
            model_name='pokemon',
            name='test_1',
            field=models.ManyToManyField(related_name='_pokemon_test_1_+', to='pokemon_entities.Pokemon'),
        ),
    ]

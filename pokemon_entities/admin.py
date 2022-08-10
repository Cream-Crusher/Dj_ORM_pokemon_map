from django.contrib import admin
from .models import Pokemon, PokemonEntity
import pokemon_entities

admin.site.register(Pokemon)
admin.site.register(PokemonEntity)
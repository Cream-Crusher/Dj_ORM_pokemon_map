import folium
import re

from .models import PokemonEntity, Pokemon
from django.http import HttpResponseNotFound
from django.shortcuts import render
from requests import request
from django.utils.timezone import localtime
from django.shortcuts import get_object_or_404


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)    
    names_and_parameters = PokemonEntity.objects.all()
    pokemons_on_page = []

    for pokemon in names_and_parameters:
        img_url = request.build_absolute_uri('media/{}'.format(pokemon.pokemon.image))
        pokemons_on_page.append({
            'pokemon_id':  pokemon.id,
            'img_url': img_url,
            'title_ru': title_ru
        })

        add_pokemon(
            folium_map, pokemon.lat,
            pokemon.low,
            img_url
        )

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    pokemons = []
    pokemon = Pokemon.objects.all()
    pokemon_entity = pokemon.get(id=pokemon_id).pokemon.filter(disappeared_at__gte=localtime(), appeared_at__lte=localtime()).first()
    previous_pokemon = pokemon_entity.pokemon.progenitor
    next_evolution = pokemon_entity.pokemon.next_evolution.first()

    if previous_pokemon:

        previous_evolution = {
            "title_ru": previous_pokemon,
            "pokemon_id": previous_pokemon.id,
            "img_url": request.build_absolute_uri('../../media/{}'.format(previous_pokemon.image))
        }
    else:
        previous_evolution = {}

    if next_evolution:

        next_evolution = {
            "title_ru": next_evolution,
            "pokemon_id": next_evolution.id,
            "img_url": request.build_absolute_uri('../../media/{}'.format(next_evolution.image))
        }
    else:
        next_evolution = {}

    pokemons.append(
        {
            'pokemon_id': pokemon_entity.id,
            'title_ru': pokemon_entity.pokemon.name,
            'title_en': pokemon_entity.pokemon.name_en,
            'title_jp': pokemon_entity.pokemon.name_jp,
            'description': pokemon_entity.pokemon.description,
            'img_url': request.build_absolute_uri('../../media/{}'.format(pokemon_entity.pokemon.image)),
            'entities': [
                {
                    'level': pokemon_entity.level,
                    'lat': pokemon_entity.lat,
                    'lon': pokemon_entity.low
                },
                ],
            "next_evolution": next_evolution,
            'previous_evolution': previous_evolution
        },
    )

    for pokemon in pokemons:

        try:
            pokemon_obj = get_object_or_404(Pokemon, id=pokemon_id)
            requested_pokemon = pokemon
        except:
            return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in requested_pokemon['entities']:
        add_pokemon(
            folium_map, pokemon_entity['lat'],
            pokemon_entity['lon'],
            pokemon['img_url']
        )

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemon
    })

import folium

from .models import PokemonEntity, Pokemon
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.utils import timezone


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
    pokemons = Pokemon.objects.all()
    localtime = timezone.localtime()
    pokemon_entities = PokemonEntity.objects.filter(disappeared_at__gte=localtime, appeared_at__lte=localtime)
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    pokemons_on_page = []

    for pokemon_entity in pokemon_entities:
        img_url = request.build_absolute_uri('media/{}'.format(pokemon_entity.pokemon.image))

        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.low,
            img_url
        )

    for pokemon in pokemons:
        img_url = request.build_absolute_uri('media/{}'.format(pokemon.image))

        pokemons_on_page.append({
            'pokemon_id':  pokemon.id,
            'img_url': img_url,
            'title_ru': pokemon
            })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def get_pokemon_previous_evolution(pokemon_entity, request):
    previous_pokemon = pokemon_entity.pokemon.progenitor

    if previous_pokemon:

        return {
            "title_ru": previous_pokemon,
            "pokemon_id": previous_pokemon.id,
            "img_url": request.build_absolute_uri('../../media/{}'.format(previous_pokemon.image))
            }
    else:
        return {}


def get_pokemon_next_evolution(pokemon_entity, request):
    next_evolution = pokemon_entity.pokemon.next_evolutions.first()

    if next_evolution:

        return {
            "title_ru": next_evolution,
            "pokemon_id": next_evolution.id,
            "img_url": request.build_absolute_uri('../../media/{}'.format(next_evolution.image))
            }
    else:
        return {}


def get_pokemon_locations(pokemon_entities):
    pokemon_locations = []

    for pokemon_entity in pokemon_entities:

        pokemon_locations.append({
            'level': pokemon_entity.level,
            'lat': pokemon_entity.lat,
            'lon': pokemon_entity.low
            })

    return pokemon_locations


def show_pokemon(request, pokemon_id):
    pokemon = get_object_or_404(Pokemon, id=pokemon_id)
    localtime = timezone.localtime()
    pokemon_entities = pokemon.entities.filter(disappeared_at__gte=localtime, appeared_at__lte=localtime)
    pokemon_locations = get_pokemon_locations(pokemon_entities)
    pokemon_previous_evolution = get_pokemon_previous_evolution(pokemon_entities.first(), request)
    pokemon_next_evolution = get_pokemon_next_evolution(pokemon_entities.first(), request)

    requested_pokemon = {
        'pokemon_id': pokemon.id,
        'title_ru': pokemon.name,
        'title_en': pokemon.name_en,
        'title_jp': pokemon.name_jp,
        'description': pokemon.description,
        'img_url': request.build_absolute_uri('../../media/{}'.format(pokemon.image)),
        'entities': pokemon_locations,
        "next_evolution": pokemon_next_evolution,
        'previous_evolution': pokemon_previous_evolution
        }

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    for pokemon_entity in requested_pokemon['entities']:
        add_pokemon(
            folium_map, pokemon_entity['lat'],
            pokemon_entity['lon'],
            requested_pokemon['img_url']
        )

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': requested_pokemon
    })

import folium

from .models import PokemonEntity, Pokemon
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.utils.timezone import localtime


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
    entity_pokemons = PokemonEntity.objects.filter(disappeared_at__gte=localtime(), appeared_at__lte=localtime())
    obj_pokemons = Pokemon.objects.all()
    pokemons_on_page = []

    for pokemon_entity in entity_pokemons:
        img_url = request.build_absolute_uri('media/{}'.format(pokemon_entity.pokemon.image))

        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.low,
            img_url
        )

    for pokemon_obj in obj_pokemons:
        img_url = request.build_absolute_uri('media/{}'.format(pokemon_obj.image))

        pokemons_on_page.append({
            'pokemon_id':  pokemon_obj.id,
            'img_url': img_url,
            'title_ru': pokemon_obj
            })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def get_previous_evolution_pokemon(pokemon_entity, request):
    previous_pokemon = pokemon_entity.pokemon.progenitor

    if previous_pokemon:

        return {
            "title_ru": previous_pokemon,
            "pokemon_id": previous_pokemon.id,
            "img_url": request.build_absolute_uri('../../media/{}'.format(previous_pokemon.image))
            }
    else:
        return {}


def get_next_evolution_pokemon(pokemon_entity, request):
    next_evolution = pokemon_entity.pokemon.next_evolutions.first()

    if next_evolution:

        return {
            "title_ru": next_evolution,
            "pokemon_id": next_evolution.id,
            "img_url": request.build_absolute_uri('../../media/{}'.format(next_evolution.image))
            }
    else:
        return {}


def get_location_pokemons(entitys_pokemon):
    location_pokemons = []

    for pokemon_entity in entitys_pokemon:

        location_pokemons.append({
            'level': pokemon_entity.level,
            'lat': pokemon_entity.lat,
            'lon': pokemon_entity.low
            })

    return location_pokemons


def show_pokemon(request, pokemon_id):
    pokemons_obj = Pokemon.objects.get(id=pokemon_id)
    entitys_pokemon = PokemonEntity.objects.filter(pokemon=pokemon_id, disappeared_at__gte=localtime(), appeared_at__lte=localtime())
    location_pokemons = get_location_pokemons(entitys_pokemon)
    previous_evolution_pokemon = get_previous_evolution_pokemon(entitys_pokemon.first(), request)
    next_evolution_pokemon = get_next_evolution_pokemon(entitys_pokemon.first(), request)

    requested_pokemon = {
        'pokemon_id': pokemons_obj.id,
        'title_ru': pokemons_obj.name,
        'title_en': pokemons_obj.name_en,
        'title_jp': pokemons_obj.name_jp,
        'description': pokemons_obj.description,
        'img_url': request.build_absolute_uri('../../media/{}'.format(pokemons_obj.image)),
        'entities': location_pokemons,
        "next_evolution": next_evolution_pokemon,
        'previous_evolution': previous_evolution_pokemon
        }

    if requested_pokemon['pokemon_id'] == int(pokemon_id):

        folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

        for pokemon_entity in requested_pokemon['entities']:
            add_pokemon(
                folium_map, pokemon_entity['lat'],
                pokemon_entity['lon'],
                requested_pokemon['img_url']
            )
    else:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': requested_pokemon
    })

import os

from flask import Flask, render_template, request

import requests_cache
import pokepy

requests_cache.install_cache('pokedex_cache', backend='sqlite', expire_after=86400)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/pokedex')
    def pokedex():
        client = pokepy.V2Client()
        # Get region from query parameter, default to 'all'
        request_region = request.args.get('region', default='all', type=str).lower()
        if request_region != 'all':
            # Try to get region data
            try:
                region_data = client.get_region(request_region)[0]
            except Exception:
                return "Region not found", 404
            else:
                pokemon_list = []
                for pokedex in region_data.pokedexes:
                    # Get pokedex for the region
                    pokedex_data = client.get_pokedex(pokedex.name)[0]
                    # Iterate through pokemon entries
                    for entry in pokedex_data.pokemon_entries:
                        # Get pokemon species and then the default variety of that species
                        pokemon_species = client.get_pokemon_species(entry.pokemon_species.name)[0]
                        pokemon = client.get_pokemon(pokemon_species.varieties[0].pokemon.name)[0]
                        # Check if the generation matches the region's main generation
                        if pokemon_species.generation.url == region_data.main_generation.url:
                            pokemon_list.append(pokemon)
                # Remove duplicates
                pokemon_list = list({p.id: p for p in pokemon_list}.values())
                # Sort by Pokemon ID
                pokemon_list.sort(key=lambda x: x.id)
                return render_template('pokedex.html', pokemon_list=pokemon_list)
        else:
            pokemon_list = []
            for i in range(1, 1026):
                pokemon = client.get_pokemon(i)[0]
                pokemon_list.append(pokemon)
            return render_template('pokedex.html', pokemon_list=pokemon_list)
            

    return app

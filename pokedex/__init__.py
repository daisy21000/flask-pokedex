import os

from flask import Flask, render_template
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
        client_cache = pokepy.V2Client()
        pokemon_list_string = "<ul>"
        for i in range(1, 1025):
            pokemon = client_cache.get_pokemon(i)[0]
            pokemon_list_string += f"<li>{pokemon.species.name.title()}</li>"
        pokemon_list_string += "</ul>"
        return pokemon_list_string
    return app

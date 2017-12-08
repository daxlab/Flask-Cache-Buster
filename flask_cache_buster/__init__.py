import os
import hashlib
from pathlib import Path


HASH_SIZE = 10


def __is_file_to_be_busted(filepath, extensions):
    """

    :param filepath:
    :return: True or False
    """
    if not extensions:
        return True
    return Path(filepath).suffix in extensions if filepath else False


def register_cache_buster(app, extensions=None):
    """
    Register `app` in cache buster so that `url_for` adds a unique prefix
    to URLs generated for the `'static'` endpoint. Also make the app able
    to serve cache-busted static files.

    This allows setting long cache expiration values on static resources
    because whenever the resource changes, so does its URL.
    """

    bust_map = {}  # map from an unbusted filename to a busted one
    unbust_map = {}  # map from a busted filename to an unbusted one
    # http://flask.pocoo.org/docs/0.12/api/#flask.Flask.static_folder

    app.logger.debug('Starting computing hashes for static assets')
    # compute (un)bust tables.
    for dirpath, dirnames, filenames in os.walk(app.static_folder):
        for filename in filenames:
            # compute version component
            rooted_filename = os.path.join(dirpath, filename)
            if not __is_file_to_be_busted(rooted_filename, extensions):
                continue
            with open(rooted_filename, 'r') as f:
                version = hashlib.md5(f.read()).hexdigest()[:HASH_SIZE]

            # add version
            unbusted = os.path.relpath(rooted_filename, app.static_folder)
            busted = os.path.join(version, unbusted)

            # save computation to map
            bust_map[unbusted] = busted
            unbust_map[busted] = unbusted
    app.logger.debug('Finished Starting computing hashes for static assets')

    def bust_filename(file):
        return bust_map.get(file, file)

    def unbust_filename(file):
        return unbust_map.get(file, file)

    @app.url_defaults
    def reverse_to_cache_busted_url(endpoint, values):
        """
        Make `url_for` produce busted filenames when using the 'static'
        endpoint.
        """
        if endpoint == 'static':
            values['filename'] = bust_filename(values['filename'])

    def debusting_static_view(file):
        """
        Serve a request for a static file having a busted name.
        """
        return original_static_view(filename=unbust_filename(file))

    # Replace the default static file view with our debusting view.
    original_static_view = app.view_functions['static']
    app.view_functions['static'] = debusting_static_view

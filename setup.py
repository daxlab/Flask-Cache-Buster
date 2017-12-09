from setuptools import setup
setup(
    name='Flask-Cache-Buster',
    version='1.0.1',
    description='Flask extension calculates new cache busted path for static files',
    packages=['flask_cache_buster'],
    license='MIT',
    url='https://github.com/daxlab/Flask-Cache-Buster',
    install_requires=[
        'Flask',
    ],
)

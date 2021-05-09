from setuptools import setup, find_packages

DEPENDENCIES = [
    'pandas',
    'dash',
    'dash-bootstrap-components',
    'dash-daq',
    'dash-auth',
    'cryptography',
    'gunicorn',
    'flask',
    'flask_restful'
]

with open("README.md", "r") as f:
    readme = f.read()


setup(
    name='enema',
    version='1.0.0',
    description='Resource Congestion Resolution Service',
    long_description=readme,
    author='Krzysztof Czarnecki',
    author_email='kjczarne@gmail.com',
    install_requires=DEPENDENCIES
)

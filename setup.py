# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "swagger_server"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "connexion",
    "swagger-ui-bundle>=0.0.2"
]

setup(
    name=NAME,
    version=VERSION,
    description="Tienda y Pasarela de Pago (TPP)",
    author_email="",
    url="",
    keywords=["Swagger", "Tienda y Pasarela de Pago (TPP)"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['swagger_server=swagger_server.__main__:main']},
    long_description="""\
    El microservicio de Tienda y Pasarela de Pago (TPP) gestiona el catálogo de productos musicales y merchandising, el carrito de compras de los usuarios y los métodos de pago asociados a cada cuenta.  Permite consultar el catálogo de productos, añadir y eliminar productos del carrito, consultar el contenido del carrito y gestionar los métodos de pago. Los productos pueden ser canciones, álbumes o artículos de merchandising, y se integran con otros microservicios para obtener información adicional de usuarios y autores.  Funcionalidades principales: - Consulta de productos disponibles en la tienda, con detalles como nombre, precio, artista, colaboradores, fecha de lanzamiento, género, portada, etc. - Gestión del carrito de compras: añadir productos, eliminar productos y consultar el contenido del carrito por usuario. - Administración de métodos de pago: alta y baja de tarjetas, PayPal, etc. - Seguridad mediante autenticación por API Key y permisos granulares para cada operación.  El microservicio se conecta con el microservicio de Usuarios para obtener información de métodos de pago y productos comprados, y con el microservicio de Temas y Autores para relacionar productos musicales con los datos de la tienda. El precio de cada producto se gestiona en la base de datos propia del microservicio.
    """
)

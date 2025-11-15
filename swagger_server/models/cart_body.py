# coding: utf-8
from __future__ import absolute_import
from swagger_server.models.base_model_ import Model
from swagger_server import util

class CartBody(Model):
    """Modelo para el cuerpo del carrito (canciones, álbumes o merch)."""

    def __init__(self, song_id: int = None, album_id: int = None, merch_id: int = None, unidades: int = 1):  # noqa: E501
        """CartBody - a model defined in Swagger

        :param song_id: ID of the song to add.
        :param album_id: ID of the album to add.
        :param merch_id: ID of the merch to add.
        :param unidades: Quantity (only applies to merch).
        """
        self.swagger_types = {
            'song_id': int,
            'album_id': int,
            'merch_id': int,
            'unidades': int
        }

        self.attribute_map = {
            'song_id': 'songId',
            'album_id': 'albumId',
            'merch_id': 'merchId',
            'unidades': 'unidades'
        }

        self._song_id = song_id
        self._album_id = album_id
        self._merch_id = merch_id
        self._unidades = unidades or 1

    @classmethod
    def from_dict(cls, dikt) -> 'CartBody':
        """Returns the dict as a model."""
        return util.deserialize_model(dikt, cls)

    @property
    def song_id(self) -> int:
        return self._song_id

    @song_id.setter
    def song_id(self, song_id: int):
        self._song_id = song_id

    @property
    def album_id(self) -> int:
        return self._album_id

    @album_id.setter
    def album_id(self, album_id: int):
        self._album_id = album_id

    @property
    def merch_id(self) -> int:
        return self._merch_id

    @merch_id.setter
    def merch_id(self, merch_id: int):
        self._merch_id = merch_id

    @property
    def unidades(self) -> int:
        return self._unidades

    @unidades.setter
    def unidades(self, unidades: int):
        if unidades is not None and unidades < 1:
            raise ValueError("La cantidad debe ser al menos 1")
        self._unidades = unidades or 1

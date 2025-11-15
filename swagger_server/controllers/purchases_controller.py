import connexion
import six
import requests
from datetime import datetime

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.purchase import Purchase  # noqa: E501
from swagger_server import util
from swagger_server.dbconx import dbConectar, dbDesconectar

from swagger_server.controllers.config import USER_SERVICE_URL
from swagger_server.controllers.authorization_controller import verify_token_and_get_user_id

def set_purchase(body=None):
    """Set a product as purchased by the user."""
    db_conexion = None
    try:
        # Verifica que el cuerpo sea JSON
        if not connexion.request.is_json:
            return Error(code="400", message="El cuerpo de la petición no es JSON"), 400
        body = Purchase.from_dict(connexion.request.get_json())

        # --- VERIFICAR TOKEN ---
        token = connexion.request.cookies.get("token")
        user_id, error_response = verify_token_and_get_user_id(token)
        if error_response:
            return error_response
        # --- VERIFICAR TOKEN ---

        # Conexión con la base de datos
        db_conexion = dbConectar()
        cursor = db_conexion.cursor()
        # Inserta la compra
        cursor.execute(
            """
            INSERT INTO Compras (idUsuario, importe, fecha, metodoPago)
            VALUES (%s, %s, %s, %s)
            RETURNING idCompra
            """,
            (user_id, body.purchase_price, body.purchase_date, body.payment_method_id)
        )
        result = cursor.fetchone()
        if not result:
            db_conexion.rollback()
            return Error(code="500", message="No se pudo registrar la compra"), 500
        id_compra = result[0]

        # Registrar los productos de la compra en las tablas intermedias
        if body.song_ids:
            for song_id in body.song_ids:
                try:
                    cursor.execute(
                        "INSERT INTO CancionesCompra (idCompra, idCancion) VALUES (%s, %s)",
                        (id_compra, song_id)
                    )
                except Exception as e:
                    print(f"Error al registrar canción {song_id}: {e}")
        
        if body.album_ids:
            for album_id in body.album_ids:
                try:
                    cursor.execute(
                        "INSERT INTO AlbumesCompra (idCompra, idAlbum) VALUES (%s, %s)",
                        (id_compra, album_id)
                    )
                except Exception as e:
                    print(f"Error al registrar álbum {album_id}: {e}")
        
        if body.merch_ids:
            for merch_id in body.merch_ids:
                try:
                    cursor.execute(
                        "INSERT INTO MerchCompra (idCompra, idMerch) VALUES (%s, %s)",
                        (id_compra, merch_id)
                    )
                except Exception as e:
                    print(f"Error al registrar merch {merch_id}: {e}")

        db_conexion.commit()
        cursor.close()

        return {"message": f"Compra registrada con id {id_compra}", "userId": user_id}, 200

    except Exception as e:
        if db_conexion:
            db_conexion.rollback()
        print("Error al registrar la compra:", e)
        return Error(code="500", message=str(e)), 500

    finally:
        if db_conexion:
            dbDesconectar(db_conexion)

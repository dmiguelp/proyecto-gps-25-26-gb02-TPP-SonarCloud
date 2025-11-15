import connexion
import six
import requests

from swagger_server.models.cart_body import CartBody  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.product import Product  # noqa: E501
from swagger_server import util
from swagger_server.dbconx import dbConectar, dbDesconectar
from swagger_server.controllers.config import USER_SERVICE_URL, TYA_SERVICE_URL
from swagger_server.controllers.authorization_controller import verify_token_and_get_user_id



def add_to_cart(body=None):
    """Add a product (song, album or merch) to the authenticated user's cart."""
    db_conexion = None
    try:
        if not connexion.request.is_json:
            return Error(code="400", message="El cuerpo de la petición no es JSON"), 400
        body = CartBody.from_dict(connexion.request.get_json())

        # --- VERIFICAR TOKEN ---
        token = connexion.request.cookies.get("token")
        user_id, error_response = verify_token_and_get_user_id(token)
        if error_response:
            return error_response
        # --- VERIFICAR TOKEN ---

        db_conexion = dbConectar()
        cursor = db_conexion.cursor()

        if body.song_id:
            cursor.execute("SELECT 1 FROM CancionesCarrito WHERE idCancion = %s AND idUsuario = %s",
                           (body.song_id, user_id))
            if cursor.fetchone():
                return Error(code="400", message="La canción ya está en el carrito"), 400
            cursor.execute("INSERT INTO CancionesCarrito (idCancion, idUsuario) VALUES (%s, %s)",
                           (body.song_id, user_id))

        elif body.album_id:
            cursor.execute("SELECT 1 FROM AlbumesCarrito WHERE idAlbum = %s AND idUsuario = %s",
                           (body.album_id, user_id))
            if cursor.fetchone():
                return Error(code="400", message="El álbum ya está en el carrito"), 400
            cursor.execute("INSERT INTO AlbumesCarrito (idAlbum, idUsuario) VALUES (%s, %s)",
                           (body.album_id, user_id))

        elif body.merch_id:
            cursor.execute("SELECT 1 FROM MerchCarrito WHERE idMerch = %s AND idUsuario = %s",
                           (body.merch_id, user_id))
            if cursor.fetchone():
                return Error(code="400", message="El artículo ya está en el carrito"), 400
            cursor.execute("INSERT INTO MerchCarrito (idMerch, idUsuario, unidades) VALUES (%s, %s, %s)",
                           (body.merch_id, user_id, body.unidades))

        else:
            return Error(code="400", message="Debes proporcionar songId, albumId o merchId"), 400
        
        db_conexion.commit()
        cursor.close()
        return {"message": "Producto añadido al carrito correctamente"}, 200

    except Exception as e:
        if db_conexion:
            db_conexion.rollback()
        print("Error al añadir al carrito:", e)
        return Error(code="500", message=str(e)), 500

    finally:
        if db_conexion:
            dbDesconectar(db_conexion)



def get_cart_products():
    """Get all products from the authenticated user's cart."""
    db_conexion = None
    try:
        # --- VERIFICAR TOKEN ---
        token = connexion.request.cookies.get("token")
        user_id, error_response = verify_token_and_get_user_id(token)
        if error_response:
            return error_response
        # --- VERIFICAR TOKEN ---

        db_conexion = dbConectar()
        cursor = db_conexion.cursor()

        canciones = []
        albumes = []
        merchs = []
        productos = []
        
        # Canciones
        cursor.execute("""
            SELECT c.idCancion
            FROM CancionesCarrito c
            WHERE c.idUsuario = %s
        """, (user_id,))
        for row in cursor.fetchall():
            canciones.append(row[0])
            
        # Álbumes
        cursor.execute("""
            SELECT a.idAlbum
            FROM AlbumesCarrito a
            WHERE a.idUsuario = %s
        """, (user_id,))
        for row in cursor.fetchall():
            albumes.append(row[0])

        # Merch
        cursor.execute("""
            SELECT m.idMerch, m.unidades
            FROM MerchCarrito m
            WHERE m.idUsuario = %s
        """, (user_id,))
        for row in cursor.fetchall():
            merchs.append((row[0], row[1]))

        # Resolvemos IDs de canciones, albumes y merch usando el microservicio TyA.
        for cancion_id in canciones:
            try:
                response = requests.get(f"{TYA_SERVICE_URL}/song/{cancion_id}", timeout=3)
                if response.status_code == 200:
                    producto_data = response.json()
                    producto_schema = Product()
                    producto_schema.song_id = producto_data.get("songId")
                    producto_schema.name = producto_data.get("title")
                    producto_schema.description = producto_data.get("description")
                    producto_schema.price = producto_data.get("price")
                    producto_schema.artist = str(producto_data.get("artistId", 0))
                    producto_schema.colaborators = [str(i) for i in producto_data.get("collaborators", [])]
                    producto_schema.genre = str(producto_data.get("genres", ["0"])[0]) if producto_data.get("genres") else "0"
                    producto_schema.duration = producto_data.get("duration", 0)
                    producto_schema.cover = producto_data.get("cover")
                    producto_schema.release_date = producto_data.get("releaseDate")
                    producto_schema.album_id = producto_data.get("albumId")
                    productos.append(producto_schema)
            except Exception as e:
                print(f"Error al obtener canción {cancion_id}: {e}")

        for album_id in albumes:
            try:
                response = requests.get(f"{TYA_SERVICE_URL}/album/{album_id}", timeout=3)
                if response.status_code == 200:
                    producto_data = response.json()
                    producto_schema = Product()
                    producto_schema.album_id = producto_data.get("albumId")
                    producto_schema.name = producto_data.get("title")
                    producto_schema.description = producto_data.get("description")
                    producto_schema.price = producto_data.get("price")
                    producto_schema.artist = str(producto_data.get("artistId", 0))
                    producto_schema.colaborators = [str(i) for i in producto_data.get("collaborators", [])]
                    producto_schema.genre = str(producto_data.get("genres", ["0"])[0]) if producto_data.get("genres") else "0"
                    producto_schema.song_list = [str(i) for i in producto_data.get("songs", [])]
                    producto_schema.cover = producto_data.get("cover")
                    producto_schema.release_date = producto_data.get("releaseDate")
                    productos.append(producto_schema)
            except Exception as e:
                print(f"Error al obtener álbum {album_id}: {e}")

        for merch_tuple in merchs:
            merch_id = merch_tuple[0]  # El primer elemento es el ID
            try:
                response = requests.get(f"{TYA_SERVICE_URL}/merch/{merch_id}", timeout=3)
                if response.status_code == 200:
                    producto_data = response.json()
                    producto_schema = Product()
                    producto_schema.merch_id = producto_data.get("merchId")
                    producto_schema.name = producto_data.get("title")
                    producto_schema.description = producto_data.get("description")
                    producto_schema.price = producto_data.get("price")
                    producto_schema.artist = str(producto_data.get("artistId", 0))
                    producto_schema.colaborators = [str(i) for i in producto_data.get("collaborators", [])]
                    producto_schema.genre = "Merch"
                    producto_schema.cover = producto_data.get("cover")
                    producto_schema.release_date = producto_data.get("releaseDate")
                    productos.append(producto_schema)
            except Exception as e:
                print(f"Error al obtener merch {merch_id}: {e}")

        cursor.close()
        return [p.to_dict() for p in productos], 200

    except Exception as e:
        print("Error al obtener productos del carrito:", e)
        return Error(code="500", message=str(e)), 500
    finally:
        if db_conexion:
            dbDesconectar(db_conexion)


def remove_from_cart(product_id, type):
    """Remove a product from the authenticated user's cart."""
    db_conexion = None
    try:
        # --- VERIFICAR TOKEN ---
        token = connexion.request.cookies.get("token")
        user_id, error_response = verify_token_and_get_user_id(token)
        if error_response:
            return error_response
        # --- VERIFICAR TOKEN ---

        # Eliminar producto del carrito del usuario autenticado
        db_conexion = dbConectar()
        cursor = db_conexion.cursor()

        # type: "song" -> song
        # type: "album" -> album
        # type: "merch" -> merch

        if type == "song" or type == "0":
            cursor.execute("DELETE FROM CancionesCarrito WHERE idCancion = %s AND idUsuario = %s",
                           (product_id, user_id))
        elif type == "album" or type == "1":
            cursor.execute("DELETE FROM AlbumesCarrito WHERE idAlbum = %s AND idUsuario = %s",
                           (product_id, user_id))
        elif type == "merch" or type == "2":
            cursor.execute("DELETE FROM MerchCarrito WHERE idMerch = %s AND idUsuario = %s",
                           (product_id, user_id))
        else:
            return Error(code="400", message="Tipo de producto inválido"), 400
    
        db_conexion.commit()
        cursor.close()

        return {"message": "Producto eliminado del carrito correctamente"}, 200

    except Exception as e:
        if db_conexion:
            db_conexion.rollback()
        print("Error al eliminar del carrito:", e)
        return Error(code="500", message=str(e)), 500

    finally:
        if db_conexion:
            dbDesconectar(db_conexion)

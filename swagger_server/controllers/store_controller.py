import connexion
import httpx
from swagger_server.models.error import Error
from swagger_server.models.product import Product
from swagger_server.dbconx import dbConectar, dbDesconectar
from swagger_server.controllers.config import USER_SERVICE_URL, TYA_SERVICE_URL

def show_storefront_products():
    """Obtiene canciones, álbumes y merch del microservicio Temas y Autores y los devuelve formateados para el frontend."""
    conexion = None
    try:
        productos = []

        # --- Obtener datos del microservicio Temas y Autores ---
        try:
            with httpx.Client(timeout=5.0) as client:
                canciones = client.get(f"{TYA_SERVICE_URL}/canciones").json()
                albumes = client.get(f"{TYA_SERVICE_URL}/albumes").json()
                merch = client.get(f"{TYA_SERVICE_URL}/merch").json()
        except Exception as e:
            print(f"Error al conectar con Temas y Autores: {e}")
            canciones, albumes, merch = [], [], []

        # --- Mapear / Enmascarar canciones ---
        for c in canciones:
            productos.append(Product(
                song_id=c.get("songId"),
                name=c.get("title"),
                artist=str(c.get("artistId")),
                release_date=f"{c.get('releaseDate')}T00:00:00Z",
                album_id=c.get("albumId"),
                description=c.get("description"),
                song_list=[],
                merch_id=0,
                duration=c.get("duration"),
                cover=c.get("cover"),
                price=c.get("price"),
                genre=str(c.get("genres", ["0"])[0]) if c.get("genres") else "0",
                colaborators=[str(i) for i in c.get("collaborators", [])]
            ))

        # --- Mapear álbumes ---
        for a in albumes:
            productos.append(Product(
                song_id=0,
                name=a.get("title"),
                artist=str(a.get("artistId")),
                release_date=f"{a.get('releaseDate')}T00:00:00Z",
                album_id=a.get("albumId"),
                description=a.get("description"),
                song_list=[str(i) for i in a.get("songs", [])],
                merch_id=0,
                duration=0,
                cover=a.get("cover"),
                price=a.get("price"),
                genre=str(a.get("genres", ["0"])[0]) if a.get("genres") else "0",
                colaborators=[str(i) for i in a.get("collaborators", [])]
            ))

        # --- Mapear merch ---
        for m in merch:
            productos.append(Product(
                song_id=0,
                name=m.get("title"),
                artist=str(m.get("artistId")),
                release_date=f"{m.get('releaseDate')}T00:00:00Z",
                album_id=0,
                description=m.get("description"),
                song_list=[],
                merch_id=m.get("merchId"),
                duration=0,
                cover=m.get("cover"),
                price=m.get("price"),
                genre="Merch",
                colaborators=[str(i) for i in m.get("collaborators", [])]
            ))

        # --- Retornar la lista formateada ---
        return [p.to_dict() for p in productos]

    except Exception as e:
        print(f"Error general al obtener los productos: {e}")
        return Error(code="500", message=str(e))
    finally:
        if conexion:
            dbDesconectar(conexion)

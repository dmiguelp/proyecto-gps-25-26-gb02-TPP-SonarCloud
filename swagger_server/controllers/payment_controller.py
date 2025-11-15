import connexion
import six
import requests

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.payment_method import PaymentMethod  # noqa: E501
from swagger_server import util
from swagger_server.dbconx import dbConectar, dbDesconectar

# URL del microservicio de usuarios
from swagger_server.controllers.config import USER_SERVICE_URL
from swagger_server.controllers.authorization_controller import verify_token_and_get_user_id


def add_payment_method(body=None):
    """Add a new payment method."""
    db_conexion = None
    try:
        if not connexion.request.is_json:
            return Error(code="400", message="El cuerpo de la petición no es JSON"), 400
        body = PaymentMethod.from_dict(connexion.request.get_json())

        # --- VERIFICAR TOKEN ---
        token = connexion.request.cookies.get("token")
        user_id, error_response = verify_token_and_get_user_id(token)
        if error_response:
            return error_response
        # --- VERIFICAR TOKEN ---


        # Conexión a la base de datos
        db_conexion = dbConectar()
        cursor = db_conexion.cursor()

        id_metodo = None
        # Crear el método de pago
        cursor.execute(
            """
            INSERT INTO MetodosPago (numeroTarjeta, mesValidez, anioVlidez, nombreTarjeta)
            VALUES (%s, %s, %s, %s)
            RETURNING idMetodoPago
            """,
            (body.card_number, body.expire_month, body.expire_year, body.card_holder)
        )
        result = cursor.fetchone()
        if not result:
            db_conexion.rollback()
            return Error(code="500", message="No se pudo crear el método de pago"), 500
        id_metodo = result[0]

        # Asociar usuario con método de pago
        cursor.execute(
            """
            INSERT INTO UsuariosMetodosPago (idUsuario, idMetodoPago)
            VALUES (%s, %s)
            """,
            (user_id, id_metodo)
        )
        
        db_conexion.commit()
        cursor.close()

        return {"message": f"Método de pago agregado con id {id_metodo}", "userId": user_id}, 200

    except Exception as e:
        if db_conexion:
            db_conexion.rollback()
        print("Error al añadir método de pago:", e)
        return Error(code="500", message=str(e)), 500

    finally:
        if db_conexion:
            dbDesconectar(db_conexion)


def delete_payment_method(payment_method_id):
    """Delete a payment method by ID."""
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

        cursor.execute("DELETE FROM MetodosPago WHERE idMetodoPago = %s", (payment_method_id,))
        if cursor.rowcount == 0:
            return Error(code="404", message="Método de pago no encontrado"), 404
        
        cursor.execute("DELETE FROM UsuariosMetodosPago WHERE idMetodoPago = %s", (payment_method_id,))
        
        db_conexion.commit()
        cursor.close()
        return {"message": "Método de pago eliminado correctamente"}, 200

    except Exception as e:
        if db_conexion:
            db_conexion.rollback()
        print("Error al eliminar método de pago:", e)
        return Error(code="500", message=str(e)), 500

    finally:
        if db_conexion:
            dbDesconectar(db_conexion)


def show_user_payment_methods():
    """Returns a list of payment methods for the selected user."""
    db_conexion = None
    try:

        # --- VERIFICAR TOKEN ---
        token = connexion.request.cookies.get("token")
        user_id, error_response = verify_token_and_get_user_id(token)
        if error_response:
            return error_response
        # --- VERIFICAR TOKEN ---

        # Consultar la base de datos con el user_id
        db_conexion = dbConectar()
        cursor = db_conexion.cursor()

        ids_metodos_pago = []
        metodos = []
        cursor.execute("""
            SELECT idMetodoPago FROM UsuariosMetodosPago WHERE idUsuario = %s
        """, (user_id,))
        rows_ids = cursor.fetchall()
        ids_metodos_pago = [row[0] for row in rows_ids]
        if not ids_metodos_pago:
            return [], 200  # Retornar lista vacía si no hay métodos de pago

        for metodo_id in ids_metodos_pago:
            cursor.execute("""
                SELECT idMetodoPago, numeroTarjeta, mesValidez, anioVlidez, nombreTarjeta FROM MetodosPago WHERE idMetodoPago = %s
            """, (metodo_id,))
            tupla = cursor.fetchone()
            if tupla:
                metodo = PaymentMethod(
                    card_number=tupla[1],
                    expire_month=tupla[2],
                    expire_year=tupla[3],
                    card_holder=tupla[4]
                )
                # Agregar id como atributo adicional
                metodo.id = tupla[0]
                metodos.append(metodo)
        cursor.close()
        return [m.to_dict() for m in metodos], 200

    except Exception as e:
        print("Error al obtener métodos de pago:", e)
        return Error(code="500", message=str(e)), 500

    finally:
        if db_conexion:
            dbDesconectar(db_conexion)

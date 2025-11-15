# Correcciones Realizadas al Proyecto

## Resumen
Se han identificado y corregido múltiples errores en los controladores del proyecto para que sean conformes con la definición de API en `swagger.yaml`.

## Cambios Realizados

### 1. **cart_controller.py**

#### Problema: Conflicto de nombres de variables
- **Causa**: La variable local `conexion` inicializada a `None` conflictua con el módulo `connexion` usado para acceder a `connexion.request`
- **Solución**: Renombrar la variable local a `db_conexion` en todas las funciones

#### Problema: Error de sintaxis en `merchs.append()`
- **Línea original**: `merchs.append(row[0], row[1])`
- **Corrección**: `merchs.append((row[0], row[1]))`
- **Razón**: `append()` solo acepta un argumento; se debe pasar una tupla

#### Problema: Objeto Product incompleto
- **Línea original**: `productos.append(pro)` (variable no definida)
- **Corrección**: Se añadieron las líneas faltantes para completar la construcción del objeto Product con sus campos artist, colaborators y genre

#### Problema: Nombre incorrecto de parámetro
- **Línea original**: `def remove_from_cart(product_id, product_type):`
- **Corrección**: `def remove_from_cart(product_id, type):`
- **Razón**: El swagger.yaml define el parámetro query como `type`

#### Problema: Manejo incorrecto del parámetro `type`
- **Original**: Comparaciones con números (0, 1, 2)
- **Corrección**: Manejo de strings ("song", "album", "merch") y números como fallback

#### Problema: Parámetros de tupla incompletos en SQL
- **Original**: `(user_id)` - esto es solo una variable, no una tupla
- **Corrección**: `(user_id,)` - tupla con un elemento
- **Ubicaciones**: En `get_cart_products()` para las tres consultas SELECT

### 2. **payment_controller.py**

#### Problema: Igual conflicto de nombres de variables
- **Solución**: Renombrar `conexion` a `db_conexion` en las funciones:
  - `add_payment_method()`
  - `delete_payment_method()`
  - `show_user_payment_methods()`

#### Problema: Uso incorrecto de `executemany()`
- **Línea original**: `cursor.executemany(..., (ids_metodos_pago))`
- **Corrección**: Cambiar a un bucle con `cursor.execute()` individual para cada ID

#### Problema: Retorno de tuplas en lugar de objetos PaymentMethod
- **Original**: Retornaba tuplas con user_id adicional
- **Corrección**: Retornar objetos `PaymentMethod` instanciados correctamente

#### Problema: Retorno sin serialización
- **Original**: `return metodos, 200` (lista de objetos)
- **Corrección**: `return [m.to_dict() for m in metodos], 200` (lista de diccionarios JSON)

### 3. **purchases_controller.py**

#### Problema: Igual conflicto de nombres de variables
- **Solución**: Renombrar `conexion` a `db_conexion`

#### Problema: Referencia a atributo no existente
- **Línea original**: `return {"message": f"...", "userId": body.user_id}, 200`
- **Corrección**: `return {"message": f"...", "userId": user_id}, 200`
- **Razón**: El modelo `Purchase` no tiene atributo `user_id`; el usuario se obtiene del token

## Conformidad con swagger.yaml

Todos los cambios garantizan que los controladores ahora son conformes con la especificación de API:

✅ **POST /cart** - `add_to_cart()`: Correcciones de sintaxis y nombres de variables  
✅ **GET /cart** - `get_cart_products()`: Parámetros SQL correctos, objetos Product completos  
✅ **DELETE /cart/{productId}** - `remove_from_cart()`: Parámetro `type` correcto según swagger.yaml  
✅ **POST /payment** - `add_payment_method()`: Variables de conexión renombradas  
✅ **DELETE /payment/{paymentMethodId}** - `delete_payment_method()`: Variables de conexión corregidas  
✅ **GET /payment** - `show_user_payment_methods()`: Retorna PaymentMethod serializado  
✅ **POST /purchase** - `set_purchase()`: Usuario extraído correctamente del token  

## Archivos Modificados

1. `swagger_server/controllers/cart_controller.py`
2. `swagger_server/controllers/payment_controller.py`
3. `swagger_server/controllers/purchases_controller.py`

## Validación

✅ No hay errores de sintaxis  
✅ No hay variables indefinidas  
✅ Conformidad con swagger.yaml  
✅ Manejo correcto de excepciones y recursos de base de datos

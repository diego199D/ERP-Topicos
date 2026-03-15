import json
import pymysql

def lambda_handler(event, context):
    conexion = None
    try:
        conexion = pymysql.connect(
            host='erp-diego-ahorro.c564mc4wyknl.us-east-2.rds.amazonaws.com',
            user='admin',
            password='diego199D',
            database='db_inventario',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # Detección mejorada del método para HTTP API y REST API
        metodo = event.get('requestContext', {}).get('http', {}).get('method', event.get('httpMethod'))
        
        with conexion.cursor() as cursor:
            if metodo == 'POST':
                # GUARDAR PRODUCTO
                body = json.loads(event.get('body', '{}'))
                sql = "INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s)"
                cursor.execute(sql, (body.get('nombre'), body.get('precio'), body.get('stock')))
                conexion.commit()
                res = {"mensaje": "✅ Producto añadido correctamente al inventario."}
            else:
                # LISTAR PRODUCTOS (GET)
                cursor.execute("SELECT * FROM productos")
                res = cursor.fetchall()

        return {
            'statusCode': 200,
            'body': json.dumps(res, default=str)
        }

    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
    finally:
        if conexion:
            conexion.close()
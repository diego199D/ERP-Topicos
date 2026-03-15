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
        
        metodo = event.get('requestContext', {}).get('http', {}).get('method', event.get('httpMethod'))
        
        with conexion.cursor() as cursor:
            if metodo == 'POST':
                body = json.loads(event.get('body', '{}'))
                p_id = body.get('producto_id')
                cantidad = body.get('cantidad')
                proveedor = body.get('proveedor', 'Proveedor S.A.')

                # 1. Registrar la Compra
                sql_compra = "INSERT INTO compras (producto_id, cantidad, proveedor) VALUES (%s, %s, %s)"
                cursor.execute(sql_compra, (p_id, cantidad, proveedor))
                
                # 2. SUMAR STOCK (Incrementar)
                sql_update = "UPDATE productos SET stock = stock + %s WHERE id = %s"
                cursor.execute(sql_update, (cantidad, p_id))
                
                conexion.commit()
                return {'statusCode': 200, 'body': json.dumps({'res': '✅ Compra registrada y stock repuesto.'})}
            else:
                cursor.execute("SELECT * FROM compras")
                return {'statusCode': 200, 'body': json.dumps(cursor.fetchall(), default=str)}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
    finally:
        if conexion: conexion.close()
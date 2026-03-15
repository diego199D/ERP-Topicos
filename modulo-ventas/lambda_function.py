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
                c_id = body.get('cliente_id')
                cantidad = body.get('cantidad')

                # 1. ¿Hay stock?
                cursor.execute("SELECT stock, nombre FROM productos WHERE id = %s", (p_id,))
                prod = cursor.fetchone()
                
                if not prod or prod['stock'] < cantidad:
                    return {'statusCode': 400, 'body': json.dumps({'error': 'Stock insuficiente'})}

                # 2. Registrar venta y 3. Restar stock
                cursor.execute("INSERT INTO ventas (producto_id, cliente_id, cantidad) VALUES (%s, %s, %s)", (p_id, c_id, cantidad))
                cursor.execute("UPDATE productos SET stock = stock - %s WHERE id = %s", (cantidad, p_id))
                
                conexion.commit()
                return {'statusCode': 200, 'body': json.dumps({'res': '✅ Venta exitosa'})}
            else:
                # El reporte pro con JOINs
                cursor.execute("""
                    SELECT v.id, p.nombre as producto, c.nombre as cliente, v.cantidad, v.fecha 
                    FROM ventas v
                    JOIN productos p ON v.producto_id = p.id
                    JOIN clientes c ON v.cliente_id = c.id
                """)
                return {'statusCode': 200, 'body': json.dumps(cursor.fetchall(), default=str)}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
    finally:
        if conexion: conexion.close()
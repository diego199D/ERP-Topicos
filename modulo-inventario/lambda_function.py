import json
import pymysql

def lambda_handler(event, context):
    # 1. Conexión a la base de datos
    conexion = pymysql.connect(
        host='erp-diego-ahorro.c564mc4wyknl.us-east-2.rds.amazonaws.com',
        user='admin', password='diego199D', database='db_inventario',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        # 2. Identificar de dónde vienen los datos (API Gateway o Segunda Lambda)
        if isinstance(event.get('body'), str):
            data = json.loads(event['body']) # Viene de afuera (Thunder Client)
        else:
            data = event # Viene de otra Lambda (Venta o Compra)

        # 3. Revisar si nos están pidiendo una "Acción Especial" (Modificar Stock)
        accion = data.get('accion')

        with conexion.cursor() as cursor:
            # CASO A: Una venta o compra nos pide cambiar el stock
            if accion == 'modificar_stock':
                cant = int(data['cantidad']) # Positivo para compra, negativo para venta
                id_p = data['producto_id']
                
                # Intentamos actualizar solo si hay stock suficiente (si es resta)
                sql = "UPDATE productos SET stock = stock + %s WHERE id = %s"
                if cant < 0:
                    sql += " AND stock >= %s"
                    cursor.execute(sql, (cant, id_p, abs(cant)))
                else:
                    cursor.execute(sql, (cant, id_p))
                
                conexion.commit()
                # Si se cambió 1 fila, todo OK. Si es 0, es que no había stock.
                return {"status": "OK" if cursor.rowcount > 0 else "ERROR_STOCK"}

            # CASO B: Petición normal desde el navegador o Thunder Client
            metodo = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
            
            if metodo == 'POST':
                sql = "INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s)"
                cursor.execute(sql, (data['nombre'], data['precio'], data['stock']))
                conexion.commit()
                return {'statusCode': 200, 'body': json.dumps("Producto creado")}
            else:
                cursor.execute("SELECT * FROM productos")
                return {'statusCode': 200, 'body': json.dumps(cursor.fetchall(), default=str)}

    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({"error": str(e)})}
    finally:
        conexion.close()
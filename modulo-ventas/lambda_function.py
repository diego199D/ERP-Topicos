import json
import pymysql
import boto3 # Esta librería es la que permite "llamar" a otras Lambdas

# Creamos el cliente de Lambda fuera del handler para que sea más rápido
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    conexion = None
    try:
        conexion = pymysql.connect(
            host='erp-diego-ahorro.c564mc4wyknl.us-east-2.rds.amazonaws.com',
            user='admin', password='diego199D', database='db_inventario',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        metodo = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
        
        if metodo == 'POST':
            body = json.loads(event.get('body', '{}'))
            prod_id = body.get('producto_id')
            cant = body.get('cantidad')
            clie_id = body.get('cliente_id')

            # --- PASO 1: VISITAR A INVENTARIO PARA DESCONTAR ---
            # Preparamos el mensaje para la otra Lambda
            payload_para_inventario = {
                "accion": "modificar_stock",
                "producto_id": prod_id,
                "cantidad": -abs(int(cant)) # Lo enviamos negativo para que reste
            }

            # Llamamos a la Lambda de Inventario
            respuesta_aws = lambda_client.invoke(
                FunctionName='modulo-inventario', # <--- REVISA QUE ESTE SEA EL NOMBRE EXACTO
                InvocationType='RequestResponse',
                Payload=json.dumps(payload_para_inventario)
            )
            
            # Leemos lo que nos respondió Inventario
            resultado_inv = json.loads(respuesta_aws['Payload'].read())

            # --- PASO 2: SI INVENTARIO DIJO OK, REGISTRAMOS LA VENTA ---
            if resultado_inv.get('status') == 'OK':
                with conexion.cursor() as cursor:
                    sql = "INSERT INTO ventas (producto_id, cliente_id, cantidad) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (prod_id, clie_id, cant))
                    conexion.commit()
                res = {"mensaje": "Venta realizada y stock actualizado por Inventario."}
            else:
                return {
                    'statusCode': 400, 
                    'body': json.dumps({"error": "No hay stock suficiente en Inventario."})
                }
        else:
            # GET: Listar ventas
            with conexion.cursor() as cursor:
                cursor.execute("SELECT * FROM ventas")
                res = cursor.fetchall()
                
        return {'statusCode': 200, 'body': json.dumps(res, default=str)}

    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
    finally:
        if conexion: conexion.close()
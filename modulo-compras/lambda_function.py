import json
import pymysql
import boto3

# Cliente de AWS para llamar a Inventario
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
            cant = int(body.get('cantidad'))
            proveedor = body.get('proveedor')

            # --- PASO 1: PEDIR A INVENTARIO QUE SUME STOCK ---
            payload_para_inventario = {
                "accion": "modificar_stock",
                "producto_id": prod_id,
                "cantidad": abs(cant) # Siempre positivo para que SUME
            }

            respuesta_aws = lambda_client.invoke(
                FunctionName='modulo-inventario', # <--- REVISA QUE SEA EL NOMBRE EXACTO
                InvocationType='RequestResponse',
                Payload=json.dumps(payload_para_inventario)
            )
            
            resultado_inv = json.loads(respuesta_aws['Payload'].read())

            # --- PASO 2: SI INVENTARIO SUMO BIEN, REGISTRAMOS LA COMPRA ---
            if resultado_inv.get('status') == 'OK':
                with conexion.cursor() as cursor:
                    sql = "INSERT INTO compras (producto_id, cantidad, proveedor) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (prod_id, cant, proveedor))
                    conexion.commit()
                res = {"mensaje": "Compra registrada y stock aumentado en Inventario."}
            else:
                return {'statusCode': 400, 'body': json.dumps({"error": "No se pudo actualizar el stock"})}
        else:
            # GET: Listar compras realizadas
            with conexion.cursor() as cursor:
                cursor.execute("SELECT * FROM compras")
                res = cursor.fetchall()
                
        return {'statusCode': 200, 'body': json.dumps(res, default=str)}

    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
    finally:
        if conexion: conexion.close()
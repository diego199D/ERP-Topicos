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
        
        # Esta línea asegura que detecte el POST correctamente
        metodo = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
        
        with conexion.cursor() as cursor:
            if metodo == 'POST':
                body = json.loads(event.get('body', '{}'))
                sql = "INSERT INTO clientes (nombre, email, telefono) VALUES (%s, %s, %s)"
                cursor.execute(sql, (body.get('nombre'), body.get('email'), body.get('telefono')))
                conexion.commit()
                res = {"mensaje": "Cliente registrado con éxito."}
            else:
                cursor.execute("SELECT * FROM clientes")
                res = cursor.fetchall()
                
        return {'statusCode': 200, 'body': json.dumps(res, default=str)}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
    finally:
        if conexion: conexion.close()
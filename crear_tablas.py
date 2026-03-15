import pymysql

HOST = 'erp-diego-ahorro.c564mc4wyknl.us-east-2.rds.amazonaws.com'
USER = 'admin'
PASS = 'diego199D' 
DB_NAME = 'db_inventario'

try:
    conexion = pymysql.connect(host=HOST, user=USER, password=PASS, database=DB_NAME)
    cursor = conexion.cursor()
    
    # 1. Tabla Productos
    cursor.execute("CREATE TABLE IF NOT EXISTS productos (id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(100), precio DECIMAL(10,2), stock INT)")
    
    # 2. Tabla Clientes (Actualizada con email y telefono)
    cursor.execute("DROP TABLE IF EXISTS clientes")
    cursor.execute("CREATE TABLE clientes (id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(100), email VARCHAR(100), telefono VARCHAR(20))")
    
    # 3. Tabla Compras
    cursor.execute("CREATE TABLE IF NOT EXISTS compras (id INT AUTO_INCREMENT PRIMARY KEY, producto_id INT, cantidad INT, proveedor VARCHAR(100), fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    
    # 4. Tabla Ventas
    cursor.execute("CREATE TABLE IF NOT EXISTS ventas (id INT AUTO_INCREMENT PRIMARY KEY, producto_id INT, cliente_id INT, cantidad INT, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    
    conexion.commit()
    print("✅ Todas las tablas (Inventario, Clientes, Compras, Ventas) están listas.")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if 'conexion' in locals(): conexion.close()
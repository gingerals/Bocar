import pyodbc
import re
from flask import Flask, render_template

app = Flask(__name__)

# Conectarse a la base de datos y obtener las ultimas 5 capturas de cada dispositivo
def getSS(device=None):
    # Conectar a SQL Server y ejecutar la consulta
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.2.101;DATABASE=BSNEE;UID=bocar;PWD=oUdIslenDiMA')        
    cursor = conn.cursor()

    # Obtener la lista de categorías/UnitName disponibles
    cursor.execute('''
    ;WITH CTE
    AS(
        SELECT 
            Devices.DeviceID,
            Devices.Label, 
            Devices.UnitName, 
            FilePath,
            LocalTimeStamp,
            ROW_NUMBER() OVER (PARTITION BY DeviceScreenShots.DeviceID ORDER BY LocalTimeStamp DESC) as Capturas
        FROM 
            [BSNEE].[dbo].[DeviceScreenShots]
        INNER JOIN 
            [BSNEE].[dbo].[Devices]
        ON
            Devices.DeviceID = DeviceScreenShots.DeviceID
        WHERE 
            Devices.NetworkID = 19
    )

    SELECT UnitName FROM CTE WHERE Capturas <= 1
    ''')

    devices = [row[0] for row in cursor.fetchall()]

    # Construir la consulta SQL basada en los dispositivos seleccionados
    if device:
        # consulta para obtener las últimas 5 capturas de pantalla de cada dispositivo dentro del NetworkID 19
        sql = f'''
            ;WITH CTE
            AS(
                SELECT 
                    Devices.DeviceID,
                    Devices.Label, 
                    Devices.UnitName, 
                    FilePath,
                    LocalTimeStamp,
                    ROW_NUMBER() OVER (PARTITION BY DeviceScreenShots.DeviceID ORDER BY LocalTimeStamp DESC) as Capturas
                FROM 
                    [BSNEE].[dbo].[DeviceScreenShots]
                INNER JOIN 
                    [BSNEE].[dbo].[Devices]
                ON
                    Devices.DeviceID = DeviceScreenShots.DeviceID
                WHERE 
                    Devices.NetworkID = 19 AND UnitName = '{device}'
            )

            SELECT * FROM CTE WHERE Capturas <= 5
            '''
    else: 
        sql = '''
            ;WITH CTE
            AS(
                SELECT 
                    Devices.DeviceID,
                    Devices.Label, 
                    Devices.UnitName, 
                    FilePath,
                    LocalTimeStamp,
                    ROW_NUMBER() OVER (PARTITION BY DeviceScreenShots.DeviceID ORDER BY LocalTimeStamp DESC) as Capturas
                FROM 
                    [BSNEE].[dbo].[DeviceScreenShots]
                INNER JOIN 
                    [BSNEE].[dbo].[Devices]
                ON
                    Devices.DeviceID = DeviceScreenShots.DeviceID
                WHERE 
                    Devices.NetworkID = 19
            )

            SELECT * FROM CTE WHERE Capturas <= 5
            '''

    cursor.execute(sql)
    results = cursor.fetchall()

    # Reemplazar image_path con URL y filename
    for row in results:
        # Extraer filename de image_path utilizando expresiones regulares
        filename = re.search(r'[^\\/]+$', row.FilePath).group()
        # Reemplazar la primera parte de image_path con la URL
        row.FilePath = 'http://storage.v16.mx/DeviceScreenShots/Public/' + row.Label + '/' + filename

    conn.close()

    # Renderizar el template about con los resultados de la consulta dentro del template index
    return devices, results

def getVideos(fileName):
    # Conectar a SQL Server y ejecutar la consulta
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.2.101;DATABASE=BSNEE;UID=bocar;PWD=oUdIslenDiMA')        
    cursor = conn.cursor()

    # Consultamos el token del video seleccionado

    sql = f'''
    SELECT
        [FileName],
        [UploadToken]

    FROM 
        [BSNEE].[dbo].[Content]
    WHERE 
        Type = 4
    AND 
        NetworkID = 19
    AND 
        FileName = '{fileName}'
    '''

    cursor.execute(sql)
    resultados = cursor.fetchall()

    conn.close()
    
    return resultados

import pyodbc
import re
from flask import Flask, render_template

app = Flask(__name__)

# Connecct to the database and get the latest 5 SS from every device
def db(category=None):
    # Connect to SQL Server and execute query
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.2.101;DATABASE=BSNEE;UID=bocar;PWD=oUdIslenDiMA')        
    cursor = conn.cursor()

    # Get the list of available categories/UnitName
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

    categories = [row[0] for row in cursor.fetchall()]

    # Construct the sql query based on the selected devices
    if category:
        # query to get the last 5 ss from each device within the NetworkID 19
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
                    Devices.NetworkID = 19 AND UnitName = '{category}'
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

    # Replace image_path with URL and filename
    for row in results:
        # Extract filename from image_path using regular expression
        filename = re.search(r'[^\\/]+$', row.FilePath).group()
        # Replace first part of image_path with URL
        row.FilePath = 'http://storage.v16.mx/DeviceScreenShots/Public/' + row.Label + '/' + filename

    conn.close()

    # Render the about template with query result inside the index template
    return categories, results

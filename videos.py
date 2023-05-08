import xml.etree.ElementTree as ET
import pandas as pd
import urllib.request

def getDailyReportTable(url):
    try:
        # Obtener el contenido XML de la URL
        with urllib.request.urlopen(url) as url:
            xml_content = url.read()
        root = ET.fromstring(xml_content)
        worksheet = root.find('{urn:schemas-microsoft-com:office:spreadsheet}Worksheet')
        table = worksheet.find('{urn:schemas-microsoft-com:office:spreadsheet}Table')
        rows = table.findall('{urn:schemas-microsoft-com:office:spreadsheet}Row')
        
        # Obtener los encabezados de la tabla
        headers = []
        for cell in rows[0]:
            data = cell.find('{urn:schemas-microsoft-com:office:spreadsheet}Data')
            headers.append(data.text)
        
        # Obtener los datos de la tabla
        rows_data = []
        for row in rows[1:]:
            row_data = []
            for cell in row:
                data = cell.find('{urn:schemas-microsoft-com:office:spreadsheet}Data')
                row_data.append(data.text)
            rows_data.append(row_data)
        
        # Crear el DataFrame
        df = pd.DataFrame(rows_data, columns=headers)
        df = df.query("`Media Type` == 'video'")
        
        return df
    except Exception as e:
        print(f'Error al procesar el archivo XML: {e}')

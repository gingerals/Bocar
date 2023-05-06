import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

def getSoup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup

def getDailyReport(playerID):
    # Se define una URL base a la que se le pasa el id del player que estamos buscando
    url_base = 'http://storage.v16.mx/DeviceLogs/Reports/{playerID}/BOCAR/playback/'.format(playerID=playerID)

    # Parseamos el contenido de la respuesta a través de xml-etree.ElementTree
    soup = getSoup(url_base)

    mensaje = f"No se ha podido encontrar el archivo"
    
    # Buscamos los enlaces a los archivos DailyReport.xml y determinamos el más reciente 
    link = soup.find("a")  # Iniciamos en el primer enlace

    while link is not None:

        sublink = urljoin(url_base, link.get("href"))
        print(f"Actualizando dirección: {sublink}")
        
        # Si el enlace contiene el texto "[To Parent Directory]", lo omitimos
        if "[To Parent Directory]" in link.text:
            link = link.find_next("a")
            print(f'Omitiendo enlace de retorno: {link}')
            continue

        # Si el enlace contiene "DailyReport.xml", se ha encontrado el archivo
        if "DailyReport.xml" in sublink:
            mensaje = f"URL del DailyReport más reciente: {sublink}"
        else:
             # Si el enlace no contiene el archivo, actualizamos el objeto soup
            soup = getSoup(sublink)
            link = soup.find("a")

        # Buscamos en el siguiente enlace
        link = link.find_next("a") if link is not None else None
    
    return mensaje

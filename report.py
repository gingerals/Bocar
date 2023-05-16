from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


def getSoup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


def es_enlace_numero(enlace):
    """
    Comprueba si un enlace es numérico o no
    """
    try:
        int(enlace.text.strip("/"))
        return True
    except ValueError:
        return False

def obtener_fecha_anterior(soup, url_base):
    """
    Obtiene la fecha del DailyReport más reciente de un directorio
    """
    enlaces = soup.find_all("a")
    enlaces_numericos = [enlace for enlace in enlaces if es_enlace_numero(enlace)]
    if not enlaces_numericos:
        return None
    
    url_fecha = max(enlaces_numericos, key=lambda x: int(x.text.strip("/")))
    fecha = url_fecha.text.strip("/")
    print(f"Obteniendo {fecha}")
    url_fecha_completa = urljoin(url_base, url_fecha.get("href"))
    soup_fecha = getSoup(url_fecha_completa)
    
    return fecha, soup_fecha

def getDailyReportURL(playerID):
    print('\nComenzando búsqueda\n\n')
    url_base = f'http://storage.v16.mx/DeviceLogs/Reports/{playerID}/BOCAR/playback/'
    soup = getSoup(url_base)
    mensaje = "No se ha podido encontrar el archivo"
    
    fecha_actual, soup_actual = obtener_fecha_anterior(soup, url_base)
    while fecha_actual is not None:
        url_fecha_actual = urljoin(url_base, fecha_actual)
        fecha_actual_soup = obtener_fecha_anterior(soup_actual, url_fecha_actual)
        if fecha_actual_soup is None:
            break
        fecha_actual, soup_actual = fecha_actual_soup
        if fecha_actual is not None:
            print(f"\nAvanzando a la fecha {fecha_actual}")
    
    enlaces = soup_actual.find_all("a")
    enlace_reporte = None
    for enlace in enlaces:
        if enlace.text == "DailyReport.xml":
            enlace_reporte = enlace
            break

    if enlace_reporte is not None:
        url_reporte = urljoin(url_base, enlace_reporte.get("href"))
        mensaje = url_reporte
        print(f"\nReporte obtenido en: {url_reporte}")

    return mensaje

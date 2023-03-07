import socket
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import argparse
import requests
from pandas import read_excel, DataFrame

import sys

fichero = 'COpenMed_20230219.xlsx'
hoja_links = 6
indice = 'URL'
numRegistrosComprobar = 500

if (len(sys.argv)>1):
    if (str(sys.argv[1]) != "COpenMed_20230219.xlsx"):
        fichero = sys.argv[1]
        hoja_links = 0
        indice = 0
    else:
        fichero = 'COpenMed_20230219.xlsx'
        hoja_links = 6
        indice = 'URL'

else:
    print("Este programa soporta la introducción de un fichero a procesar por parámetros")
    print("Para indicar el archivo excel de links a examinar debe de pasarse como primer parámetro")
    print("El excel ha de incluir en la 1a hoja, 2a columna, en la casilla B1 un 0 para poder identificar que es la columna a analizar")
    print("Ejemplo:")
    print("./valida_links.py <fichero_excel_links_analizar>")
    print("")
    print("")

# Leemos el excel, la hoja con los links
df_sheet_index = read_excel(fichero, sheet_name=hoja_links)

# Debug: mostrar todos los enlaces URL presentes en el excel
# print(df_sheet_index['URL'])
# print(df_sheet_index[0])

print("Analizando Links...")

def make_request(url):
    if "file://" not in url:
        if "https://" not in url:
            if "http://" not in url:
                url2 = "https://" + url
            else:
                url2 = url[url.find("http://") + 7:]
                url2 = "http://" + str(url2)
        else:
            url2 = url[url.find("https://") + 8:]
            url2 = "https://" + str(url2)
    else:
        url2 = url[url.find("file://") + 7:]
        url2 = "file://" + str(url2)

    url2 = url2.encode('ascii', errors='ignore').decode('ascii')

    if "file://" not in url:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"
        }
        try:

            response = requests.get(url2, headers=headers, timeout=(20, 25))
            return response.status_code

        except requests.exceptions.Timeout as e:
            # Como no devuelve status_code, se le asigna un valor de 408 Request Timeout
            print('408 Timeout URL: ' + str(url2))
            return 408

        except requests.exceptions.TooManyRedirects as e:
            print('408 TooManyRedirects URL: ' + str(url2))
            return 408


        except requests.exceptions.ConnectTimeout:
            print('408 ConnectTimeout URL: ' + str(url2))
            return 408

        except requests.exceptions.RequestException:
            print('408 RequestException URL: ' + str(url2))
            return 408

        except requests.exceptions.SSLError:
            print('409 SSLError URL: ' + str(url2))
            return 409

    else:
        # Los file hay que comprobarlos de otra forma
        req = Request(url2)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36')
        try:
            with urlopen(req, timeout=30) as response2:
                return response2.status
        except HTTPError as error:
            print("HTTPError  URL ES: " + str(url2) + "  " + str(error.reason))
            return str(error.status) + " " + error.reason
        except URLError as error:
            print("URLError  URL ES: " + str(url2) + "  " + str(error.reason))
            return error.reason
        except TimeoutError:
            print("TimeoutError URL ES: " + str(url2))
            return "Request timed out"


# Creamos un listado con los links caidos
links_caidos = []
cell = -1
registrosComprobados = -1
for link in df_sheet_index[indice]:
    registrosComprobados += 1
    cell += 1
    if registrosComprobados <= numRegistrosComprobar:
        try:
            codeReturned = make_request(link)
            # Si el link no devuelve OK, se añade a la lista de links caidos
            if codeReturned != 200 and codeReturned != 406:  # scielo.isciii.es da errores 503 y van          and codeReturned != 503
                if "scielo.isciii" in link:
                    continue
                links_caidos.append(link)
                print(str(codeReturned) + " LINK CAIDO: " + link)

        except socket.timeout:  # si es scielo si que va, falso positivo
            if "scielo.isciii" in link:
                continue
            links_caidos.append(link)
            print("TIMEOUT" + " LINK CAIDO: " + link)
    else:
        # Si es un link que no toca comprobar se añade para la comprobar la próxima vez
        links_caidos.append(link)


    # Convertimos la lista de links caidos a un Dataframe pandas
codesReceived = DataFrame(links_caidos)

# Generamos el excel con los datos caidos
fichero_nombre = fichero
if ".xls" in fichero:
    fichero_nombre = fichero[:-4]
if ".xlsx" in fichero:
    fichero_nombre = fichero[:-5]

codesReceived.to_excel(fichero_nombre + "__VALIDADO.xlsx")

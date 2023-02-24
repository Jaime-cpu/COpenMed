import socket

from pandas import read_excel, DataFrame
import urllib.request
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Leemos el excel, la hoja con los links
df_sheet_index = read_excel('COpenMed_20230219.xlsx', sheet_name=6)


# Debug: mostrar todos los enlaces URL presentes en el excel
# print(df_sheet_index['URL'])

def make_request(url):
    req = Request(url)
    req.add_header('User-Agent'.encode('utf-8').strip(), 'Mozilla/5.0'.encode('utf-8').strip())

    try:
        with urlopen(req, timeout=10) as response:
            # print(response.status)
            return response.status
    except HTTPError as error:
        # print(error.status, error.reason)
        return str(error.status) + " " + error.reason
    except URLError as error:
        # print(error.reason)
        return error.reason
    except TimeoutError:
        # print("Request timed out")
        return "Request timed out"


# Creamos un listado con los links caidos
links_caidos = []
cell = -1

for link in df_sheet_index['URL']:
    cell += 1
    try:
        codeReturned = make_request(link)
        # Si el link no devuelve OK, se añade a la lista de links caidos
        if codeReturned != 200 and codeReturned != 406 : # scielo.isciii.es da errores 503 y van          and codeReturned != 503
            if "scielo.isciii" in link:
                continue
            links_caidos.append(link)
            print(str(codeReturned) + " LINK CAIDO: " + link)

    except socket.timeout: # si es scielo si que va, falso positivo
        if "scielo.isciii" in link:
            continue
        links_caidos.append(link)
        print("TIMEOUT" + " LINK CAIDO: " + link)

# Convertimos la lista de links caidos a un Dataframe pandas
codesReceived = DataFrame(links_caidos)

# Generamos el excel con los datos caidos
codesReceived.to_excel("COpenMed_20230219__VALIDADO.xlsx")

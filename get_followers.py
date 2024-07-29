import requests
import time

# Limitations: 15req/15min 75000 user_ids to retrieve every 15 minutes = 7.200.000 user_ids per day.

# aqui el bearer del api academico
bearer="AAAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# esta funcion debe ser substituida por una encargada de insertar los usuarios en la tabla USER
# seguidamente comprobar si la relacion seguidor-seguido que se acaba de recuperar existe
# si no existe crearla en la tabla FOLLOW
# A su vez, se debe comprobar si los seguidores descargados corresponden con los seguidores registrados en la DB
# Para de esta manera ver si algun usuario HA PERDIDO SEGUIDORES, si es el caso, insertar el registro correspondiente
# en la tabla UNFOLLOW
# Se debe implementar una mecanismo sencillo estilo try-catch para realizar la espera necesaria en el caso de que la API
# haya alcanzado el # maximo de requests por minuto. 
def to_file(user_ids, username):
    with open(str(username)+".txt", 'a') as f:
        for line in user_ids:
            print(line)
            f.write(f"{line}\n")

# usuarios de los que descargar seguidores
user_list = ["elonmusk", "billgates"]

for user in user_list:

    ses=requests.Session()
    ses.headers["Authorization"] = f"Bearer {bearer}"
    ses.headers["User-Agent"] = "FOLLOWER.DOWNLADER.TOOL"

    url = "https://api.twitter.com/1.1/followers/ids.json?screen_name="+str(user)

    params = {
            "count":5000
    }

    rc=ses.get(url=url, params=params, timeout=5)
    time.sleep(60)

    if rc:
        jrc = rc.json()
        if "ids" in jrc.keys():
            to_file(jrc["ids"], user)

        while "next_cursor_str" in jrc.keys():
            next_cursor = jrc["next_cursor_str"]
            params = {
            "count":5000,
            "cursor":next_cursor
            }
            rc=ses.get(url=url, params=params, timeout=5)
            time.sleep(60)
            jrc = rc.json()
            if "ids" in jrc.keys():
                to_file(jrc["ids"], user)

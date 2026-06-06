import subprocess
import json
import time
from datetime import datetime

DESTINOS = ["192.168.10.1", "192.168.10.2"]
ARCHIVO_SALIDA = "datos_prueba.json"

def ejecutar_comando(comando):
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, timeout=10)
        return resultado.stdout
    except subprocess.TimeoutExpired:
        return "Timeout"
    except Exception as e:
        return str(e)

def main():
    datos_totales = []

    while True:
        marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ciclo = {"timestamp": marca_tiempo, "destinos": {}}

        for ip in DESTINOS:
            # Ping de 80 bytes
            salida_ping = ejecutar_comando(f"ping -c 3 -s 80 {ip}")
            # Traceroute BATMAN
            salida_batman = ejecutar_comando(f"sudo batctl tr {ip}")

            ciclo["destinos"][ip] = {
                "ping_80bytes": salida_ping,
                "batman_hops": salida_batman
            }

        datos_totales.append(ciclo)

        with open(ARCHIVO_SALIDA, 'w') as f:
            json.dump(datos_totales, f, indent=4)

        time.sleep(5)

if __name__ == "__main__":
    main()
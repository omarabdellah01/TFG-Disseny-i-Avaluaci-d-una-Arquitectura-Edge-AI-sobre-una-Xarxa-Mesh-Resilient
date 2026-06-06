import cv2
import json
import time
import socket
from ultralytics import YOLO

# --- CONFIGURACIÓ DE XARXA MESH (BATMAN-adv) ---
DEST_IP = "192.168.10.1"  # IP del node central
DEST_PORT = 5000          # Port TCP d'escolta

# 1. Càrrega del model optimitzat per a hardware NVIDIA
print("[SISTEMA] Carregant motor d'inferència YOLO (TensorRT)...")
# Utilitzem el model .engine exportat per a màxim rendiment a la Jetson Nano
model = YOLO("yolov8n.engine") 

img_path = "prueba_yolo.jpg"
img = cv2.imread(img_path)

if img is None:
    print("[ERROR] No s'ha pogut llegir el fotograma d'entrada.")
else:
    # 3. Execució de la inferència (One-pass)
    results = model(img)

    # 4. Processament de resultats i Filtratge Semàntic
    print("\n--- ANÀLISI DE VÍDEO (EDGE COMPUTING) ---")
    alertes_generades = []
    
    for r in results:
        for box in r.boxes:
            conf = float(box.conf[0])
            
            # FILTRE TALLAFOCS: Només processem si la certesa és > 80% (Secció 4.4 del TFG)
            if conf > 0.80:
                clase = model.names[int(box.cls[0])]
                
                # Extracció de coordenades del Bounding Box (quadre delimitador)
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Generació de la càrrega útil (Payload de metadades)
                alerta = {
                    "timestamp": round(time.time(), 2),
                    "clase": clase,
                    "confianza": round(conf, 2),
                    "bbox": [x1, y1, x2, y2]
                }
                alertes_generades.append(alerta)
                print(f"ALERTA VÀLIDA: {clase.upper()} (Confiança: {conf:.2f}) -> Coordenades: {x1},{y1},{x2},{y2}")
            else:
                # Falsos positius descartats localment, no saturen la xarxa Mesh
                pass 

    # 5. Descàrrega de dades a la xarxa (Offloading - Secció 4.3 del TFG)
    if alertes_generades:
        # Serialització binària a format JSON
        payload_json = json.dumps(alertes_generades)
        payload_bytes = payload_json.encode('utf-8')
        
        print(f"\n[XARXA] Transmetent paquet JSON d'emergència ({len(payload_bytes)} bytes).")
        
        # Obertura de Socket TCP i transmissió al node destí
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2.0)
                s.connect((DEST_IP, DEST_PORT))
                s.sendall(payload_bytes)
                print(f"[XARXA] Dades entregades amb èxit a {DEST_IP}:{DEST_PORT}.")
        except Exception as e:
            print(f"[XARXA] Error de transmissió a la malla: {e}")
    else:
        print("\n[XARXA] Cap anomalia rellevant.")
# TFG-Disseny-i-Avaluació-d´una-Arquitectura-Edge-AI-sobre-una-Xarxa-Mesh-Resilient
This repository contains the data, configuration scripts, and visualization code for the Bachelor's Thesis (TFG): **"Disseny i Avaluació d'una Arquitectura Edge AI sobre una Xarxa Mesh Resilient"** by Omar Abdellah Khaddaj (Universitat Pompeu Fabra).

The project demonstrates how combining decentralized Mesh routing (BATMAN-adv) with Edge Computing (YOLOv8 on NVIDIA Jetson Orin Nano) creates a resilient, self-healing communication system capable of operating in disaster zones without centralized infrastructure.

## 📂 Repository Structure

* **`/Data`**: Contains the raw datasets extracted during physical testbed experimentation.
    * `datos_prueba.json`: One-way latency data mapped against physical distance.
    * `data_Fig11.txt`: UDP throughput logs during the extreme Triple-Failover (Self-Healing) experiment.
    * `datos_metadatas_edge.json` & `datos_video_4Mbps.json`: Network payload analysis for Edge AI vs Cloud Streaming comparison.
* **`/Figures`**: Python scripts (`matplotlib`, `seaborn`) used to generate the academic figures and heatmaps presented in Chapter 5 of the thesis. 
* **`/Systems and Network Configuration`**: Low-level bash scripts and Python code for hardware deployment.
    * `jetsonnano_mesh.txt` / `raspberry_mesh.txt`: Network interfaces setup, Ad-Hoc mode, MTU tuning, and BATMAN-adv initialization.
    * `yolo.py`: Edge AI inference script using YOLOv8 (TensorRT optimized) and socket-based JSON telemetry offloading.

## ⚙️ Hardware Testbed
* **Gateway / Edge Node:** NVIDIA Jetson Orin Nano (JetPack 6, L4T).
* **Relay Nodes:** Raspberry Pi 4 Model B.
* **Protocol:** BATMAN-adv (Layer 2 routing) over 2.4 GHz (Channel 11).

## Usage
To reproduce the figures from the thesis, navigate to the `/Figures` directory and run the corresponding script. Make sure to have `pandas`, `matplotlib`, and `seaborn` installed:
```bash
pip install pandas matplotlib seaborn
python3 Fig11.py

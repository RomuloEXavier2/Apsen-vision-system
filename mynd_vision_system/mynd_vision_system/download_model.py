# -*- coding: utf-8 -*-
from roboflow import Roboflow
import os

def baixar_pesos():
    # Substitua pela sua API Key (Settings -> API Keys no Roboflow)
    rf = Roboflow(api_key="SUA_API_KEY_AQUI") 

    project = rf.workspace("mynds-workspace").project("find-small-boxes-pyutr")
    version = project.version(1) 

    # Baixa no formato YOLOv11
    dataset = version.download("yolov11")

    print(f"\n[!] Download concluído!")
    print(f"[!] Vá até a pasta '{dataset.location}/weights/' e mova o 'best.pt' para a pasta 'models/' do projeto.")

if __name__ == "__main__":
    baixar_pesos()

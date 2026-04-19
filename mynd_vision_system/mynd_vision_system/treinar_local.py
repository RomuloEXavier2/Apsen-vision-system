# -*- coding: utf-8 -*-
from ultralytics import YOLO
import os

def treinar():
    # Carrega o modelo base (YOLOv11 Nano - ideal para velocidade)
    model = YOLO("yolo11n.pt") 

    # Caminho para o arquivo YAML que criamos
    yaml_path = "dataset_local.yaml"

    print(f"[*] Iniciando treinamento com dataset em: {yaml_path}")

    # Treinamento
    model.train(
        data=yaml_path,
        epochs=100,      # Para 0 erros, 100 épocas é o ideal
        imgsz=640,
        device="cpu",    # Se tiver GPU NVIDIA, mude para 0
        project="mynd_finance_v1",
        name="detector_caixas_real"
    )

    print("\n[!] TREINO FINALIZADO!")
    print("[!] Seu modelo 'best.pt' estará em: mynd_finance_v1/detector_caixas_real/weights/best.pt")

if __name__ == "__main__":
    treinar()

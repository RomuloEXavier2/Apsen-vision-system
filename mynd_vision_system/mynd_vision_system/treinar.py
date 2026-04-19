# -*- coding: utf-8 -*-
from ultralytics import YOLO

def treinar():
    # Carrega o modelo base
    model = YOLO("yolo11n.pt") 

    # Treina o modelo com seus dados locais
    model.train(
        data="dataset/data.yaml",
        epochs=50,
        imgsz=640,
        device="cpu", # Mude para 0 se tiver placa NVIDIA (GPU)
        project="mynd_model",
        name="versao_1"
    )
    print("Treino concluído! O melhor modelo estará em: mynd_model/versao_1/weights/best.pt")

if __name__ == "__main__":
    treinar()

# -*- coding: utf-8 -*-
import os


def update_to_external_dataset():
    project_dir = "mynd_vision_system"
    # Caminho onde está o seu dataset baixado (Ajuste o caminho se necessário)
    # No Windows, o padrão é C:/Users/SEU_USUARIO/Downloads/...
    user_path = os.path.expanduser("~")
    dataset_path = os.path.join(user_path, "Downloads", "Find small boxes.v2-continuous-improvement-2026-04-19.yolov11")

    # Normaliza caminhos para evitar erro de barra no Windows
    dataset_path = dataset_path.replace("\\", "/")

    os.makedirs(f"{project_dir}/models", exist_ok=True)

    # 1. CRIANDO O data.yaml CUSTOMIZADO
    # Ele aponta diretamente para a pasta de Downloads
    data_yaml_content = f"""
path: {dataset_path}
train: train/images
val: valid/images
test: test/images

names:
  0: Medicamento  # O Roboflow geralmente exporta a partir do 0
"""
    with open(f"{project_dir}/dataset_local.yaml", "w", encoding="utf-8") as f:
        f.write(data_yaml_content)

    # 2. SCRIPT DE TREINAMENTO (treinar_local.py)
    train_script = r'''# -*- coding: utf-8 -*-
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
'''

    with open(f"{project_dir}/treinar_local.py", "w", encoding="utf-8") as f:
        f.write(train_script)

    print(f"[*] PROJETO CONFIGURADO PARA DATASET EXTERNO.")
    print(f"[!] Caminho detectado: {dataset_path}")
    print("[!] Próximo passo: No PyCharm, execute 'treinar_local.py'.")


if __name__ == "__main__":
    update_to_external_dataset()
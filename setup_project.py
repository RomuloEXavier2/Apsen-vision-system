import os


def create_project():
    # 1. Estrutura de Diretórios
    project_name = "mynd_vision_system"
    folders = [
        project_name,
        f"{project_name}/models",
        f"{project_name}/logs",
        f"{project_name}/utils"
    ]

    print(f"[*] Iniciando criação do projeto: {project_name}")
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"[+] Pasta criada: {folder}")

    # 2. Arquivo de Requisitos
    requirements = """ultralytics
opencv-python
numpy
torch
torchvision
"""
    with open(f"{project_name}/requirements.txt", "w") as f:
        f.write(requirements)
    print("[+] Arquivo requirements.txt gerado.")

    # 3. Código Principal (main.py)
    main_code = """import cv2
import os
import logging
from datetime import datetime
from ultralytics import solutions

# Configuração de Logs Profissionais
if not os.path.exists('logs'):
    os.makedirs('logs')

log_file = f"logs/contagem_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
)

class MyndVision:
    def __init__(self, model_name="yolo11n-obb.pt", source=0):
        self.source = source
        self.model_path = model_name

        # Definição da ROI (Região de Interesse) - Quadrante de Contagem
        # Formato: [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        self.region_points = [(100, 600), (1180, 600), (1180, 100), (100, 100)]

        logging.info(f"Carregando modelo {model_name}...")
        self.counter = solutions.ObjectCounter(
            show=True,
            region=self.region_points,
            model=self.model_path,
            line_width=2,
            conf=0.6,
            persist=True
        )
        self.cap = None

    def executar(self):
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            logging.error("Falha ao abrir fonte de vídeo.")
            return

        print("\\n--- MONITORAMENTO ATIVO: PRESSIONE 'Q' PARA PARAR ---")

        try:
            while self.cap.isOpened():
                success, frame = self.cap.read()
                if not success:
                    break

                # Processamento central do Ultralytics Solutions
                annotated_frame = self.counter.count(frame)

                # Feedback de contagem no console para auditoria
                # O atributo in_count é o total acumulado de itens que entraram na zona
                print(f"\\rItens Detectados: {self.counter.in_count}", end="")

                cv2.imshow("Mynd Vision System - Zero Divergencia", annotated_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            logging.info(f"Processo finalizado. Total final: {self.counter.in_count}")

if __name__ == "__main__":
    app = MyndVision()
    app.executar()
"""
    with open(f"{project_name}/main.py", "w") as f:
        f.write(main_code)
    print("[+] Arquivo main.py gerado com lógica OBB.")

    # 4. Arquivo de README/Instruções
    readme = f"""# Mynd Vision System - Guia Rápido

1. Instale as dependências:
   pip install -r requirements.txt

2. Execute o sistema:
   python main.py

3. Calibração:
   Edite a variável `self.region_points` no `main.py` para alinhar com sua esteira/bancada.
"""
    with open(f"{project_name}/README.md", "w") as f:
        f.write(readme)
    print("[+] Arquivo README.md gerado.")

    print(f"\\n[!] PROJETO PRONTO. Entre na pasta '{project_name}' e siga o README.")


if __name__ == "__main__":
    create_project()
# -*- coding: utf-8 -*-
import cv2
import os
import logging
import numpy as np
from datetime import datetime
from ultralytics import solutions

# Configuração de Logs
if not os.path.exists('logs'):
    os.makedirs('logs')

log_file = f"logs/contagem_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(log_file, encoding='utf-8'), logging.StreamHandler()]
)


class MyndVision:
    def __init__(self, model_name="yolo11n-obb.pt", source=0):
        self.source = source
        self.model_path = model_name
        self.region_points = [(100, 600), (1180, 600), (1180, 100), (100, 100)]

        logging.info(f"Carregando modelo {model_name}...")

        self.counter = solutions.ObjectCounter(
            model=self.model_path,
            region=self.region_points,
            show=False,
            line_width=2,
            conf=0.4  # Reduzi um pouco para facilitar o teste inicial
        )
        self.cap = None

    def executar(self):
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            logging.error("Falha ao abrir fonte de vídeo.")
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        print("\n--- MONITORAMENTO MYND ATIVO: PRESSIONE 'Q' PARA PARAR ---")

        try:
            while self.cap.isOpened():
                success, frame = self.cap.read()
                if not success:
                    break

                # 1. Processa o frame
                # Em algumas versões da SDK, o retorno de counter(frame) é None
                # e a imagem fica em self.counter.im0
                self.counter(frame)

                # 2. Captura a imagem anotada gerada internamente
                annotated_frame = getattr(self.counter, 'im0', frame)

                # 3. Lógica de contagem robusta
                c_in = getattr(self.counter, 'in_counts', getattr(self.counter, 'in_count', 0))
                c_out = getattr(self.counter, 'out_counts', getattr(self.counter, 'out_count', 0))

                print(f"\rLOGÍSTICA MYND -> Entrada: {c_in} | Saída: {c_out}", end="")

                # 4. Verifica se a imagem é válida para o imshow
                if annotated_frame is not None and isinstance(annotated_frame, np.ndarray):
                    cv2.imshow("Mynd Vision System - Zero Divergencia", annotated_frame)
                else:
                    cv2.imshow("Mynd Vision System - Zero Divergencia", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            logging.error(f"Erro durante a execução: {e}")
        finally:
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            logging.info("Sistema finalizado.")


if __name__ == "__main__":
    app = MyndVision(source=0)
    app.executar()
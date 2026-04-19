# -*- coding: utf-8 -*-
import cv2
import os
import logging
from ultralytics import solutions

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class MyndIndustrialEngine:
    def __init__(self, model_name="best.pt"):
        # Localização do seu modelo treinado no Roboflow
        self.model_path = os.path.join("models", model_name)

        if not os.path.exists(self.model_path):
            logging.error(f"ERRO: O arquivo {self.model_path} não foi encontrado na pasta models!")
            return

        # ROI: Região de contagem (Ajustada para pegar a parte central da visão)
        self.region_points = [(50, 650), (1230, 650), (1230, 100), (50, 100)]

        logging.info(f"MOTOR MYND CARREGADO: {self.model_path}")

        # Inicializando com ByteTracker Nativo (Alta Precisão)
        self.counter = solutions.ObjectCounter(
            model=self.model_path,
            region=self.region_points,
            show=False,
            conf=0.6,   # Confiança alta para evitar contagens fantasmas
            line_width=2
        )

    def rodar(self, source=0):
        cap = cv2.VideoCapture(source)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        print("\n[V1] SISTEMA DE VISÃO 'FIND SMALL BOXES' OPERACIONAL")

        try:
            while cap.isOpened():
                success, frame = cap.read()
                if not success: break

                # Inferência Local (Sem dependência de API do Roboflow)
                self.counter(frame)

                # Renderização
                annotated_frame = getattr(self.counter, 'im0', frame)
                count = getattr(self.counter, 'in_counts', getattr(self.counter, 'in_count', 0))

                # Feedback de Autoridade Mynd
                cv2.putText(annotated_frame, f"MYND BOX COUNT: {count}", (50, 60), 
                            cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 0), 2)

                cv2.imshow("MYND INDUSTRIAL VISION - EDGE", annotated_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()
            logging.info("Sessão finalizada com sucesso.")

if __name__ == "__main__":
    engine = MyndIndustrialEngine(model_name="best.pt")
    if hasattr(engine, 'counter'):
        engine.rodar(source=0)

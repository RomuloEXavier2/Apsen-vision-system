# -*- coding: utf-8 -*-
"""
MYND Industrial Vision — contagem de caixas de medicamento com YOLOv11.

Uso:
    python main.py                         # câmera 0, modelo models/best.pt
    python main.py --source video.mp4      # arquivo de vídeo
    python main.py --conf 0.5 --source 1   # outra câmera / outra confiança

A ROI (região de contagem) é lida de roi.json, gerado por calibrar_roi.py.
Sem roi.json, usa a ROI padrão abaixo (resolução 1280x720).
"""
import argparse
import json
import logging
import os
from datetime import datetime

import cv2
from ultralytics import solutions

DEFAULT_ROI = [(50, 650), (1230, 650), (1230, 100), (50, 100)]
ROI_FILE = "roi.json"

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"logs/contagem_{datetime.now():%Y%m%d}.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


def carregar_roi(path=ROI_FILE):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            pts = [tuple(p) for p in json.load(f)["region_points"]]
        logging.info(f"ROI carregada de {path}: {pts}")
        return pts
    logging.info("roi.json não encontrado — usando ROI padrão.")
    return DEFAULT_ROI


class MyndIndustrialEngine:
    def __init__(self, model_path, conf=0.6, region=None):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo não encontrado: {model_path}")
        self.region_points = region or carregar_roi()
        self.counter = solutions.ObjectCounter(
            model=model_path,
            region=self.region_points,
            show=False,
            conf=conf,  # confiança alta evita contagens fantasmas
            line_width=2,
        )
        logging.info(f"Motor MYND carregado: {model_path} (conf={conf})")

    def rodar(self, source=0):
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            logging.error(f"Falha ao abrir a fonte de vídeo: {source}")
            return
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        print("\n[MYND] Visão operacional — pressione 'Q' para encerrar")
        count = 0
        try:
            while cap.isOpened():
                ok, frame = cap.read()
                if not ok:
                    break
                result = self.counter(frame)
                # compatível com versões novas (SolutionResults) e antigas (im0 / in_count)
                annotated = getattr(result, "plot_im", None)
                if annotated is None:
                    annotated = getattr(self.counter, "im0", frame)
                count = getattr(result, "in_count",
                                getattr(self.counter, "in_count", getattr(self.counter, "in_counts", 0)))

                cv2.putText(annotated, f"MYND BOX COUNT: {count}", (50, 60),
                            cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 0), 2)
                cv2.imshow("MYND INDUSTRIAL VISION - EDGE", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()
            logging.info(f"Sessão finalizada. Contagem final: {count}")


def main():
    ap = argparse.ArgumentParser(description="MYND Industrial Vision — contagem por ROI")
    ap.add_argument("--model", default=os.path.join("models", "best.pt"))
    ap.add_argument("--source", default="0", help="índice da câmera ou caminho de vídeo")
    ap.add_argument("--conf", type=float, default=0.6)
    args = ap.parse_args()
    source = int(args.source) if args.source.isdigit() else args.source
    MyndIndustrialEngine(args.model, conf=args.conf).rodar(source)


if __name__ == "__main__":
    main()

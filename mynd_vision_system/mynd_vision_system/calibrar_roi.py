# -*- coding: utf-8 -*-
"""
Calibração da ROI com o mouse.

    python calibrar_roi.py            # câmera 0
    python calibrar_roi.py --source 1

Clique nos 4 cantos da área de contagem (em qualquer ordem, de preferência
no sentido horário). Teclas:  R = refazer   S = salvar roi.json   Q = sair
"""
import argparse
import json

import cv2
import numpy as np

pontos = []


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(pontos) < 4:
        pontos.append((x, y))
        print(f"Ponto {len(pontos)}: ({x}, {y})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="0")
    ap.add_argument("--out", default="roi.json")
    args = ap.parse_args()
    source = int(args.source) if args.source.isdigit() else args.source

    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    win = "Calibrar ROI - MYND"
    cv2.namedWindow(win)
    cv2.setMouseCallback(win, on_mouse)

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Falha ao ler a câmera.")
            break
        for p in pontos:
            cv2.circle(frame, p, 6, (0, 255, 255), -1)
        if len(pontos) > 1:
            cv2.polylines(frame, [np.array(pontos, np.int32)], len(pontos) == 4, (0, 255, 0), 2)
        cv2.putText(frame, f"Pontos: {len(pontos)}/4  |  R refazer  S salvar  Q sair",
                    (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow(win, frame)

        k = cv2.waitKey(1) & 0xFF
        if k == ord("r"):
            pontos.clear()
        elif k == ord("s") and len(pontos) == 4:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump({"region_points": pontos, "resolution": [frame.shape[1], frame.shape[0]]}, f, indent=2)
            print(f"ROI salva em {args.out}: {pontos}")
            break
        elif k == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

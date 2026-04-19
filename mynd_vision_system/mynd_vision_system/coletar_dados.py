# -*- coding: utf-8 -*-
import cv2
import os
import uuid

cap = cv2.VideoCapture(0)
save_path = "dataset/train/images"
os.makedirs(save_path, exist_ok=True)

print("Posicione a caixa e aperte 'S' para salvar. 'Q' para sair.")

while True:
    ret, frame = cap.read()
    cv2.imshow("Coleta de Dados Mynd", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        img_name = f"{save_path}/img_{uuid.uuid4().hex[:6]}.jpg"
        cv2.imwrite(img_name, frame)
        print(f"Foto salva: {img_name}")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

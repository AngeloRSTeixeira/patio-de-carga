"""Gera as texturas usadas na cena (origem: criadas por este script).
Uso: python gerar_texturas.py
"""
import os
import random
from PIL import Image, ImageDraw

random.seed(7)
os.makedirs("images", exist_ok=True)

# Chão: placas de concreto 4x4 com juntas e ruído
N = 512
img = Image.new("RGB", (N, N))
px = img.load()
for y in range(N):
    for x in range(N):
        v = 150 + random.randint(-18, 18)
        px[x, y] = (v, v, v - 5)
d = ImageDraw.Draw(img)
for i in range(0, N + 1, 128):
    d.line([(i, 0), (i, N)], fill=(95, 95, 92), width=4)
    d.line([(0, i), (N, i)], fill=(95, 95, 92), width=4)
img.save("images/chao_concreto.png")

# Caixa de madeira: tábuas, moldura e travessa diagonal
M = 256
img = Image.new("RGB", (M, M))
px = img.load()
for y in range(M):
    tabua = y // 64
    for x in range(M):
        r = 170 + 10 * (tabua % 2) + random.randint(-12, 12)
        px[x, y] = (r, int(r * 0.68), int(r * 0.38))
d = ImageDraw.Draw(img)
for i in range(64, M, 64):
    d.line([(0, i), (M, i)], fill=(90, 55, 25), width=3)
moldura = (120, 75, 35)
d.rectangle([0, 0, M - 1, M - 1], outline=moldura, width=24)
d.line([(12, M - 12), (M - 12, 12)], fill=moldura, width=22)
d.rectangle([0, 0, M - 1, M - 1], outline=(70, 40, 18), width=3)
img.save("images/caixa_madeira.png")

print("Texturas geradas em images/")

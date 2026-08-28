# -*- coding: utf-8 -*-
"""Собирает self-contained версию сайта: все assets вшиваются как data: URI."""
import base64, re, os, sys

SRC = 'index.html'
OUT = 'dist/supermarkt-artifact.html'
MIME = {'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.mp4':'video/mp4','.svg':'image/svg+xml'}

s = open(SRC, encoding='utf-8').read()

# strip document scaffolding — артефакт добавляет свой
s = re.sub(r'^<!DOCTYPE html>\s*', '', s, flags=re.I)
s = re.sub(r'<html[^>]*>\s*', '', s, count=1, flags=re.I)
s = re.sub(r'</html>\s*$', '', s, flags=re.I)
s = re.sub(r'</?head[^>]*>\s*', '', s, flags=re.I)
s = re.sub(r'<body[^>]*>\s*', '', s, count=1, flags=re.I)
s = re.sub(r'</body>\s*', '', s, count=1, flags=re.I)
# favicon + og:image ссылаются на файлы — артефакту не нужны
s = re.sub(r'<link rel="icon"[^>]*>\s*', '', s)
s = re.sub(r'<meta property="og:image"[^>]*>\s*', '', s)
s = re.sub(r'<meta charset[^>]*>\s*', '', s, flags=re.I)
s = re.sub(r'<meta name="viewport"[^>]*>\s*', '', s, flags=re.I)
# имя страницы в галерее артефактов — без пояснения после тире
s = s.replace('<title>SUPERMARKT — немецкий в магазине</title>', '<title>Немецкий в магазине</title>')

used, missing, total = [], [], 0
def inline(m):
    global total
    attr, path = m.group(1), m.group(2)
    if path.startswith(('data:', 'http')):
        return m.group(0)
    if not os.path.exists(path):
        missing.append(path); return m.group(0)
    ext = os.path.splitext(path)[1].lower()
    raw = open(path, 'rb').read()
    total += len(raw)
    used.append((path, len(raw)))
    b64 = base64.b64encode(raw).decode()
    return f'{attr}="data:{MIME[ext]};base64,{b64}"'

s = re.sub(r'(src)="(assets/[^"]+)"', inline, s)

os.makedirs('dist', exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(s)

for p, n in used:
    print(f'  inlined {p:44s} {n/1024:8.1f} KB')
if missing:
    print('MISSING:', missing); sys.exit(1)
print(f'\nassets raw: {total/1024/1024:.2f} MB')
print(f'{OUT}: {os.path.getsize(OUT)/1024/1024:.2f} MB')

#!/usr/bin/env python3
"""Publica 10-19 desde academy_10_19_ligero.zip usando la API de GitHub.
Software libre: biblioteca estándar Python; sin dependencias de pago.
Requiere variable GITHUB_TOKEN con permiso Contents: write.
Uso: python3 scripts/publicar_10_19.py /ruta/academy_10_19_ligero.zip
"""
import base64
import json
import os
import sys
import urllib.request
import zipfile

REPO = "bohemio-ws/academy"
TOKEN = os.environ.get("GITHUB_TOKEN")
API = f"https://api.github.com/repos/{REPO}"

def api(method, path, data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        API + path, data=body, method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)

def main(path):
    if not TOKEN:
        raise SystemExit("Falta GITHUB_TOKEN (Contents: write)")
    with zipfile.ZipFile(path) as z:
        expected = [f"{i}.webp" for i in range(10, 20)]
        for name in expected:
            if name not in z.namelist():
                raise SystemExit(f"Falta {name}")
        ref = api("GET", "/git/ref/heads/main")
        parent = ref["object"]["sha"]
        base_tree = api("GET", f"/git/commits/{parent}")["tree"]["sha"]
        entries = []
        for name in expected:
            data = z.read(name)
            if not data.startswith(b"RIFF") or data[8:12] != b"WEBP":
                raise SystemExit(f"No es WebP: {name}")
            blob = api("POST", "/git/blobs", {
                "content": base64.b64encode(data).decode("ascii"),
                "encoding": "base64",
            })
            entries.append({"path": f"mnemonic-art/{name}",
                            "mode": "100644", "type": "blob", "sha": blob["sha"]})
            print(f"Preparado: {name} ({len(data)} bytes)")
        tree = api("POST", "/git/trees", {"base_tree": base_tree, "tree": entries})
        commit = api("POST", "/git/commits", {
            "message": "Publicar ilustraciones aprobadas 10-19 de Academy",
            "tree": tree["sha"], "parents": [parent],
        })
        api("PATCH", "/git/refs/heads/main", {"sha": commit["sha"], "force": False})
        print("PUBLICADO:", commit["sha"])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python3 scripts/publicar_10_19.py ARCHIVO.zip")
    main(sys.argv[1])

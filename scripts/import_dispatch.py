#!/usr/bin/env python3
"""Importacao segura do payload enviado pelo Power Automate/GitHub dispatch."""
import os, base64, pathlib, sys
from validate_radar import validate_and_normalize

PAYLOAD = os.getenv('RADAR_CSV_BASE64', '')
if not PAYLOAD or len(PAYLOAD) > 65535:
    print('Payload ausente ou excessivamente grande', file=sys.stderr)
    sys.exit(1)
try:
    decoded = base64.b64decode(PAYLOAD, validate=True)
    clean = validate_and_normalize(decoded)
except (ValueError, UnicodeError) as err:
    print('CSV recebido rejeitado: ' + str(err), file=sys.stderr)
    sys.exit(1)
p = pathlib.Path('files/radar.csv')
p.parent.mkdir(parents=True,exist_ok=True)
p.write_bytes(clean)
print(f'CSV recebido e validado: {len(clean)} bytes')

#!/usr/bin/env python3
"""Valida e normaliza o arquivo BYOR. Biblioteca padrão; nenhum pacote adicional."""
import csv, io, sys, pathlib
REQUIRED = ['name', 'ring', 'quadrant', 'isNew', 'description']
RINGS = {'adopt', 'trial', 'assess', 'caution'}
QUADRANTS = {'tools', 'platforms', 'techniques', 'languages & frameworks'}
MAX_CSV_BYTES = 48000  # Mantem compatibilidade com repository_dispatch (<64KB JSON)

def validate_and_normalize(data: bytes) -> bytes:
    if not data or len(data) > MAX_CSV_BYTES:
        raise ValueError('CSV vazio ou excedeu 48 KB; reavalie o transporte repository_dispatch')
    text = data.decode('utf-8-sig')
    parsed = csv.DictReader(io.StringIO(text, newline=''))
    if parsed.fieldnames != REQUIRED:
        raise ValueError(f'Cabecalhos esperados, exatamente nesta ordem: {REQUIRED}; recebido: {parsed.fieldnames}')
    seen, rows = set(), []
    for number, original in enumerate(parsed, start=2):
        if None in original:
            raise ValueError(f'Linha {number}: colunas adicionais inesperadas')
        row = {k: (original.get(k) or '').strip() for k in REQUIRED}
        row['ring'] = row['ring'].lower()
        if row['ring'] == 'hold':
            row['ring'] = 'caution'
        row['quadrant'] = row['quadrant'].lower()
        value = row['isNew'].lower()
        if value in {'true','1','yes','sim','verdadeiro'}:
            row['isNew'] = 'TRUE'
        elif value in {'false','0','no','não','nao','falso'}:
            row['isNew'] = 'FALSE'
        else:
            raise ValueError(f'Linha {number}: isNew invalido: {row["isNew"]}')
        if not row['name'] or not row['description']:
            raise ValueError(f'Linha {number}: nome ou descricao vazia')
        if row['ring'] not in RINGS or row['quadrant'] not in QUADRANTS:
            raise ValueError(f'Linha {number}: classificacao invalida: {row["ring"]} / {row["quadrant"]}')
        key = row['name'].casefold()
        if key in seen:
            raise ValueError(f'Linha {number}: nome duplicado: {row["name"]}')
        seen.add(key)
        rows.append(row)
    if len(rows) < 20:
        raise ValueError(f'Esperava pelo menos 20 tecnologias para evitar publicar dados incompletos; recebido {len(rows)}')
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=REQUIRED, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode('utf-8')

def main():
    path = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'files/radar.csv')
    clean = validate_and_normalize(path.read_bytes())
    print(f'VALIDADO: {path} | {len(list(csv.DictReader(io.StringIO(clean.decode()))))} tecnologias | {len(clean)} bytes')

if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError, csv.Error) as exc:
        print(f'ERRO: {exc}', file=sys.stderr)
        sys.exit(1)

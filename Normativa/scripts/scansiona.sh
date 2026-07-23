#!/usr/bin/env bash
# scansiona.sh — Passo B dell'avvio sessione: manifest dell'archivio + delta.
#
# Uso:  bash scripts/scansiona.sh <cartella-progetto>
#
# Produce  context/MANIFEST.tsv  (inventario meccanico: percorso, data, dimensione,
# estensione, cercabilita') e stampa a video SOLO il delta rispetto alla scansione
# precedente. Il manifest NON va letto in contesto: e' un file di lavoro, si
# interroga con grep. E' usa-e-getta: se cancellato si rigenera identico.
#
# Sola lettura sulla cartella normativa: qui non si scrive nulla.

set -uo pipefail

BASE="${1:-.}"
ARCH="$BASE/normativa"
CTX="$BASE/context"
MAN="$CTX/MANIFEST.tsv"

[ -d "$ARCH" ] || { echo "ERRORE: cartella archivio non trovata: $ARCH" >&2; exit 1; }
mkdir -p "$CTX"

# I temporanei stanno in /tmp: la cartella montata non consente la cancellazione.
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
NEW="$TMP/MANIFEST.new"

# --- Estensioni non cercabili come testo (immagini e binari vari) --------------
#     Restano a manifest (esistono) ma vanno ESCLUSE dal fan-out di ricerca.
NOTEXT='jpg|jpeg|gif|png|ico|zip|iso|exe|dll|mdb'

# --- Genera il manifest -------------------------------------------------------
find "$ARCH" -type f ! -name 'desktop.ini' -printf '%P\t%TY-%Tm-%Td\t%s\n' \
| awk -F'\t' -v notext="$NOTEXT" 'BEGIN{OFS="\t"}
    {
      n = split($1, p, "/"); f = p[n]
      ext = ""
      if (f ~ /\./) { m = split(f, q, "."); ext = tolower(q[m]) }
      cercabile = (ext ~ "^(" notext ")$") ? "no" : "si"
      print $1, $2, $3, ext, cercabile
    }' \
| sort -t$'\t' -k1,1 > "$NEW"

TOT=$(wc -l < "$NEW")
SRC=$(awk -F'\t' '$5=="si"' "$NEW" | wc -l)

# --- Primo avvio: nessun manifest precedente ----------------------------------
if [ ! -f "$MAN" ]; then
  cat "$NEW" > "$MAN"
  echo "MANIFEST CREATO (prima scansione) — nessun confronto disponibile."
  echo "File totali: $TOT | cercabili come testo: $SRC | non cercabili: $((TOT-SRC))"
  echo
  echo "Per settore:"
  awk -F'\t' '{split($1,p,"/"); c[p[1]]++} END{for (s in c) printf "  %-32s %4d\n", s, c[s]}' "$MAN" | sort
  exit 0
fi

# --- Delta: confronta percorso+data+dimensione --------------------------------
cut -f1-3 "$MAN" | sort -t$'\t' -k1,1 > "$TMP/old3"
cut -f1-3 "$NEW" | sort -t$'\t' -k1,1 > "$TMP/new3"

comm -13 "$TMP/old3" "$TMP/new3" | cut -f1 | sort -u > "$TMP/in_new"
comm -23 "$TMP/old3" "$TMP/new3" | cut -f1 | sort -u > "$TMP/in_old"

comm -23 "$TMP/in_new" "$TMP/in_old" > "$TMP/aggiunti"
comm -13 "$TMP/in_new" "$TMP/in_old" > "$TMP/rimossi"
comm -12 "$TMP/in_new" "$TMP/in_old" > "$TMP/modificati"

NA=$(wc -l < "$TMP/aggiunti"); NRM=$(wc -l < "$TMP/rimossi"); NM=$(wc -l < "$TMP/modificati")

echo "SCANSIONE ARCHIVIO — $(date +%Y-%m-%d)"
echo "File totali: $TOT (cercabili: $SRC | non cercabili: $((TOT-SRC)))"
echo "Delta: +$NA nuovi | -$NRM rimossi | ~$NM modificati"

if [ "$NA"  -gt 0 ]; then echo; echo "NUOVI:";      sed 's/^/  + /' "$TMP/aggiunti"; fi
if [ "$NRM" -gt 0 ]; then echo; echo "RIMOSSI:";    sed 's/^/  - /' "$TMP/rimossi"; fi
if [ "$NM"  -gt 0 ]; then echo; echo "MODIFICATI:"; sed 's/^/  ~ /' "$TMP/modificati"; fi
[ $((NA+NRM+NM)) -eq 0 ] && echo "Archivio invariato."

cat "$NEW" > "$MAN"
exit 0

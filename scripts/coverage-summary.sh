#!/usr/bin/env bash
#
# Recap couleur de la couverture de code (Jacoco) dans le terminal, classe par classe.
# Pensé pour la démo de conférence : lancer `./mvnw test` puis ce script pour voir
# immédiatement quelles classes ont besoin d'être mieux couvertes, sans ouvrir le HTML.
#
# Usage : ./scripts/coverage-summary.sh [seuil_orange] [seuil_vert]
#   seuil_orange (défaut 50) : en dessous -> rouge
#   seuil_vert   (défaut 80) : en dessous -> orange, au dessus -> vert

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CSV_FILE="${PROJECT_ROOT}/target/jacoco-report/jacoco.csv"

SEUIL_ROUGE="${1:-50}"
SEUIL_VERT="${2:-80}"

RED=$'\033[31m'
YELLOW=$'\033[33m'
GREEN=$'\033[32m'
BOLD=$'\033[1m'
RESET=$'\033[0m'

if [[ ! -f "${CSV_FILE}" ]]; then
    echo "Pas de rapport Jacoco trouvé (${CSV_FILE})." >&2
    echo "Lance d'abord : ./mvnw test" >&2
    exit 1
fi

echo ""
echo "${BOLD}Récap couverture de code — couverture-code${RESET}"
echo "Source : target/jacoco-report/jacoco.csv"
echo ""
printf "%-45s %10s %10s %8s\n" "CLASSE" "LIGNES %" "BRANCHES %" "STATUT"
printf '%s\n' "--------------------------------------------------------------------------------"

awk -F',' -v red="${RED}" -v yellow="${YELLOW}" -v green="${GREEN}" -v reset="${RESET}" \
    -v seuilRouge="${SEUIL_ROUGE}" -v seuilVert="${SEUIL_VERT}" '
    NR == 1 { next }
    {
        classe = $2 "." $3
        ligneManquee = $8; ligneCouverte = $9
        brancheManquee = $6; brancheCouverte = $7

        totalLignes = ligneManquee + ligneCouverte
        totalBranches = brancheManquee + brancheCouverte

        pctLignes = (totalLignes > 0) ? (ligneCouverte / totalLignes * 100) : 100
        pctBranches = (totalBranches > 0) ? (brancheCouverte / totalBranches * 100) : 100

        rows[NR] = classe
        pl[NR] = pctLignes
        pb[NR] = pctBranches
        n = NR
    }
    END {
        # tri a bulles simple par pourcentage de lignes croissant (peu de classes, suffisant)
        for (i = 2; i <= n; i++) {
            for (j = i; j > 2 && pl[j] < pl[j-1]; j--) {
                t = rows[j]; rows[j] = rows[j-1]; rows[j-1] = t
                t = pl[j]; pl[j] = pl[j-1]; pl[j-1] = t
                t = pb[j]; pb[j] = pb[j-1]; pb[j-1] = t
            }
        }

        for (i = 2; i <= n; i++) {
            color = red
            statut = "A COUVRIR"
            if (pl[i] >= seuilVert) { color = green; statut = "OK" }
            else if (pl[i] >= seuilRouge) { color = yellow; statut = "PARTIEL" }

            printf "%s%-45s %9.0f%% %9.0f%% %10s%s\n", color, rows[i], pl[i], pb[i], statut, reset
        }
    }
' "${CSV_FILE}"

echo ""
echo "Rapport HTML détaillé : target/jacoco-report/index.html"
echo ""

#!/usr/bin/env bash
#
# Recap couleur de la couverture de code (Jacoco) dans le terminal, classe par classe,
# scindé par type de test : JUnit (unitaire) vs Cucumber (intégration/BDD) vs global.
# Pensé pour la démo de conférence : lancer `./mvnw test` puis ce script pour voir
# immédiatement ce que chaque type de test couvre réellement — et ce qu'aucun des deux
# ne couvre.
#
# Usage : ./scripts/coverage-summary.sh [seuil_orange] [seuil_vert]
#   seuil_orange (défaut 50) : en dessous -> rouge
#   seuil_vert   (défaut 80) : en dessous -> orange, au dessus -> vert

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUARKUS_TARGET="${PROJECT_ROOT}/quarkus-app/target"
VIDOCQ_TARGET="${PROJECT_ROOT}/vidocq-app/target"

SEUIL_ROUGE="${1:-50}"
SEUIL_VERT="${2:-80}"

RED=$'\033[31m'
YELLOW=$'\033[33m'
GREEN=$'\033[32m'
BOLD=$'\033[1m'
CYAN=$'\033[36m'
RESET=$'\033[0m'

print_table() {
    local titre="$1"
    local csv="$2"

    echo ""
    echo "${BOLD}${CYAN}${titre}${RESET}"
    if [[ ! -f "${csv}" ]]; then
        echo "  (pas de rapport : ${csv})"
        return
    fi
    printf "  %-42s %10s %10s %8s\n" "CLASSE" "LIGNES %" "BRANCHES %" "STATUT"
    printf '%s\n' "  ------------------------------------------------------------------------------"

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

                printf "  %s%-42s %9.0f%% %9.0f%% %10s%s\n", color, rows[i], pl[i], pb[i], statut, reset
            }
        }
    ' "${csv}"
}

if [[ ! -f "${QUARKUS_TARGET}/jacoco-report/jacoco.csv" ]]; then
    echo "Pas de rapport Jacoco trouvé dans ${QUARKUS_TARGET}." >&2
    echo "Lance d'abord : ./mvnw test" >&2
    exit 1
fi

echo "${BOLD}Récap couverture de code — couverture-code${RESET}"
echo "quarkus-app : trois vues (JUnit seul, Cucumber seul, globale) — vidocq-app : une vue (JUnit)."

echo ""
echo "${BOLD}════ quarkus-app ════${RESET}"
print_table "JUNIT — tests unitaires" "${QUARKUS_TARGET}/jacoco-report-junit/jacoco.csv"
print_table "CUCUMBER — tests d'intégration (BDD)" "${QUARKUS_TARGET}/jacoco-report-cucumber/jacoco.csv"
print_table "GLOBAL — JUnit + Cucumber réunis" "${QUARKUS_TARGET}/jacoco-report/jacoco.csv"

echo ""
echo "${BOLD}════ vidocq-app ════${RESET}"
print_table "JUNIT — logique métier portée (phase 1, sans framework)" "${VIDOCQ_TARGET}/site/jacoco/jacoco.csv"

echo ""
echo "Rapports HTML détaillés :"
echo "  quarkus-app/target/jacoco-report-junit/index.html"
echo "  quarkus-app/target/jacoco-report-cucumber/index.html"
echo "  quarkus-app/target/jacoco-report/index.html"
echo "  vidocq-app/target/site/jacoco/index.html"
echo ""

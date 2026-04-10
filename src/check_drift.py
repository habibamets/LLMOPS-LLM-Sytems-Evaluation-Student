import os
import json
import sys

def check_drift(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} non trouvé.")
        sys.exit(1)

    with open(file_path, 'r') as f:
        data = json.load(f)

    metrics = data['metrics']
    failed = False
    
    # Paramètres de seuils (doivent matcher ceux de app.py ou être plus stricts)
    DRIFT_SHARE_THRESHOLD = 0.1 # On accepte max 10% de colonnes qui dérivent
    STAT_THRESHOLD = 0.1        # p-value en dessous de laquelle on considère qu'il y a drift

    print("\n" + "="*55)
    print("\033[95mCI QUALITY GATE - DRIFT MONITORING\033[0m")
    print("="*55)
    
    for m in metrics:
        metric_id = m.get('metric_id', '')

        # 1. Vérification globale du nombre de colonnes en dérive
        if metric_id.startswith("DriftedColumnsCount"):
            # share est le % de colonnes en drift (ex: 0.25 pour 1/4)
            share = m.get('value', {}).get('share', 0)
            count = m.get('value', {}).get('count', 0)
            
            if share > DRIFT_SHARE_THRESHOLD:
                print(f"\033[91m[DATASET] Dérive majeure : {share*100:.1f}% des colonnes ({int(count)}) dérivent !\033[0m")
                failed = True
            else:
                print(f"\033[92m[DATASET] Stabilité globale : {share*100:.1f}% de dérive.\033[0m")

        # 2. Focus spécifique sur le Sentiment (p-value)
        if metric_id.startswith("ValueDrift(column=Sentiment"):
            p_value = m.get('value', 1.0)
            if p_value < STAT_THRESHOLD:
                print(f"\033[91m[CONTENT] Dérive du Sentiment détectée (p={p_value:.4f})\033[0m")
                failed = True
            else:
                print(f"\033[92m[CONTENT] Sentiment stable (p={p_value:.4f})\033[0m")

        # 3. Focus spécifique sur les PII (Emails)
        if metric_id.startswith("ValueDrift(column=Email_PII"):
            p_value = m.get('value', 1.0)
            if p_value < STAT_THRESHOLD:
                print(f"\033[91m[SECURITY] Dérive des patterns PII/Emails détectée !\033[0m")
                failed = True
            else:
                print(f"\033[92m[SECURITY] Patterns PII stables.\033[0m")

    print("-" * 55)
    if failed:
        print("\033[91mALERTE : La dérive est trop élevée. Déploiement bloqué.\033[0m")
        sys.exit(1)
    else:
        print("\033[92mSTABILITÉ : Les données sont conformes à la référence.\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    check_drift("reports/chapter2_drift_report.json")
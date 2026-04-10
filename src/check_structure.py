import os
import json
import sys

def check_structure(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        sys.exit(1)

    with open(file_path, 'r') as f:
        data = json.load(f)

    metrics = data['metrics']
    failed = False
    
    print("\n" + "="*50)
    print("\033[96mCI QUALITY GATE - STRUCTURAL CONFORMITY\033[0m")
    print("="*50)
    
    for m in metrics:
        metric_id = m.get('metric_id')

        # Vérification de la validité JSON (Syntaxe)
        if metric_id == "MeanValue(column=Syntax_OK)":
            val = m.get('value', 0)
            if val < 0.9: # On veut au moins 90% de succès technique
                print(f"\033[91m[SYNTAX] Success rate: {val*100:.1f}% (Min 90%)\033[0m")
                failed = True
            else:
                print(f"\033[92m[SYNTAX] Success rate: {val*100:.1f}%\033[0m")

        # Vérification de la conformité au Schéma (Contrat)
        if metric_id == "MeanValue(column=Schema_Compliance)":
            val = m.get('value', 0)
            if val < 0.8: # Le schéma est plus difficile à obtenir
                print(f"\033[91m[SCHEMA] Compliance: {val*100:.1f}% (Min 80%)\033[0m")
                failed = True
            else:
                print(f"\033[92m[SCHEMA] Compliance: {val*100:.1f}%\033[0m")

        # Vérification de la propreté (Pas de bavardage au début)
        if metric_id == "MeanValue(column=Strict_Start_JSON)":
            val = m.get('value', 0)
            if val < 0.5: # Gemma3 270m est bavard
                print(f"\033[93m[FORMAT] Chatty model: {val*100:.1f}% strict JSON starts\033[0m")
            else:
                print(f"\033[92m[FORMAT] Prompt respected: {val*100:.1f}% strict starts\033[0m")

    print("-" * 50)
    if failed:
        print("\033[91mDEPLOYMENT REJECTED: TECHNICAL ERRORS DETECTED.\033[0m")
        sys.exit(1)
    else:
        print("\033[92mDEPLOYMENT CLEAN: STRUCTURE IS VALID.\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    check_structure("reports/chapter3_structural_report.json")
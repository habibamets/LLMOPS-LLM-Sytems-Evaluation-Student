import os

import requests
import pandas as pd

from evidently import Report, Dataset, DataDefinition
from evidently.descriptors import IsValidJSON, JSONSchemaMatch, RegExp
from evidently.presets import TextEvals


def call_gemma(text):
    url = os.getenv("OLLAMA_HOST", "http://localhost:11434") + "/api/generate"
    # Prompt incitant à l'extraction structurée
    prompt = f"Extract vendor and total amount from this text. Return ONLY JSON with keys 'vendor' (string) and 'total' (number). Text: {text}"
    
    payload = {
        "model": "gemma3:270m",
        "prompt": prompt,
        "stream": False,
        "format": "json" # Aide Ollama à structurer la sortie
    }
    try:
        response = requests.post(url, json=payload)
        return response.json().get("response", "")
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"

def run_evaluation():
    os.makedirs("reports", exist_ok=True)

    # 1. Dataset de test (Factures brutes)
    invoices = [
        "Invoice from CloudCorp, total 560.00 USD",
        "Dinner at Luigi's: 42.50 euros",
        "Subscription renewal - Netflix - 15.99$",
        "Broken text with no clear data" # Cas problématique
    ]

    # 2. Inférence locale
    print("Gemma 3 270M génère les extractions...")
    results = [call_gemma(inv) for inv in invoices]
    print(f"Extractions générées: {results}")
    df = pd.DataFrame({"raw_invoice": invoices, "prediction": results})

    # 3. Définition du Contrat (JSON Schema)
    schema = {
        "vendor": str,
        "total": float
    }

    # 4. Configuration Evidently
    data_definition = DataDefinition(text_columns=['prediction'])
    
    dataset = Dataset.from_pandas(
        df,
        data_definition=data_definition,
        descriptors=[
            # A. Validité Technique (Syntaxe)
            IsValidJSON("prediction", alias="Syntax_OK"),
            
            # B. Conformité du Schéma (Contrat d'interface)
            JSONSchemaMatch("prediction", expected_schema=schema, alias="Schema_Compliance"),
            
            # C. Qualité "Contrat Prompt" (Chattiness)
            # Vérifie si la réponse commence strictement par '{' (pas de "Here is...")
            RegExp("prediction", reg_exp=r"^\{", alias="Strict_Start_JSON"),
        ]
    )

    # 5. Création du rapport
    report = Report([
        TextEvals()
    ])

    print("Analyse structurelle en cours...")
    snapshot = report.run(reference_data=None, current_data=dataset)
    
    snapshot.save_html("reports/chapter3_structural_report.html")
    snapshot.save_json("reports/chapter3_structural_report.json")
    print("Évaluation terminée. Consultez les fichiers dans /reports.")

if __name__ == "__main__":
    run_evaluation()
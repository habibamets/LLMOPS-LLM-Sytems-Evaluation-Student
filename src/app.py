import os

import pandas as pd
from evidently import Report, Dataset, DataDefinition
from evidently.presets import TextEvals, DataDriftPreset
from evidently.descriptors import Sentiment, TextLength, RegExp

def run_drift_analysis():
    os.makedirs("reports", exist_ok=True)

    # 1. Reference Data (Semaine A : Stable et conforme)
    ref_df = pd.DataFrame({
        "user_query": [
            "How can I reset my password?",
            "Do you offer international shipping?",
            "I would like to upgrade my subscription.",
            "Tell me more about your privacy policy.",
            "My order hasn't arrived yet, can you check?",
            "I want to change my delivery address."
        ]
    })

    # 2. Current Data (Semaine B : Dérive et anomalies)
    current_df = pd.DataFrame({
        "user_query": [
            "Your service is terrible! I want a refund now!", # Sentiment Drift
            "Can you send the invoice to my email: john.doe@gmail.com?", # PII Leakage
            "I am very angry with the delay. Fix it!", # Sentiment Drift
            "Hola, ¿pueden ayudarme con mi pedido?", # Language Drift
            "I hate this bot, give me a human!", # Sentiment Drift
            "Contact me at support@scam.com" # PII Leakage
        ]
    })

    # 3. Définition des données et des descripteurs
    # On définit 'user_query' comme colonne textuelle.
    # On y attache des descripteurs qui deviendront des "colonnes virtuelles" pour le drift.
    data_definition = DataDefinition(text_columns=['user_query'])

    # Regex simple pour détecter la présence d'un email
    email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    
    ref_dataset = Dataset.from_pandas(
        ref_df, 
        data_definition=data_definition,
        descriptors=[
            Sentiment("user_query", alias="Sentiment"),
            TextLength("user_query", alias="Length"),
            RegExp("user_query", reg_exp=email_regex, alias="Email_PII")
        ]
    )

    current_dataset = Dataset.from_pandas(
        current_df, 
        data_definition=data_definition,
        descriptors=[
            Sentiment("user_query", alias="Sentiment"),
            TextLength("user_query", alias="Length"),
            RegExp("user_query", reg_exp=email_regex, alias="Email_PII")
        ]
    )

    # 4. Configuration du rapport
    # TextEvals : Analyse sémantique détaillée de la période actuelle
    # DataDriftPreset : Compare les distributions (Ref vs Current) de tous les descripteurs
    report = Report([
        TextEvals(),
        DataDriftPreset(
            text_method="perc_text_content_drift",
            text_threshold=0.1,
            drift_share=0.1,
            threshold=0.4
        )
    ])

    print("Analyse statistique de la dérive (Drift) en cours...")
    snapshot = report.run(reference_data=ref_dataset, current_data=current_dataset)

    # 5. Sauvegarde
    snapshot.save_html("reports/chapter2_drift_report.html")
    snapshot.save_json("reports/chapter2_drift_report.json")
    print("Évaluation terminée. Rapports générés dans le dossier /reports.")

if __name__ == "__main__":
    run_drift_analysis()
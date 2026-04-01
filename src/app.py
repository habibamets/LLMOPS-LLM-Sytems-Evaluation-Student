import os
import sys

import pandas as pd
from evidently import Report, Dataset, DataDefinition
from evidently.presets import TextEvals
from evidently.descriptors import TextLength, OOVWordsPercentage, Sentiment, RegExp

def run_evaluation():
    os.makedirs("reports", exist_ok=True)

    # Simulation de logs de production
    data = {
        "question": [
            "How can I cancel my order?",
            "Do you deliver to Canada?",
            "What is this terrible customer service?",
            "Thank you for your help!"
        ],
        "answer": [
            "You can cancel your order in the 'My orders' tab.",
            "Yes, we deliver to Canada within 5 to 7 business days.",
            "I am sorry for your experience. How can I help you?",
            "You're welcome! I am at your disposal."
        ]
    }
    df = pd.DataFrame(data)

    # On cible la colonne de réponse de l'IA
    dataset = Dataset.from_pandas(
        df,
        data_definition=DataDefinition(
            text_columns=['question', 'answer']),
        descriptors=[
            TextLength("answer", alias="Length"),
            OOVWordsPercentage("answer", alias="OOV"),
            Sentiment("answer", alias="Sentiment"),
            RegExp("answer", reg_exp=r"(?i)(cannot answer|I don't know)", alias="Refusal_Regex")
            ]
    )
    
    # Configuration du rapport avec longueur et preset sémantique
    report = Report([
        TextEvals()
    ])

    print("Exécution de l'analyse Evidently...")
    snapshot = report.run(reference_data=None, current_data=dataset)

    # Sauvegarde des deux formats (Audit vs Automatisation)
    snapshot.save_html("reports/chapter1_foundations_report.html")
    snapshot.save_json("reports/chapter1_foundations_report.json")
    print("Évaluation terminée. Rapports générés dans le dossier /reports.")

if __name__ == "__main__":
    run_evaluation()

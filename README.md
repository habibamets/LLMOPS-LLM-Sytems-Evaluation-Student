# Chapitre 2 : Profiling Avancé et Détection de Dérive (Data Drift) 📉⚠️

Ce chapitre se concentre sur l'analyse comparative des flux de données pour détecter les changements de comportement des utilisateurs et les risques de sécurité avant qu'ils ne dégradent les performances du LLM.

## 🎯 Intérêt de cette branche

L'objectif de la branche `chapter-2` est de mettre en place un monitoring de la **dérive (Drift)** :
1. **Analyse Comparative** : Comparer les données actuelles (**Current**) à une base de référence saine (**Reference**) pour identifier les changements statistiques.
2. **Détection d'Anomalies** : Identifier les dérives de sentiment (agressivité croissante), de longueur de prompt (complexité) ou de langue.
3. **Sécurité Déterministe** : Détecter les fuites de données personnelles (**PII**) comme les emails via des descripteurs RegExp.
4. **Stability Gate** : Automatiser la décision de blocage (CI/CD) si la dérive dépasse les seuils de tolérance.

---

## 🏗️ Architecture d'Analyse de Dérive

Le système utilise un conteneur unique (`evaluator`) qui :
*   Charge deux jeux de données simulés (Semaine A vs Semaine B).
*   Calcule des descripteurs sémantiques et statistiques (Sentiment, Longueur, Regex).
*   Produit un diagnostic de dérive statistique avec **Evidently AI**.

---

## 📁 Structure de l'Analyse

*   `src/app.py` : Script principal configurant le `DataDriftPreset` et les descripteurs.
*   `src/check_drift.py` : Le "Quality Gate" qui interprète les p-values et les rapports de dérive.
*   `reports/` : Contient le rapport détaillé de dérive.

---

> [!IMPORTANT]
> La dérive des entrées (**Input Drift**) est souvent un indicateur avancé d'un futur échec du modèle. Surveiller ce qui rentre permet d'anticiper les problèmes de qualité sur ce qui sort.

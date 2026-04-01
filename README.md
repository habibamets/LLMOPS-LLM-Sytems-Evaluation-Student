# Chapitre 7 : Monitoring Long-Terme et Dashboarding 📊

Ce chapitre marque la transition d'une approche de **Quality Gate** (validation ponctuelle en CI/CD) vers une **Observabilité Continue** de votre application RAG en production.

## 🎯 Intérêt de cette branche

L'objectif de la branche `chapter-7` est de mettre en place une infrastructure de monitoring capable de :
1. **Détecter les dérives (drift)** : Suivre l'évolution de la qualité sémantique (*Faithfulness*) au fil du temps.
2. **Surveiller la sécurité** : Visualiser les tentatives de fuites de données sensibles (*Secret Leaks*) et l'efficacité des Guardrails.
3. **Centraliser les rapports** : Passer de fichiers JSON/HTML statiques à un tableau de bord dynamique et persistant avec **Evidently UI**.

---

## 🏗️ Architecture du Monitoring

Le système repose sur quatre piliers :
*   **Evidently UI** : Un service centralisé (Docker) qui héberge les dashboards et stocke les snapshots de données.
*   **LiteLLM Proxy** : Utilisé comme passerelle pour interroger les juges LLM (Llama 3 via Groq) de manière sécurisée et optimisée.
*   **`dashboard_push.py`** : Script d'initialisation qui déclare la structure du dashboard (code-as-config) et génère un historique simulé.
*   **`monitor_rag.py`** : Script de production qui interroge réellement le RAG et pousse les métriques fraîches vers l'UI.

---

## 🚀 Lancement et Utilisation

Assurez-vous d'avoir votre fichier `.env` configuré avec vos clés d'API (Groq, etc.).

### 1. Démarrer la stack RAGOPS
Lancez les services de base (API, Vecteur DB, Proxy) :
```bash
make up
```

> [!TIP]
> En production, le script `monitor_rag.py` est destiné à être exécuté via une tâche planifiée (Cron job) toutes les heures ou tous les jours pour assurer une surveillance sans interruption.

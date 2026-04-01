# Chapitre 6 : Intégration Continue (CI/CD) et Tests E2E 🛡️

Ce chapitre se concentre sur l'automatisation de la qualité et de la sécurité via des pipelines de test robustes, garantissant qu'aucune régression (sémantique ou sécuritaire) n'atteigne la production.

## 🎯 Intérêt de cette branche

L'objectif de la branche `chapter-6` est de transformer nos scripts d'audit manuels en un **Quality Gate** automatique. 

Grâce à **Testcontainers**, nous créons un environnement éphémère identique à la production pour chaque exécution de test, permettant de valider :
1. **La Triade RAG** : Fidélité (*Faithfulness*), Pertinence du contexte (*Context Precision*) et du contenu (*Answer Relevance*).
2. **La Résilience Sécuritaire** : Red Teaming automatique pour détecter les fuites de secrets et les contournements de Guardrails.
3. **L'Intégrité de l'Architecture** : Vérification que tous les composants (Backend, Meilisearch, Proxy, TEI) collaborent correctement.

---

## 🏗️ Architecture des Tests (DooD)

Le système utilise le pattern **DooD (Docker-out-of-Docker)** :
*   Le conteneur de test (`ragops-tester`) accède au socket Docker de l'hôte (`/var/run/docker.sock`).
*   Il pilote la création et la destruction de la stack complète via **Docker Compose** directement depuis le code Python.
*   **Pytest** orchestre les scénarios de test et **Evidently AI** agit comme le juge (LLM-as-a-Judge) pour valider les réponses.

---

## 🚀 Lancement et Utilisation

Assurez-vous d'avoir votre fichier `.env` configuré avec vos clés d'API (Groq, etc.).

### 1. Préparer l'environnement
Construisez les images de base de l'application :
```bash
make build
```
---

## 📁 Structure des Tests

*   `tests/test_llm_e2e.py` : Le fichier maître contenant les fixtures Testcontainers et les scénarios Pytest.
*   `tests/golden_dataset.json` : Le référentiel de "vérité terrain" (Ground Truth) utilisé pour l'évaluation.
*   `tests/Dockerfile.test` : L'environnement isolé pour l'exécution des tests en CI.

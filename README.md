# Chapitre 3 : Évaluation Structurelle et Tests Déterministes 🏗️🔍

Ce chapitre traite de l'utilisation des LLMs en tant que composants logiciels fiables, en imposant une validation de structure (JSON, Schémas) pour garantir leur intégration dans des pipelines applicatifs.

## 🎯 Intérêt de cette branche

L'objectif de la branche `chapter-3` est de mettre en place une validation déterministe pour l'extraction d'entités :
1. **Validation de Syntaxe** : S'assurer que le LLM produit un JSON valide (`IsValidJSON`).
2. **Conformité au Schéma** : Vérifier que les clés attendues sont présentes et du bon type (`JSONSchemaMatch`).
3. **Robustesse Logicielle** : Tester un modèle léger (**Gemma 3 270M via Ollama**) sujet au "bavardage" pour apprendre à construire des filets de sécurité (parsing robuste, retries).

---

## 🏗️ Architecture d'Évaluation Structurelle

Le système repose sur deux services orchestrés par Docker Compose :
*   **Ollama** : Héberge le modèle local `gemma3:270m` sur le port `11434`.
*   **Evaluator** : Un conteneur Python qui interroge Ollama, extrait les données et génère des rapports de conformité avec **Evidently AI**.

---

## 🚀 Lancement et Utilisation

### 1. Démarrer l'environnement complet
Cette commande verrouille les dépendances, construit les images et lance l'extraction suivie de l'audit :
```bash
make run
```

**Ce que fait cette commande :**
1. Elle télécharge et lance Gemma 3 en local.
2. Elle simule l'extraction de données depuis des factures brutes.
3. Elle vérifie si la sortie est un JSON valide et si elle contient les champs `vendor` (string) et `total` (number).
4. Elle génère un rapport HTML et JSON dans le dossier `reports/`.
5. Elle exécute `check_structure.py` pour valider si le taux de succès technique est suffisant (ex: > 90%).

---

## 🛠️ Commandes utiles

| Commande | Action |
| :--- | :--- |
| `make run` | Construit et lance tout le cycle (Extraction + Audit) |
| `docker compose down` | Arrête et nettoie tous les services |
| `docker compose logs -f ollama` | Suit le chargement du modèle local |

---

## 📁 Structure de l'Évaluation

*   `src/app.py` : Logique d'extraction via Ollama et configuration des descripteurs de structure.
*   `src/check_structure.py` : Le "Quality Gate" technique qui valide les taux de succès syntaxiques et schématiques.
*   `reports/` : Contient le rapport `chapter3_structural_report.html` détaillant chaque échec de format.

---

> [!TIP]
> En production, privilégiez toujours une validation déterministe par code (Regex, Pydantic) pour la structure. Réservez l'évaluation par LLM uniquement pour le sens et la nuance sémantique.

---
*Basé sur le support de cours : [cours.md](./cours.md)*

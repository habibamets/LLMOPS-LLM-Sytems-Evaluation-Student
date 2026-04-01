# Chapitre 5 : Sécurité, Robustesse et Guardrails 🛡️🔒

Ce chapitre traite de la protection des systèmes LLM contre les attaques malveillantes et les fuites de données, en passant d'une simple évaluation de la qualité à une véritable stratégie de **Défense en Profondeur**.

## 🎯 Intérêt de cette branche

L'objectif de la branche `chapter-5` est d'apprendre à sécuriser une application RAG face aux menaces du monde réel :
1. **Red Teaming Automatisé** : Utiliser **Evidently AI** pour bombarder le système de prompts malveillants (Jailbreak, Injection) et mesurer son taux de succès/échec.
2. **Blocage Actif via Guardrails** : Implémenter **Nvidia NeMo Guardrails** pour intercepter les attaques avant qu'elles n'atteignent le LLM.
3. **Prévention des fuites (PII)** : S'assurer que le système ne divulgue pas d'informations sensibles (secrets, emails, tokens) présentes dans son contexte documentaire.

---

## 🏗️ Architecture de Sécurité (Défense en Profondeur)

Le système combine deux approches complémentaires :
*   **Audit Passif (Evidently AI)** : Agit comme un système d'alarme. Il évalue a posteriori (ou en CI/CD) si les défenses ont tenu bon.
*   **Défense Active (NeMo Guardrails)** : Agit comme un vigile. Il utilise le langage **Colang** pour définir des règles de conduite et bloque les requêtes suspectes en temps réel.

---

## 🚀 Lancement et Utilisation

Assurez-vous d'avoir votre fichier `.env` configuré avec vos clés d'API (Groq, etc.).

### 1. Démarrer la stack RAGOPS
Lancez les services de base (Backend avec NeMo intégré, Meilisearch, LiteLLM) :
```bash
make up
```

## 📁 Configuration de la Sécurité

*   `backend/app/nemo_config/` : Contient la "loi" du système (`rails.co`) et la configuration du modèle régulateur (`config.yaml`).
*   `src/red_teaming.py` : Le script qui définit les vecteurs d'attaque.
*   `src/check_security.py` : Le garde-fou final qui décide si le build doit échouer en cas de vulnérabilité.

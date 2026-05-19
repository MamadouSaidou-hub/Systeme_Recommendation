# EduReco API — Tests via CMD (curl Windows)

**Prérequis** : `python api.py` doit tourner dans un terminal séparé  
**Base URL** : `http://127.0.0.1:5001`

---

## 1. Health Check

```bash
curl http://127.0.0.1:5001/api/health
```

**Réponse attendue (200)**
```json
{"statut": "ok", "message": "API EduReco fonctionne !"}
```

---

## 2. Créer un utilisateur

### ✅ Cas nominal
```bash
curl -X POST http://127.0.0.1:5001/api/users -H "Content-Type: application/json" -d "{\"nom\":\"Bah\",\"prenom\":\"Imamsaid\",\"email\":\"imamsaidou@gmail.com\",\"pays\":\"Senegal\",\"niveau_etudes\":\"licence\",\"domaine\":\"informatique\",\"objectif\":\"devenir data scientist\",\"langue\":\"francais\"}"
```

**Réponse attendue (201)**
```json
{
  "succes": true,
  "message": "Bienvenue Mamadou !",
  "utilisateur": {
    "id": 1,
    "nom": "Diallo",
    "prenom": "Mamadou",
    "email": "mamadou@gmail.com",
    "pays": "Senegal",
    "niveau_etudes": "licence",
    "domaine": "informatique"
  }
}
```

---

### ❌ Email déjà utilisé (relancer la même commande)
```bash
curl -X POST http://127.0.0.1:5001/api/users -H "Content-Type: application/json" -d "{\"nom\":\"Diallo\",\"prenom\":\"Mamadou\",\"pays\":\"Senegal\",\"niveau_etudes\":\"licence\",\"domaine\":\"informatique\"}"
```

**Réponse attendue (409)**
```json
{"succes": false, "erreur": "Cet email est d\u00e9j\u00e0 utilis\u00e9"}
```

---

### ❌ Champ manquant (email absent)
```bash
curl -X POST http://127.0.0.1:5001/api/users -H "Content-Type: application/json" -d "{\"nom\":\"Diallo\",\"prenom\":\"Mamadou\",\"pays\":\"Senegal\",\"niveau_etudes\":\"licence\",\"domaine\":\"informatique\"}"
```

**Réponse attendue (400)**
```json
{"succes": false, "erreur": "Champ obligatoire manquant : 'email'"}
```

---

### ❌ Niveau invalide
```bash
curl -X POST http://127.0.0.1:5001/api/users -H "Content-Type: application/json" -d "{\"nom\":\"Diallo\",\"prenom\":\"Mamadou\",\"email\":\"test2@gmail.com\",\"pays\":\"Senegal\",\"niveau_etudes\":\"terminale\",\"domaine\":\"informatique\"}"
```

**Réponse attendue (400)**
```json
{"succes": false, "erreur": "Niveau invalide. Valeurs : ['lycee', 'bac', 'licence', 'master', 'doctorat']"}
```

---

### ❌ Domaine invalide
```bash
curl -X POST http://127.0.0.1:5001/api/users -H "Content-Type: application/json" -d "{\"nom\":\"Diallo\",\"prenom\":\"Mamadou\",\"email\":\"test3@gmail.com\",\"pays\":\"Senegal\",\"niveau_etudes\":\"licence\",\"domaine\":\"philosophie\"}"
```

**Réponse attendue (400)**
```json
{"succes": false, "erreur": "Domaine invalide. Valeurs : ['informatique', 'medecine', 'droit', 'economie', 'ingenierie', 'science', 'arts', 'education']"}
```

---

## 3. Connexion

### ✅ Email existant
```bash
curl -X POST http://127.0.0.1:5001/api/users/connexion -H "Content-Type: application/json" -d "{\"email\":\"mamadou@gmail.com\"}"
```

**Réponse attendue (200)**
```json
{
  "succes": true,
  "message": "Bienvenue Mamadou ",
  "utilisateur": { "id": 1, "prenom": "Mamadou", ... }
}
```

---

### ❌ Email inconnu
```bash
curl -X POST http://127.0.0.1:5001/api/users/connexion -H "Content-Type: application/json" -d "{\"email\":\"inconnu@gmail.com\"}"
```

**Réponse attendue (404)**
```json
{"succes": false, "erreur": "Email introuvable. Cr\u00e9ez d'abord votre profil."}
```

---

### ❌ Email vide
```bash
curl -X POST http://127.0.0.1:5001/api/users/connexion -H "Content-Type: application/json" -d "{\"email\":\"\"}"
```

**Réponse attendue (400)**
```json
{"succes": false, "erreur": "Email requis"}
```

---

## 4. Récupérer un profil par ID

### ✅ ID existant (remplace 1 par l'id retourné à la création)
```bash
curl http://127.0.0.1:5001/api/users/9
```

**Réponse attendue (200)**
```json
{
  "succes": true,
  "utilisateur": { "id": 1, "nom": "Diallo", "prenom": "Mamadou", ... }
}
```

---

### ❌ ID inexistant
```bash
curl http://127.0.0.1:5001/api/users/9999
```

**Réponse attendue (404)**
```json
{"succes": false, "erreur": "Utilisateur introuvable"}
```

---

## 5. Recommandations NLP

### ✅ Cas nominal (remplace 1 par l'id réel)
```bash
curl http://127.0.0.1:5001/api/recommendations/9
```

> ⚠️ Prend 3 à 5 secondes — le modèle NLP encode les textes

**Réponse attendue (200)**
```json
{
  "succes": true,
  "texte_profil": "Etudiant niveau licence en informatique au Senegal, objectif devenir data scientist, langue francais",
  "formations": [
    { "id": 3, "titre": "Data Science avec Python", "score": 0.8921, "pct": 89.2 },
    { "id": 7, "titre": "Machine Learning", "score": 0.8543, "pct": 85.4 }
  ],
  "bourses": [
    { "id": 2, "titre": "Bourse AFD", "score": 0.7812, "pct": 78.1 }
  ]
}
```

---

### ❌ Utilisateur inexistant
```bash
curl http://127.0.0.1:5001/api/recommendations/9999
```

**Réponse attendue (404)**
```json
{"succes": false, "erreur": "Utilisateur introuvable"}
```

---

## Ordre logique pour le cours

```bash
# Etape 1 — Vérifier que l'API tourne
curl http://127.0.0.1:5001/api/health

# Etape 2 — Créer un profil (noter l'id retourné)
curl -X POST http://127.0.0.1:5001/api/users -H "Content-Type: application/json" -d "{\"nom\":\"Diallo\",\"prenom\":\"Mamadou\",\"email\":\"mamadou@gmail.com\",\"pays\":\"Senegal\",\"niveau_etudes\":\"licence\",\"domaine\":\"informatique\",\"objectif\":\"devenir data scientist\",\"langue\":\"francais\"}"

# Etape 3 — Tester le doublon
curl -X POST http://127.0.0.1:5001/api/users -H "Content-Type: application/json" -d "{\"nom\":\"Diallo\",\"prenom\":\"Mamadou\",\"email\":\"mamadou@gmail.com\",\"pays\":\"Senegal\",\"niveau_etudes\":\"licence\",\"domaine\":\"informatique\"}"

# Etape 4 — Se connecter
curl -X POST http://127.0.0.1:5001/api/users/connexion -H "Content-Type: application/json" -d "{\"email\":\"mamadou@gmail.com\"}"

# Etape 5 — Récupérer le profil (remplace 1 par ton id)
curl http://127.0.0.1:5001/api/users/1

# Etape 6 — Générer les recommandations NLP (remplace 1 par ton id)
curl http://127.0.0.1:5001/api/recommendations/1
```

---

## Valeurs valides

| Champ | Valeurs acceptées |
|---|---|
| `niveau_etudes` | `lycee` `bac` `licence` `master` `doctorat` |
| `domaine` | `informatique` `medecine` `droit` `economie` `ingenierie` `science` `arts` `education` |

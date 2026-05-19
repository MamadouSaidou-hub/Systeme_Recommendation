# EduReco API — Guide de Tests Postman

**Base URL** : `http://127.0.0.1:5001`  
**Header requis (tous les POST)** : `Content-Type: application/json`

---

## 1. GET /api/health — Vérifier que l'API tourne

**Méthode** : `GET`  
**URL** : `http://127.0.0.1:5001/api/health`  
**Body** : aucun

**Réponse attendue (200)**
```json
{
  "statut": "ok",
  "message": "API EduReco fonctionne !"
}
```

---

## 2. POST /api/users — Créer un utilisateur

**Méthode** : `POST`  
**URL** : `http://127.0.0.1:5001/api/users`

### ✅ Cas nominal — création réussie

```json
{
  "nom": "Diallo",
  "prenom": "Mamadou",
  "email": "mamadou.diallo@gmail.com",
  "pays": "Sénégal",
  "niveau_etudes": "licence",
  "domaine": "informatique",
  "objectif": "devenir data scientist",
  "langue": "français"
}
```

**Réponse (201)**
```json
{
  "succes": true,
  "message": "Bienvenue Mamadou !",
  "utilisateur": {
    "id": 1,
    "nom": "Diallo",
    "prenom": "Mamadou",
    "email": "mamadou.diallo@gmail.com",
    "pays": "Sénégal",
    "niveau_etudes": "licence",
    "domaine": "informatique"
  }
}
```

---

### ❌ Cas erreur — champ manquant (ex: email absent)

```json
{
  "nom": "Diallo",
  "prenom": "Mamadou",
  "pays": "Sénégal",
  "niveau_etudes": "licence",
  "domaine": "informatique"
}
```

**Réponse (400)**
```json
{
  "succes": false,
  "erreur": "Champ obligatoire manquant : 'email'"
}
```

---

### ❌ Cas erreur — niveau_etudes invalide

```json
{
  "nom": "Diallo",
  "prenom": "Mamadou",
  "email": "mamadou2@gmail.com",
  "pays": "Sénégal",
  "niveau_etudes": "terminale",
  "domaine": "informatique"
}
```

**Réponse (400)**
```json
{
  "succes": false,
  "erreur": "Niveau invalide. Valeurs : ['lycee', 'bac', 'licence', 'master', 'doctorat']"
}
```

---

### ❌ Cas erreur — email déjà utilisé (relancer la même requête du cas nominal)

Renvoyer exactement le même body que le cas nominal.

**Réponse (409)**
```json
{
  "succes": false,
  "erreur": "Cet email est déjà utilisé"
}
```

---

## 3. POST /api/users/connexion — Connexion par email

**Méthode** : `POST`  
**URL** : `http://127.0.0.1:5001/api/users/connexion`

### ✅ Cas nominal — email existant

```json
{
  "email": "mamadou.diallo@gmail.com"
}
```

**Réponse (200)**
```json
{
  "succes": true,
  "message": "Bienvenue Mamadou ",
  "utilisateur": {
    "id": 1,
    "nom": "Diallo",
    "prenom": "Mamadou",
    "email": "mamadou.diallo@gmail.com",
    "pays": "Sénégal",
    "niveau_etudes": "licence",
    "domaine": "informatique"
  }
}
```

---

### ❌ Cas erreur — email introuvable

```json
{
  "email": "inconnu@gmail.com"
}
```

**Réponse (404)**
```json
{
  "succes": false,
  "erreur": "Email introuvable. Créez d'abord votre profil."
}
```

---

### ❌ Cas erreur — email vide

```json
{
  "email": ""
}
```

**Réponse (400)**
```json
{
  "succes": false,
  "erreur": "Email requis"
}
```

---

## 4. GET /api/users/{id} — Récupérer un profil par ID

**Méthode** : `GET`  
**URL** : `http://127.0.0.1:5001/api/users/1`  
**Body** : aucun

### ✅ Cas nominal — ID existant

**Réponse (200)**
```json
{
  "succes": true,
  "utilisateur": {
    "id": 1,
    "nom": "Diallo",
    "prenom": "Mamadou",
    "email": "mamadou.diallo@gmail.com",
    "pays": "Sénégal",
    "niveau_etudes": "licence",
    "domaine": "informatique"
  }
}
```

---

### ❌ Cas erreur — ID inexistant

**URL** : `http://127.0.0.1:5001/api/users/9999`

**Réponse (404)**
```json
{
  "succes": false,
  "erreur": "Utilisateur introuvable"
}
```

---

## 5. GET /api/recommendations/{id} — Générer les recommandations NLP

**Méthode** : `GET`  
**URL** : `http://127.0.0.1:5001/api/recommendations/1`  
**Body** : aucun

> ⚠️ Ce endpoint prend quelques secondes — le modèle NLP encode les textes à la volée.

### ✅ Cas nominal

**Réponse (200)**
```json
{
  "succes": true,
  "utilisateur": {
    "id": 1,
    "nom": "Diallo",
    "prenom": "Mamadou",
    "niveau_etudes": "licence",
    "domaine": "informatique"
  },
  "texte_profil": "Etudiant niveau licence en informatique au Sénégal, objectif devenir data scientist, langue français",
  "formations": [
    {
      "id": 3,
      "titre": "Data Science avec Python",
      "domaine": "informatique",
      "score": 0.8921,
      "pct": 89.2
    },
    {
      "id": 7,
      "titre": "Machine Learning Avancé",
      "domaine": "informatique",
      "score": 0.8543,
      "pct": 85.4
    }
  ],
  "bourses": [
    {
      "id": 2,
      "titre": "Bourse AFD Afrique",
      "organisme": "AFD",
      "score": 0.7812,
      "pct": 78.1
    }
  ]
}
```

---

### ❌ Cas erreur — utilisateur inexistant

**URL** : `http://127.0.0.1:5001/api/recommendations/9999`

**Réponse (404)**
```json
{
  "succes": false,
  "erreur": "Utilisateur introuvable"
}
```

---

## Ordre logique pour les tests en cours

1. `GET /api/health` → vérifier que Flask tourne
2. `POST /api/users` → créer le profil (noter l'`id` retourné)
3. `POST /api/users` → même body → vérifier l'erreur 409
4. `POST /api/users/connexion` → se connecter avec l'email
5. `GET /api/users/1` → récupérer le profil par ID
6. `GET /api/recommendations/1` → générer les recommandations NLP

---

## Valeurs valides pour référence

| Champ | Valeurs acceptées |
|---|---|
| `niveau_etudes` | `lycee`, `bac`, `licence`, `master`, `doctorat` |
| `domaine` | `informatique`, `medecine`, `droit`, `economie`, `ingenierie`, `science`, `arts`, `education` |

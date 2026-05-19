

# **************************************************************************************************

# ============================================================
# ============================================================
# api.py
# RÔLE : API REST Flask — point d'entrée du projet EduReco
# C'est ce fichier qui reçoit les requêtes HTTP du Dashboard
# et retourne des réponses JSON
# ============================================================

# --- IMPORTS ---
# Flask  : le framework web qui crée notre serveur
# request : pour lire les données envoyées par le client (body JSON, params URL)
# jsonify : pour transformer un dictionnaire Python en réponse JSON
from flask import Flask, request, jsonify

# os : pour lire les variables d'environnement (clés secrètes)
import os

# load_dotenv : charge les variables depuis le fichier .env
from dotenv import load_dotenv

# On importe TOUTES les fonctions de database.py
# Ce fichier est le seul qui parle à Supabase
from database import (
    get_formations,            # lire toutes les formations
    get_bourses,               # lire toutes les bourses
    get_user_par_email,        # chercher un user par email
    get_user_par_id,           # chercher un user par ID
    creer_user,                # insérer un nouveau user
    email_exist,              # vérifier si un email existe déjà
    sauvegarder_recommandations # sauvegarder les résultats NLP
)

# On importe la fonction de recommandation NLP depuis modele_nlp.py
# Note : le nom est en anglais (recommender) dans ce fichier
from modele_nlp import recommender

# --- CONFIGURATION ---
# Charger les variables du fichier .env (SUPABASE_URL, SUPABASE_KEY, SECRET_KEY...)
load_dotenv()

# Créer l'application Flask
# __name__ dit à Flask où se trouve notre application
app = Flask(__name__)

# Clé secrète pour sécuriser les sessions Flask
# os.getenv() lit la valeur depuis .env, sinon utilise la valeur par défaut
app.secret_key = os.getenv("SECRET_KEY", "edureco2-secret")

# --- LISTES DE VALEURS ACCEPTÉES ---
# Ces listes servent à valider les données envoyées par l'utilisateur
# Si la valeur n'est pas dans la liste → on rejette la requête (code 400)

NIVEAUX = ['lycee', 'bac', 'licence', 'master', 'doctorat']

DOMAINES = [
    'informatique', 'medecine', 'droit', 'economie',
    'ingenierie', 'sciences', 'arts', 'education'
]


# ─────────────────────────────────────────────────────────────
# ENDPOINT 1 : GET /api/health
# Vérifier que l'API tourne correctement
# Utile pour les tests et le monitoring
# ─────────────────────────────────────────────────────────────
@app.route('/api/health', methods=['GET'])
def health():
    # On retourne simplement un message de confirmation
    # Code 200 = OK, tout va bien
    return jsonify({'statut': 'ok', 'message': 'API EduReco fonctionne !'}), 200


# ─────────────────────────────────────────────────────────────
# ENDPOINT 2 : POST /api/users
# Créer un nouveau profil utilisateur
# Le client envoie un JSON avec : nom, prenom, email, pays,
# niveau_etudes, domaine
# ─────────────────────────────────────────────────────────────
@app.route('/api/users', methods=['POST'])
def creer_utilisateur():

    # Lire le corps de la requête HTTP (format JSON)
    # request.get_json() transforme le JSON reçu en dictionnaire Python
    donnees = request.get_json()

    # --- VALIDATION 1 : Champs obligatoires ---
    # On boucle sur la liste des champs requis
    # Si un champ est absent ou vide → on retourne une erreur 400 (Bad Request)
    for champ in ['nom', 'prenom', 'email', 'pays', 'niveau_etudes', 'domaine']:
        if not donnees.get(champ):
            return jsonify({
                'succes': False,
                'erreur': f"Champ obligatoire manquant : '{champ}'"
            }), 400  # 400 = Bad Request (le client a mal envoyé les données)

    # --- VALIDATION 2 : niveau_etudes doit être dans la liste NIVEAUX ---
    if donnees['niveau_etudes'] not in NIVEAUX:
        return jsonify({
            'succes': False,
            'erreur': f"Niveau invalide. Valeurs acceptées : {NIVEAUX}"
        }), 400

    # --- VALIDATION 3 : domaine doit être dans la liste DOMAINES ---
    if donnees['domaine'] not in DOMAINES:
        return jsonify({
            'succes': False,
            'erreur': f"Domaine invalide. Valeurs acceptées : {DOMAINES}"
        }), 400

    # --- VALIDATION 4 : Email unique (pas de doublon) ---
    # email_existe() interroge la base de données
    if email_existe(donnees['email']):
        return jsonify({
            'succes': False,
            'erreur': "Cet email est déjà utilisé"
        }), 409  # 409 = Conflict (ressource déjà existante)

    # Normaliser l'email : tout en minuscule et sans espaces
    # Ex: "  USER@Gmail.com  " → "user@gmail.com"
    donnees['email'] = donnees['email'].lower().strip()

    # --- CRÉATION EN BASE ---
    try:
        # creer_user() insère les données dans Supabase et retourne l'utilisateur créé
        user = creer_user(donnees)

        # Code 201 = Created (ressource créée avec succès)
        return jsonify({
            'succes':      True,
            'message':     f"Bienvenue {user['prenom']} !",
            'utilisateur': user
        }), 201

    except Exception as e:
        # Si une erreur imprévue survient côté serveur
        # Code 500 = Internal Server Error
        return jsonify({'succes': False, 'erreur': str(e)}), 500


# ─────────────────────────────────────────────────────────────
# ENDPOINT 3 : POST /api/users/connexion
# Connexion d'un utilisateur existant par email
# Pas de mot de passe ici (prototype) — juste l'email suffit
# ─────────────────────────────────────────────────────────────
@app.route('/api/users/connexion', methods=['POST'])
def connexion():

    # Lire les données envoyées par le client
    donnees = request.get_json()

    # Récupérer l'email et le normaliser (minuscule + sans espaces)
    email = donnees.get('email', '').lower().strip()

    # Vérifier que l'email n'est pas vide
    if not email:
        return jsonify({'succes': False, 'erreur': "Email requis"}), 400

    # Chercher l'utilisateur en base par son email
    user = get_user_par_email(email)

    # Si aucun utilisateur trouvé → erreur 404 (Not Found)
    if not user:
        return jsonify({
            'succes': False,
            'erreur': "Email introuvable. Créez d'abord votre profil."
        }), 404

    # Connexion réussie → retourner le profil complet
    return jsonify({
        'succes':      True,
        'message':     f"Bienvenue {user['prenom']} !",
        'utilisateur': user
    }), 200


# ─────────────────────────────────────────────────────────────
# ENDPOINT 4 : GET /api/users/<id>
# Récupérer le profil d'un utilisateur par son ID
# <int:user_id> : Flask extrait automatiquement l'ID de l'URL
# Ex: GET /api/users/3 → user_id = 3
# ─────────────────────────────────────────────────────────────
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):

    # Chercher l'utilisateur en base par son ID
    user = get_user_par_id(user_id)

    # Si non trouvé → 404
    if not user:
        return jsonify({'succes': False, 'erreur': "Utilisateur introuvable"}), 404

    # Retourner le profil trouvé
    return jsonify({'succes': True, 'utilisateur': user}), 200


# ─────────────────────────────────────────────────────────────
# ENDPOINT 5 : GET /api/recommandations/<user_id>
# Générer les recommandations personnalisées via NLP
# C'est l'endpoint le plus important du projet !
# Étapes : profil → NLP → score → sauvegarde → réponse
# ─────────────────────────────────────────────────────────────
@app.route('/api/recommandations/<int:user_id>', methods=['GET'])
def get_recommandations(user_id):

    # --- ÉTAPE 1 : Récupérer le profil de l'utilisateur ---
    user = get_user_par_id(user_id)
    if not user:
        return jsonify({'succes': False, 'erreur': "Utilisateur introuvable"}), 404

    # --- ÉTAPE 2 : Charger toutes les données depuis Supabase ---
    formations = get_formations()  # liste de toutes les formations
    bourses    = get_bourses()     # liste de toutes les bourses

    # --- ÉTAPE 3 : Générer les recommandations via le modèle NLP ---
    # recommender() encode le profil et les items en vecteurs,
    # calcule la similarité cosinus, et retourne les 5 meilleurs
    # nb=5 : on veut les 5 meilleures recommandations
    resultats = recommender(user, formations, bourses, nb=5)

    # --- ÉTAPE 4 : Préparer les données à sauvegarder en base ---
    # On construit une liste d'items (formations + bourses) avec leurs scores
    items = []

    # Pour chaque formation recommandée
    for f in resultats['formations']:
        items.append({
            'user_id':   user_id,
            'item_id':   f['id'],          # ID de la formation
            'type_item': 'formation',
            'score':     int(f['pct']),    # Score en pourcentage (ex: 87)
            'raisons':   f'Score NLP : {f["pct"]}%'
        })

    # Pour chaque bourse recommandée
    for b in resultats['bourses']:
        items.append({
            'user_id':   user_id,
            'item_id':   b['id'],          # ID de la bourse
            'type_item': 'bourse',
            'score':     int(b['pct']),
            'raisons':   f'Score NLP : {b["pct"]}%'
        })

    # --- ÉTAPE 5 : Sauvegarder en base (remplace les anciennes reco) ---
    sauvegarder_recommandations(user_id, items)

    # --- ÉTAPE 6 : Retourner la réponse complète au client ---
    return jsonify({
        'succes':       True,
        'utilisateur':  user,
        'formations':   resultats['formations'],
        'bourses':      resultats['bourses'],
        'texte_profil': resultats['texte_profil']  # texte utilisé par le NLP
    }), 200


# ─────────────────────────────────────────────────────────────
# DÉMARRAGE DU SERVEUR
# Ce bloc s'exécute uniquement si on lance ce fichier directement
# Ex: python api.py
# Il ne s'exécute PAS si le fichier est importé ailleurs
# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("API EduReco → http://127.0.0.1:5001")
    # debug=True : redémarre automatiquement si on modifie le code
    # port=5001  : écoute sur le port 5001
    app.run(debug=True, port=5001)
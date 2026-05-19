# api.py
from flask import Flask,request,jsonify,session
import os
from dotenv import load_dotenv
from database import (
    get_formations,get_bourses,
    get_user_par_email,get_client,get_user_par_id,
    creer_user,email_exist,sauvegarder_recommendations,modifier_user_db
    
)
from modele_nlp import recommender
load_dotenv()
app=Flask(__name__)
app.secret_key=os.getenv("SECRET_KEY","edureco2-secret")

# Valeurs acceptées
NIVEAUX=['lycee','bac','licence','master','doctorat']
DOMAINES=['informatique','medecine','droit','economie','ingenierie','science','arts','education'
]

# ─────────────────────────────────────────────
# GET /api/health
# Vérifier que l'API tourne
# ─────────────────────────────────────────────
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'statut': 'ok', 'message': 'API EduReco fonctionne !'}), 200


# ─────────────────────────────────────────────
# POST /api/users
# Créer un nouveau profil utilisateur
# ─────────────────────────────────────────────
@app.route('/api/users', methods=['POST'])
def creer_utilisateur():
    donnees = request.get_json()

    # Validation des champs obligatoires
    for champ in ['nom', 'prenom', 'email', 'pays',
                  'niveau_etudes', 'domaine']:
        if not donnees.get(champ):
            return jsonify({
                'succes': False,
                'erreur': f"Champ obligatoire manquant : '{champ}'"
            }), 400

    # Validation des valeurs
    if donnees['niveau_etudes'] not in NIVEAUX:
        return jsonify({
            'succes': False,
            'erreur': f"Niveau invalide. Valeurs : {NIVEAUX}"
        }), 400

    if donnees['domaine'] not in DOMAINES:
        return jsonify({
            'succes': False,
            'erreur': f"Domaine invalide. Valeurs : {DOMAINES}"
        }), 400

    # Vérifier doublon email
    if email_exist(donnees['email']):
    # if email_exis(['email']):
        return jsonify({
            'succes': False,
            'erreur': "Cet email est déjà utilisé"
        }), 409

    donnees['email'] = donnees['email'].lower().strip()

    try:
        user = creer_user(donnees)
        return jsonify({
            'succes':      True,
            'message':     f"Bienvenue {user['prenom']} !",
            'utilisateur': user
        }), 201
    except Exception as e:
        return jsonify({'succes': False, 'erreur': str(e)}), 500


# ------------------------------------------------------------------------------
# POST /api/users/connexion
# Connexion par email
# -----------------------------------------------------------------------------
@app.route('/api/users/connexion',methods=['POST'])
def connexion():
    # lire les donnes par client
    donnees=request.get_json()
    email=donnees.get('email','').lower().strip()
# verification si l'email n'est pas vide
    if not email:
        return jsonify({'succes': False,'erreur': "Email requis"}), 400
    # chercher le user en base c à d dans la bd supabase par email
    user = get_user_par_email(email)
    # Si aucun user trouvé erreur 404 (Not Found)
    if not user:
        return jsonify({
            'succes': False,
            'erreur': "Email introuvable. Créez d'abord votre profil."
        }), 404
    
    return jsonify({
        'succes': True,
        'message': f"Bienvenue {user['prenom']} ",
        'utilisateur': user
    }), 200


#--------------------------------------------------------------------------------------------
# Endpoint 4: GET /api/users/(id)
# Recuperer le profil d'un user par son id
# exemple GET /api/users/3 user_id=3
# -------------------------------------------------------------------------------------------
# @app.route('/api/users/int:user_id',methods=['GET'])
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # cherchons user par son id dans la bd supabase
    user=get_user_par_id(user_id)
    # Si non trouvé 404
    if not user:
        return jsonify({'succes': False,'erreur': "Utilisateur introuvable"}),404
    return jsonify({'succes': True, 'utilisateur': user}), 200


# L'ajout de l'endpoint for modification 
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def modifier_user(user_id):
    # verification de si le user existe dans la bd
    user = get_user_par_id(user_id)
    if not user:
        return jsonify({
            'succes': False,
            'erreur': "Utilisateur introuvable."
        }),404
    # Lire le corps json de la requete
    donnees = request.get_json()

    if 'niveau_etudes' in donnees and donnees['niveau_etudes'] not in NIVEAUX:
        return jsonify({
            'succes': False,
            'erreur': f" niveau invalide. Valeurs acceptées : {NIVEAUX}"
        }), 400
    if 'domaine' in donnees and donnees['domaine'] not in DOMAINES:
        return jsonify({
            'succes': False,
            'erreur' : f"Domaine invalide .Valeurs acceptées : {DOMAINES}"
        }), 400
    champs_autorises=[
        'nom', 'prenom', 'pays',
        'niveau_etudes','domaine',
        'objectif','langue'
    ]
    # On ne garde que les champs autorisés avec une valeur non nulle
    mise_a_jour ={
        cle: valeur
        for cle, valeur in donnees.items()
        if cle in champs_autorises and valeur is not None
    }
     
    if not mise_a_jour:
        return jsonify({
            'succes': False,
            'erreur': "Aucun champ valide à modifier."

        }), 400
    
    # Application des mises à jours dans la base de données
    try:
        user_modifie=modifier_user_db(user_id,mise_a_jour)
        return jsonify({
            'succes': True,
            'message': "profil mis à jour avec succès.",
            'utilisateur': user_modifie 
        }), 200
    except Exception as e:
        return jsonify({
            'succes': False,
            'erreur': str(e)
        }), 500



#--------------------------------------------------------------------------------------------
# Endpoint 5: GET /api/recommendations/<int:user_id>
# Generer les recommendations personalisées via nlp
# Etape: profil---nlp--score---sauvegarde---réponse
# exemple GET /api/recommendations/<int:user_id>
# -------------------------------------------------------------------------------------------
@app.route('/api/recommendations/<int:user_id>',methods=['GET'])
def get_recommendations(user_id):
    # ---Etape 1: On va recuperer le profil de user ------
    user=  get_user_par_id(user_id)
    if not user:
        return jsonify({'succes': False, 'erreur': "Utilisateur introuvable"}),404
    # ----Etape 2: Charger toutes les donnees depuis la bd supabase---------
    formations = get_formations()
    bourses = get_bourses()
    # ----Etape 3: Generer les recommendations via le modele nlp------
    resultats=recommender(user,formations,bourses,nb=5)
    items= []
    # Pour chaque formation recommendée
    for f in resultats['formations']:
        items.append({

            'user_id':  user_id,
            'item_id':  f['id'],
            'type_item':  'formation',
            'score':  int(f['pct']),
            'raisons':  f'Score NLP : {f["pct"]}%'
        })
# pour chaque bourse recommandée
    for f in resultats['bourses']:
            items.append({

                'user_id':  user_id,
                'item_id':  f['id'],
                'type_item':  'bourse',
                'score':  int(f['pct']),
                'raisons':  f'Score NLP : {f["pct"]}%'
            })
# ---etape 4  sauvegarder en base (remplace les anciennes recomm)-----------
    sauvegarder_recommendations(user_id,items)
    return jsonify({
        'succes': True,
        'utilisateur': user,
        'formations': resultats['formations'],
        'bourses':    resultats['bourses'],
        'texte_profil': resultats['texte_profil']
    })







# Démarrage du serveur
if __name__ == '__main__':
    print("API EduReco → http://127.0.0.1:5001")
    app.run(debug=True, port=5001)





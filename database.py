"""database.py
  
============================================================
RÔLE : Connexion à Supabase + fonctions de lecture/écriture


Ce fichier est le SEUL endroit qui parle à la base de données.
Tous les autres fichiers du projet importent depuis ici.


Structure :
  get_client()        → créer la connexion --okay
  get_formations()    → lire toutes les formations---okay
  get_bourses()       → lire toutes les bourses --okay
  get_user_par_email()→ trouver un utilisateur par email --okay
  get_user_par_id()   → trouver un utilisateur par ID --okay
  creer_user()        → créer un nouvel utilisateur --okay
  email_existe()      → vérifier si un email existe déjà --okay
============================================================"""

import os
from supabase import create_client
from dotenv import load_dotenv

# chargement des var depuis le file .env
load_dotenv()
# Connexion

def get_client():
    url=os.getenv("SUPABASE_URL")
    key=os.getenv("SUPABASE_KEY")
    # verification que les clés existent
    if not url or not key:
        raise Exception(
            "Clés supabase manquantes "
            "Verifiez votre file .env"
        )
    return create_client(url,key)


# Fonction formations
def get_formations():
    db = get_client()
    result=db.table('formations').select('*').execute()
    return result.data #.data = la liste des resultats

# Fonction Bourses
def get_bourses():
    db = get_client()
    result = db.table('bourses').select('*').execute()
    return result.data


# fonction Utilisateurs
def get_user_par_email(email):
    db = get_client()
    result = db.table('utilisateurs') \
                .select('*') \
                .eq('email',email.lower().strip()) \
                .execute()
    if result.data:
        return result.data[0]
    return None 

# fonction by user_id
def get_user_par_id(user_id):
     
    db = get_client()
    result = db.table('utilisateurs') \
                .select('*') \
                .eq('id',user_id) \
                .execute()
    return result.data[0] if result.data else None
     

def creer_user(donnees):
    db = get_client()
    # insert data in user table
    result = db.table('utilisateurs').insert(donnees).execute()
    return result.data[0]


def modifier_user_db(user_id: int,donnees: dict) ->dict:
 
 
    db=get_client()
    result = (
        db.table('utilisateurs')
        .update(donnees)
        .eq('id', user_id)
        .execute()
    )

    return result.data[0]


def email_exist(email):
    return get_user_par_email(email) is not None




def sauvegarder_recommendations(user_id, items):
    db = get_client()
    
    # Supprimer les anciennes recommendations de l'utilisateur
    db.table('recommendations') \
      .delete() \
      .eq('user_id', user_id) \
      .execute()
    
    # Insérer les nouvelles
    if items:
        db.table('recommendations').insert(items).execute()



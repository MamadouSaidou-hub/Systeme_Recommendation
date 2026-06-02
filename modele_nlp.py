

# # new code propre
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity

# print("Chargement du modele NLP...")
# MODELE = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
# print("Modele OK")


# def profil_en_texte(profil):
#     niveau   = profil.get('niveau_etudes', '')  #  avec 's'
#     domaine  = profil.get('domaine', '')
#     pays     = profil.get('pays', '')
#     objectif = profil.get('objectif', '')
#     langue   = profil.get('langue', 'français')

#     texte = (
#         f"Etudiant niveau {niveau} en {domaine} "
#         f"au {pays}, objectif {objectif}, "
#         f"langue {langue}"
#     )
#     return texte


# def formation_en_texte(formation):
#     titre       = formation.get('titre', '')
#     domaine     = formation.get('domaine', '')
#     niveau      = formation.get('niveau_requis', '')
#     pays        = formation.get('pays_disponible', 'international')
#     langue      = formation.get('langue', 'français')
#     gratuit     = 'gratuit' if formation.get('est_gratuit') else 'payante'
#     organisme   = formation.get('organisme', '')
#     description = formation.get('description', '')

#     texte = (
#         f"Formation {titre} en {domaine} "
#         f"niveau {niveau}, disponible {pays}, "
#         f"en {langue}, {gratuit}, "
#         f"proposée par {organisme}. {description}"
#     )
#     return texte


# def bourse_en_texte(bourse):
#     titre       = bourse.get('titre', '')
#     organisme   = bourse.get('organisme', '')
#     niveau      = bourse.get('niveau_requis', '')
#     pays        = bourse.get('pays_eligible', '')
#     domaine     = bourse.get('domaine', '')
#     montant     = bourse.get('montant', '')
#     description = bourse.get('description', '')  #  sans 's'

#     texte = (
#         f"Bourse '{titre}' offerte par {organisme}, "
#         f"niveau {niveau}, eligible {pays}, "
#         f"domaine {domaine}, montant {montant}, "
#         f"description: {description}"
#     )
#     return texte


# def recommender(profil, formations, bourses, nb=5):  #  anglais conservé
    
#     # Step 1 : Encode the profile
#     texte_profil   = profil_en_texte(profil)
#     vecteur_profil = MODELE.encode([texte_profil])

#     # Step 2 : Encode and score formations
#     formations_recommended = []
#     if formations:
#         textes_formations   = [formation_en_texte(f) for f in formations]
#         vecteurs_formations = MODELE.encode(textes_formations)
#         scores              = cosine_similarity(vecteur_profil, vecteurs_formations)[0]

#         for i, formation in enumerate(formations):
#             formations_recommended.append({
#                 **formation,
#                 'score': round(float(scores[i]), 4),
#                 'pct':   round(float(scores[i]) * 100, 1)
#             })

#         formations_recommended.sort(key=lambda x: x['score'], reverse=True)
#         formations_recommended = formations_recommended[:nb]

#     # Step 3 : Encode and score bourses
#     bourses_recommended = []
#     if bourses:
#         textes_bourses   = [bourse_en_texte(b) for b in bourses]
#         vecteurs_bourses = MODELE.encode(textes_bourses)
#         scores           = cosine_similarity(vecteur_profil, vecteurs_bourses)[0]

#         for i, bourse in enumerate(bourses):
#             bourses_recommended.append({
#                 **bourse,
#                 'score': round(float(scores[i]), 4),
#                 'pct':   round(float(scores[i]) * 100, 1)
#             })

#         bourses_recommended.sort(key=lambda x: x['score'], reverse=True)
#         bourses_recommended = bourses_recommended[:nb]  #  bonne variable

#     return {
#         'formations':   formations_recommended,
#         'bourses':      bourses_recommended,
#         'texte_profil': texte_profil
#     }









# model for deployment
# modele_nlp.py
# ============================================================
# RÔLE : Modèle NLP — similarité sémantique via sentence-transformers
#
# ⚠️  LAZY LOADING activé pour le déploiement HuggingFace
#     Le modèle n'est chargé qu'au premier appel de recommender()
#     → évite le crash mémoire au démarrage du serveur
# ============================================================

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ─────────────────────────────────────────────────────────
# LAZY LOADING — modèle chargé au premier appel uniquement
# ─────────────────────────────────────────────────────────
MODELE = None

def get_modele():
    global MODELE
    if MODELE is None:
        print("Chargement du modele NLP...")
        MODELE = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("Modele OK")
    return MODELE


# ─────────────────────────────────────────────────────────
# FONCTIONS DE CONVERSION EN TEXTE
# Chaque objet (profil, formation, bourse) est converti
# en une phrase naturelle pour l'encodage NLP
# ─────────────────────────────────────────────────────────

def profil_en_texte(profil):
    niveau   = profil.get('niveau_etudes', '')
    domaine  = profil.get('domaine', '')
    pays     = profil.get('pays', '')
    objectif = profil.get('objectif', '')
    langue   = profil.get('langue', 'français')

    texte = (
        f"Etudiant niveau {niveau} en {domaine} "
        f"au {pays}, objectif {objectif}, "
        f"langue {langue}"
    )
    return texte


def formation_en_texte(formation):
    titre       = formation.get('titre', '')
    domaine     = formation.get('domaine', '')
    niveau      = formation.get('niveau_requis', '')
    pays        = formation.get('pays_disponible', 'international')
    langue      = formation.get('langue', 'français')
    gratuit     = 'gratuit' if formation.get('est_gratuit') else 'payante'
    organisme   = formation.get('organisme', '')
    description = formation.get('description', '')

    texte = (
        f"Formation {titre} en {domaine} "
        f"niveau {niveau}, disponible {pays}, "
        f"en {langue}, {gratuit}, "
        f"proposée par {organisme}. {description}"
    )
    return texte


def bourse_en_texte(bourse):
    titre       = bourse.get('titre', '')
    organisme   = bourse.get('organisme', '')
    niveau      = bourse.get('niveau_requis', '')
    pays        = bourse.get('pays_eligible', '')
    domaine     = bourse.get('domaine', '')
    montant     = bourse.get('montant', '')
    description = bourse.get('description', '')

    texte = (
        f"Bourse '{titre}' offerte par {organisme}, "
        f"niveau {niveau}, eligible {pays}, "
        f"domaine {domaine}, montant {montant}, "
        f"description: {description}"
    )
    return texte


# ─────────────────────────────────────────────────────────
# FONCTION PRINCIPALE — recommender
# ─────────────────────────────────────────────────────────

def recommender(profil, formations, bourses, nb=5):

    # Charger le modèle (lazy — uniquement au premier appel)
    modele = get_modele()

    # Step 1 : Encode the profile
    texte_profil   = profil_en_texte(profil)
    vecteur_profil = modele.encode([texte_profil])

    # Step 2 : Encode and score formations
    formations_recommended = []
    if formations:
        textes_formations   = [formation_en_texte(f) for f in formations]
        vecteurs_formations = modele.encode(textes_formations)
        scores              = cosine_similarity(vecteur_profil, vecteurs_formations)[0]

        for i, formation in enumerate(formations):
            formations_recommended.append({
                **formation,
                'score': round(float(scores[i]), 4),
                'pct':   round(float(scores[i]) * 100, 1)
            })

        formations_recommended.sort(key=lambda x: x['score'], reverse=True)
        formations_recommended = formations_recommended[:nb]

    # Step 3 : Encode and score bourses
    bourses_recommended = []
    if bourses:
        textes_bourses   = [bourse_en_texte(b) for b in bourses]
        vecteurs_bourses = modele.encode(textes_bourses)
        scores           = cosine_similarity(vecteur_profil, vecteurs_bourses)[0]

        for i, bourse in enumerate(bourses):
            bourses_recommended.append({
                **bourse,
                'score': round(float(scores[i]), 4),
                'pct':   round(float(scores[i]) * 100, 1)
            })

        bourses_recommended.sort(key=lambda x: x['score'], reverse=True)
        bourses_recommended = bourses_recommended[:nb]

    return {
        'formations':   formations_recommended,
        'bourses':      bourses_recommended,
        'texte_profil': texte_profil
    }
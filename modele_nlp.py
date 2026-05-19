
# # code update
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity

# print("chargement du modele nlp....")
# MODELE = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
# print("modele okay")

# def profil_en_texte(profil):
#     niveau = profil.get('niveau_etude', '')
#     domaine = profil.get('domaine', '')
#     pays = profil.get('pays', '')
#     # CORRECTION : La clé était 'pays', corrigée en 'objectif' pour correspondre au besoin
#     objectif = profil.get('objectif', '') 
#     langue = profil.get('langue', 'français')
#     texte = (
#         f"Etudiant niveau {niveau} en {domaine} "
#         f"au {pays}, objectif {objectif}, "
#         f"langue {langue}"
#     )
#     return texte

# def formation_en_texte(formation):
#     titre = formation.get('titre', '')
#     domaine = formation.get('domaine', '')
#     niveau = formation.get('niveau_requis', '')
#     pays = formation.get('pays_disponible', 'international')
#     langue = formation.get('langue', 'français')
#     gratuit = 'gratuit' if formation.get('est_gratuit') else 'payante'
#     organisme = formation.get('organisme', '')
#     description = formation.get('description', '')

#     texte = (
#         f"Formation {titre} en {domaine} "
#         f"niveau {niveau}, disponible {pays}, "
#         f"en {langue}, {gratuit}, "
#         f"proposée par {organisme}. {description}"
#     )
#     return texte

# def bourse_en_texte(bourse):
#     titre = bourse.get('titre', '')
#     organisme = bourse.get('organisme', '')
#     # CORRECTION : Ajout de la virgule manquante ici
#     niveau = bourse.get('niveau_requis', '') 
#     pays = bourse.get('pays_eligible', '')
#     domaine = bourse.get('domaine', '')
#     montant = bourse.get('montant', '')
#     description = bourse.get('descriptions', '')
    
#     # CORRECTION : Ajout de {description} pour afficher la variable, sinon on affichais juste le texte "description"
#     texte = (
#         f"Bourse '{titre}' offerte par {organisme}, "
#         f"niveau {niveau}, eligible {pays}, "
#         f"domaine {domaine}, montant {montant}, "
#         f"description: {description}"
#     )
#     return texte

# def recommender(profil, formations, bourses, nb=5):
#     # Etape 1: encodage du profil
#     texte_profil = profil_en_texte(profil)
#     vecteur_profil = MODELE.encode([texte_profil])
    
#     # Etape 2 : Encoder les formations
#     formations_recommendees = []

#     if formations:
#         textes_formations = [formation_en_texte(f) for f in formations]
#         vecteurs_formations = MODELE.encode(textes_formations)

#         # Calculer la similarité cosinus
#         scores = cosine_similarity(vecteur_profil, vecteurs_formations)[0]

#         # Associer chaque formation à son score
#         for i, formation in enumerate(formations):
#             formations_recommendees.append({
#                 **formation,
#                 'score': round(float(scores[i]), 4),
#                 # CORRECTION : float est une fonction, pas une liste. Correction de la syntaxe.
#                 'pct': round(float(scores[i]) * 100, 1) 
#             })
        
#         # Trier par ordre decroissant
#         formations_recommendees.sort(key=lambda x: x['score'], reverse=True)
#         formations_recommendees = formations_recommendees[:nb]

#     # Etape 3: encodage des bourses
#     bourses_recommendees = []
#     if bourses:
#         textes_bourses = [bourse_en_texte(b) for b in bourses]
#         vecteurs_bourses = MODELE.encode(textes_bourses)
        
#         # Calculer la similarité cosinus
#         scores = cosine_similarity(vecteur_profil, vecteurs_bourses)[0]
        
#         for i, bourse in enumerate(bourses):
#             bourses_recommendees.append({
#                 **bourse,
#                 'score': round(float(scores[i]), 4),
#                 # CORRECTION : Syntax corrigée ici aussi
#                 'pct': round(float(scores[i]) * 100, 1)
#             })
        
#         bourses_recommendees.sort(key=lambda x: x['score'], reverse=True)
#         # CORRECTION : on assignais 'formations_recommendees' au lieu de 'bourses_recommendees' ici
#         bourses_recommendees = bourses_recommendees[:nb] 

#     return {
#         'formations': formations_recommendees,
#         'bourses': bourses_recommendees,
#         'texte_profil': texte_profil
#     }



# new code propre
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

print("Chargement du modele NLP...")
MODELE = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("Modele OK")


def profil_en_texte(profil):
    niveau   = profil.get('niveau_etudes', '')  #  avec 's'
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
    description = bourse.get('description', '')  #  sans 's'

    texte = (
        f"Bourse '{titre}' offerte par {organisme}, "
        f"niveau {niveau}, eligible {pays}, "
        f"domaine {domaine}, montant {montant}, "
        f"description: {description}"
    )
    return texte


def recommender(profil, formations, bourses, nb=5):  #  anglais conservé
    
    # Step 1 : Encode the profile
    texte_profil   = profil_en_texte(profil)
    vecteur_profil = MODELE.encode([texte_profil])

    # Step 2 : Encode and score formations
    formations_recommended = []
    if formations:
        textes_formations   = [formation_en_texte(f) for f in formations]
        vecteurs_formations = MODELE.encode(textes_formations)
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
        vecteurs_bourses = MODELE.encode(textes_bourses)
        scores           = cosine_similarity(vecteur_profil, vecteurs_bourses)[0]

        for i, bourse in enumerate(bourses):
            bourses_recommended.append({
                **bourse,
                'score': round(float(scores[i]), 4),
                'pct':   round(float(scores[i]) * 100, 1)
            })

        bourses_recommended.sort(key=lambda x: x['score'], reverse=True)
        bourses_recommended = bourses_recommended[:nb]  #  bonne variable

    return {
        'formations':   formations_recommended,
        'bourses':      bourses_recommended,
        'texte_profil': texte_profil
    }
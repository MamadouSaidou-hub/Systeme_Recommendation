Creation de la base de données
Pour la bd on va user supabase 
Les tables qu'on a besoin:

Utilisateurs
Formations
Bourses
Recommendations

Creation des tables
 CREATE TABLE utilisateurs(
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    age INTEGER,
    pays VARCHAR(100) NOT NULL,
    niveau_etudes VARCHAR(50) NOT NULL,
    domaine VARCHAR(100) NOT NULL,
    objectif VARCHAR(100),
    langue VARCHAR(50) DEFAULT 'français',
    created_at TIMESTAMP DEFAULT NOW()
 );


--Table formations

CREATE TABLE formations(
    id SERIAL PRIMARY KEY,
    titre VARCHAR(300) NOT NULL,
    descriptions TEXT,
    domaine VARCHAR(100) NOT NULL,
    niveau_requis VARCHAR(50) NOT NULL,
    pays_disponible VARCHAR(100)  DEFAULT 'international',
    langue VARCHAR(50) DEFAULT 'français',
    duree VARCHAR(100),
    est_gratuit BOOLEAN  DEFAULT FALSE,
    lien VARCHAR(500),
    organisme VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW()
);

--Table bourses
CREATE TABLE bourses(
    id SERIAL PRIMARY KEY,
    titre VARCHAR(300) NOT NULL,
    descriptions TEXT,
    organisme VARCHAR(200) NOT NULL,
    pays_eligible VARCHAR(200) DEFAULT 'tous',
    niveau_requis VARCHAR(50) NOT NULL,
    domaine VARCHAR(100) NOT NULL,
    montant VARCHAR(200),
    date_limite DATE,
    type_bourse VARCHAR(100),
    lien VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);
--table recommendations

 CREATE TABLE recommendations(
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES utilisateurs(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL,
    type_item VARCHAR(20) NOT NULL,
    score INTEGER NOT NULL,
    raisons TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
python -m venv env enter 




<!-- Insertion data -->
## insertion data
INSERT INTO formations
    (titre, descriptions, domaine,niveau_requis,pays_disponible,langue,duree,est_gratuit,lien,organisme)
   
VALUES
--formation 1
('Introduction à python et Data Science',
'Apprenez les bases de python et de l'analyse de données avec des projets concret.
Idéal pour debuter en data science',
'Informatique','lycee',
'internationnal','français','8 semaines', TRUE,
'htpps://www.coursera.org', 'Coursera / IBM'
)

--bourse 1
INSERT INTO bourses
(
    titre, descriptions, organisme,pays_eligible,niveau_requis,domaine,montant,type_bourse,lien
)
VALUES
('Bourse Excellence AFD-Master en France',
'Financement complet pour etudier en France.
Couvre frais de scolarité,billet avion et vie.'
'Agence Française de Developpement',
'tous',
'licence',
'informatique',
'Frais de scolarité + 850 euro/mois',
'excellence',
'https://www.afd.fr'
),
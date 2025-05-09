ENUM_ROLE = "CREATE TYPE IF NOT EXISTS ROLE AS ENUM ('ADMINISTRATEUR','UTILISATEUR')"

ENUM_STATUS = """
    CREATE TYPE IF NOT EXISTS STATUT AS ENUM (
        'EN ATTENTE',
        'ACTIVE',
        'RAPPEL',
        'A REVOIR',
        'A SUPPRIMER'
    )
"""

table_groupes = """
    CREATE TABLE IF NOT EXISTS GROUPES(
        id_groupe SERIAL,
        nom_groupe VARCHAR(100) UNIQUE,
        CONSTRAINT pk_groupes PRIMARY KEY(id_groupe)
    )
"""


table_utilisateur = """ 
CREATE TABLE IF NOT EXISTS UTILISATEURS(
    id_utilisateur SERIAL,
    nom VARCHAR(50),
    prenom VARCHAR(100),
    email VARCHAR(70) UNIQUE,
    password VARCHAR(20),
    nom_role ROLE,
    id_groupe INT,
    CONSTRAINT pk_utilisateurs PRIMARY KEY(id_utilisateur),
    CONSTRAINT fk_groupes_utilisateurs FOREIGN KEY(id_groupe) REFERENCES GROUPES(id_groupe)
)
"""

table_prompt = """
    CREATE TABLE IF NOT EXISTS  PROMPTS(
        id_prompt SERIAL,
        libelle TEXT,
        status  STATUT,
        prix DOUBLE PRECISION DEFAULT 1000,
        date_creation DATE,
        id_utilisateur INT,
        CONSTRAINT pk_prompts PRIMARY KEY(id_prompt),
        CONSTRAINT fk_utilisateurs_prompts FOREIGN KEY(id_utilisateur) REFERENCES UTILISATEURS(id_utilisateur)
    )
"""


table_notation = """
    CREATE TABLE IF NOT EXISTS NOTATION(
        id_utilisateur INT,
        id_prompt INT,
        note INT,
        date_note DATE,
        CONSTRAINT fk_utilisateurs_notation FOREIGN KEY(id_utilisateur)  REFERENCES UTILISATEURS (id_utilisateur),
        CONSTRAINT fk_prompts_notation FOREIGN KEY (id_prompt)  REFERENCES PROMPTS (id_prompt),
        CONSTRAINT pk_notation PRIMARY KEY(id_utilisateur,id_prompt)
    )

"""

table_voter = """
    CREATE TABLE IF NOT EXISTS VOTER(
        id_utilisateur INT,
        id_prompt INT,
        vote INT,
        date_vote DATE,
        CONSTRAINT fk_utilisateurs_notation_voter FOREIGN KEY (id_utilisateur)  REFERENCES UTILISATEURS (id_utilisateur),
        CONSTRAINT fk_prompts_notation_voter FOREIGN KEY (id_prompt)  REFERENCES PROMPTS (id_prompt),
        CONSTRAINT pk_voter PRIMARY KEY(id_utilisateur,id_prompt)
    )
"""

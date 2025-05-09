from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from ..config import DATABASE_INFO
from .sript import ENUM_ROLE, ENUM_STATUS, table_groupes, table_utilisateur, table_prompt, table_notation, table_voter

def init_database():
    """Initialise la structure de la base de données."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                # Exécution des scripts dans une transaction
                cursor.execute(ENUM_ROLE)
                cursor.execute(ENUM_STATUS)
                cursor.execute(table_groupes)
                cursor.execute(table_utilisateur)
                cursor.execute(table_prompt)
                cursor.execute(table_notation)
                cursor.execute(table_voter)
                
                # Validation explicite des modifications
                conn.commit()
                print("Base de données initialisée avec succès.")
            except Exception as e:
                conn.rollback()
                print(f"Erreur lors de l'initialisation de la base de données: {e}")
                raise


# @contextmanager
def get_connection():
    """Gestionnaire de contexte pour obtenir une connexion à la base de données."""
    conn = None
    try:
        conn = connect(**DATABASE_INFO)
        return conn
    finally:
        print("terminee")
        # if conn is not None:
        #     conn.close()



# @contextmanager
def get_cursor(commit=False):
    """
    Gestionnaire de contexte pour obtenir un curseur de base de données.
    Si commit=True, la transaction est validée à la fin du bloc.
    """
    with get_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            return cursor
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.commit()
            # cursor.close()


def get_database():
    """Pour compatibilité avec le code existant."""
    with get_cursor(commit=True) as cursor:
        return cursor





















# from psycopg2 import connect
# from psycopg2.extras import RealDictCursor
# from ..config import DATABASE_INFO
# from .sript import ENUM_ROLE,ENUM_STATUS,table_groupes,table_notation,table_prompt,table_utilisateur,table_voter

# connexion = connect(
#     **DATABASE_INFO
# )

# cursor = connexion.cursor()

# cursor.execute(ENUM_ROLE)
# cursor.execute(ENUM_STATUS)
# cursor.execute(table_groupes)
# cursor.execute(table_utilisateur)
# cursor.execute(table_prompt)
# cursor.execute(table_notation)
# cursor.execute(table_voter)
# def get_database():
#     try:
#         yield cursor
#     except Exception as e:
#         print(e)
#     finally:
#         connexion.commit()
#         connexion.close()
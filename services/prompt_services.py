from ..databases.connexion import get_cursor
from datetime import datetime,timedelta


def create_prompt(id_utilisateur,data):
    cursor = None
    try:
        if not data or "libelle" not in data:
            return {"message": "Le libellé du prompt est requis"}, 400
            
        libelle = data.get("libelle")
        status = "EN ATTENTE"
        prix = 1000
        
        requete = "INSERT INTO PROMPTS (libelle, status, prix, id_utilisateur) VALUES (%s, %s, %s, %s) RETURNING *"
        cursor = get_cursor()
        cursor.execute(requete, (libelle, status, prix, id_utilisateur))
        prompt = cursor.fetchone()
        cursor.connection.commit()
        cursor.close()
        return prompt,200
    except Exception as e:
        if cursor:
            cursor.connection.rollback()
            cursor.close()
        return {"erreur": str(e)}, 500


def update_prompt(current_user,id,data):

    cursor = None
    try:        
        cursor = get_cursor()
        # Vérification du prompt
        requete_check = "SELECT * FROM PROMPTS WHERE id_prompt=%s"
        cursor.execute(requete_check, (id,))
        prompt = cursor.fetchone()
        
        if not prompt:
            cursor.close()
            return {"message": "Prompt non trouvé"}, 404
            
        # Si utilisateur normal, vérifier qu'il est propriétaire du prompt
        if current_user.get("nom_role") == "UTILISATEUR" and prompt.get("id_utilisateur") != current_user.get("id_utilisateur"):
            cursor.close()
            return {"message": "Vous ne pouvez modifier que vos propres prompts"}, 403
            
        if not data:
            cursor.close()
            return {"message": "Aucune donnée fournie pour la mise à jour"}, 400
            
        # Construction de la requête de mise à jour
        update_fields = []
        params = []
        
        if "libelle" in data:
            update_fields.append("libelle=%s")
            params.append(data.get("libelle"))
            
        if "status" in data:
            # Restriction: seul admin peut changer le statut
            if current_user.get("nom_role") != "ADMINISTRATEUR" and data.get("status") != prompt.get("status"):
                cursor.close()
                return {"message": "Seul un administrateur peut modifier le statut"}, 403
            update_fields.append("status=%s")
            params.append(data.get("status"))
            
        if "prix" in data:
            # Restriction: seul admin peut changer le prix
            if current_user.get("nom_role") != "ADMINISTRATEUR" and data.get("prix") != prompt.get("prix"):
                cursor.close()
                return {"message": "Seul un administrateur peut modifier le prix"}, 403
            update_fields.append("prix=%s")
            params.append(data.get("prix"))
        if not update_fields:
            cursor.close()
            return {"message": "Aucun champ valide à mettre à jour"}, 400
        update_fields.append("date_modification=%s")
        update_date = datetime.now()
        # Construction de la requête finale
        requete_update = "UPDATE PROMPTS SET " + ", ".join(update_fields) + " WHERE id_prompt=%s RETURNING *"
        params.append(update_date)
        params.append(id)
        cursor.execute(requete_update, tuple(params))
        new_prompt = cursor.fetchone()
        cursor.connection.commit()
        cursor.close()
        
        return new_prompt,200
    except Exception as e:
        if cursor:
            cursor.connection.rollback()
            cursor.close()
        return {"erreur": str(e)}, 500


def get_all_prompts(current_user):
    cursor = None
    try:
        if current_user.get("nom_role") not in ("ADMINISTRATEUR", "UTILISATEUR"):
            return {"message": "Accès non autorisé"}, 403
            
        cursor = get_cursor()
        #
        cursor.execute("SELECT * FROM PROMPTS")
        prompts = cursor.fetchall()
        map(transforme_prompts,prompts)
        # Les administrateurs voient tous les prompts, les utilisateurs ne voient que les prompts actifs et les leurs
        if current_user.get("nom_role") == "ADMINISTRATEUR":
            requete = "SELECT * FROM PROMPTS"
            cursor.execute(requete)
        else :
            requete = """
                SELECT * FROM PROMPTS 
                WHERE status IN ('ACTIVE','RAPPEL') 
                OR id_utilisateur = %s
            """
            cursor.execute(requete, (current_user.get("id_utilisateur"),))

        prompts = cursor.fetchall()
        
        cursor.close()
        return prompts,200
    except Exception as e:
        if cursor:
            cursor.close()
        return {"erreur": str(e)}, 500

def get_prompt_by_id(current_user, id):
    cursor = None
    try:
        cursor = get_cursor()
        requete = "SELECT * FROM PROMPTS WHERE id_prompt=%s"
        cursor.execute(requete, (id,))
        prompt = cursor.fetchone()
        transforme_prompts(prompt)
        cursor.close()

        if not prompt:
            return {"message": "Prompt non trouvé"}, 404
        
        # Vérifier l'accès au prompt (admins peuvent tout voir, utilisateurs uniquement les prompts actifs ou les leurs)
        if current_user.get("nom_role") != "ADMINISTRATEUR":
            if prompt.get("status") in ("A SUPPRIMER","") and prompt.get("id_utilisateur") != current_user.get("id_utilisateur"):
                return {"message": "Accès non autorisé à ce prompt"}, 403
            
        return prompt,200
    except Exception as e:
        if cursor:
            cursor.close()
        return {"erreur": str(e)}, 500
    
def transforme_prompts(prompt):
    
    date_modification = prompt.get("date_modification")

    # Vérifie que la date est bien un objet datetime
    if not isinstance(date_modification, datetime):
        raise ValueError("Le champ 'date_modification' doit être un objet datetime.")

    # Ajouter 48 heures à la date de modification
    date_expiration = date_modification + timedelta(hours=48)
    date_expiration1 = date_modification + timedelta(hours=24)

    # Comparer avec la date actuelle
    maintenant = datetime.now()
    cursor = get_cursor()
    if prompt.get("status")  in ("EN ATTENTE","A REVOIR") and maintenant > date_expiration:
        requete = "UPDATE PROMPTS SET status=%s WHERE id_prompt=%s" 
        cursor.execute(requete,("RAPPEL",prompt.get("id_prompt")))
        cursor.connection.commit()

    elif prompt.get("status") == "A SUPPRIMER" and maintenant > date_expiration1 :
        requete = "UPDATE PROMPTS SET status=%s WHERE id_prompt=%s" 
        cursor.execute(requete,("RAPPEL",prompt.get("id_prompt")))
        cursor.connectin.commit()
    
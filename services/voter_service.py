from ..databases.connexion import get_cursor
from datetime import datetime

def voter_prompt(current_user,id_prompt):

    try:
        cursor = get_cursor()
        
        # Vérification du prompt
        requete = "SELECT * FROM PROMPTS WHERE id_prompt=%s"
        cursor.execute(requete, (id_prompt,))
        prompt = cursor.fetchone()
        
        if not prompt:
            cursor.close()
            return {"Message": "Prompt introuvable"}
            
        if prompt.get("status") not in ("EN ATTENTE", "RAPPEL"):
            cursor.close()
            return {"Message": "Désolé, ce prompt ne peut pas être voté"}
        
        # Vérification de l'utilisateur auteur du prompt
        requete_utilisateur = "SELECT * FROM UTILISATEURS WHERE id_utilisateur=%s"
        cursor.execute(requete_utilisateur, (prompt.get("id_utilisateur"),))
        utilisateur_auteur = cursor.fetchone()
        
        if not utilisateur_auteur:
            cursor.close()
            return {"Message": "Utilisateur auteur introuvable"},404
        
        # Vérification si l'utilisateur vote son propre prompt
        if current_user.get("id_utilisateur") == prompt.get("id_utilisateur"):
            cursor.close()
            return {"Message": "Désolé, vous ne pouvez pas voter pour votre propre prompt"},101
        
        # Vérification si l'utilisateur a déjà voté pour ce prompt
        verif_vote = "SELECT * FROM VOTER WHERE id_utilisateur=%s AND id_prompt=%s"
        cursor.execute(verif_vote, (current_user.get("id_utilisateur"), id_prompt))
        vote_existant = cursor.fetchone()
        
        if vote_existant:
            cursor.close()
            return {"Message": "Vous avez déjà voté pour ce prompt"},101
        
        # Attribution du poids du vote selon le groupe
        if not current_user.get("id_groupe") or utilisateur_auteur.get("id_groupe") != current_user.get("id_groupe"):
            vote = 1
        else:
            vote = 2
        
        # Enregistrement du vote
        date_vote = datetime.now()
        vote_requete = "INSERT INTO VOTER (id_utilisateur, id_prompt, vote, date_vote) VALUES (%s, %s, %s, %s) RETURNING *"
        cursor.execute(vote_requete, (current_user.get("id_utilisateur"), id_prompt, vote, date_vote))
        votes = cursor.fetchone()
        
        # Calcul du total des votes
        total_vote_requete = "SELECT SUM(vote) as total_vote FROM VOTER WHERE id_prompt=%s"
        cursor.execute(total_vote_requete, (id_prompt,))
        result = cursor.fetchone()
        total_votes = result.get("total_vote", 0) if result else 0
        
        # Mise à jour du statut si le total des votes est suffisant
        if total_votes >= 6:
            update_requete = "UPDATE PROMPTS SET status=%s WHERE id_prompt=%s"
            cursor.execute(update_requete, ("ACTIVE", id_prompt))
        
        # Validation des modifications
        cursor.connection.commit()
        cursor.close()
        
        return votes,200
        
    except Exception as e:
        # En cas d'erreur, annuler les modifications et renvoyer un message d'erreur
        if cursor and cursor.connection:
            cursor.connection.rollback()
            cursor.close()
        return {"Erreur": str(e)}, 500

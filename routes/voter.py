from flask import Blueprint, jsonify
from ..databases.connexion import get_cursor
from datetime import datetime
from .authentification import token_required

voter_blpr = Blueprint("voter_blpr", __name__)

@voter_blpr.route("/prompt/<int:id_prompt>",methods=["POST"])
@token_required
def voter(current_user, id_prompt):
    if current_user.get("nom_role") != "UTILISATEUR":
        return jsonify({"message": "Accès non autorisé"}), 403
    
    cursor = None
    try:
        cursor = get_cursor()
        
        # Vérification du prompt
        requete = "SELECT * FROM PROMPTS WHERE id_prompt=%s"
        cursor.execute(requete, (id_prompt,))
        prompt = cursor.fetchone()
        
        if not prompt:
            cursor.close()
            return jsonify({"Message": "Prompt introuvable"})
            
        if prompt.get("status") not in ("EN ATTENTE", "RAPPEL"):
            cursor.close()
            return jsonify({"Message": "Désolé, ce prompt ne peut pas être voté"})
        
        # Vérification de l'utilisateur auteur du prompt
        requete_utilisateur = "SELECT * FROM UTILISATEURS WHERE id_utilisateur=%s"
        cursor.execute(requete_utilisateur, (prompt.get("id_utilisateur"),))
        utilisateur_auteur = cursor.fetchone()
        
        if not utilisateur_auteur:
            cursor.close()
            return jsonify({"Message": "Utilisateur auteur introuvable"})
        
        # Vérification si l'utilisateur vote son propre prompt
        if current_user.get("id_utilisateur") == prompt.get("id_utilisateur"):
            cursor.close()
            return jsonify({"Message": "Désolé, vous ne pouvez pas voter pour votre propre prompt"})
        
        # Vérification si l'utilisateur a déjà voté pour ce prompt
        verif_vote = "SELECT * FROM VOTER WHERE id_utilisateur=%s AND id_prompt=%s"
        cursor.execute(verif_vote, (current_user.get("id_utilisateur"), id_prompt))
        vote_existant = cursor.fetchone()
        
        if vote_existant:
            cursor.close()
            return jsonify({"Message": "Vous avez déjà voté pour ce prompt"})
        
        # Attribution du poids du vote selon le groupe
        if utilisateur_auteur.get("id_groupe") == current_user.get("id_groupe"):
            vote = 2
        else:
            vote = 1
        
        # Enregistrement du vote
        date_vote = datetime.now()
        vote_requete = "INSERT INTO VOTER (id_utilisateur, id_prompt, vote, date_vote) VALUES (%s, %s, %s, %s)"
        cursor.execute(vote_requete, (current_user.get("id_utilisateur"), id_prompt, vote, date_vote))
        
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
        
        return jsonify({"Reussi": True, "Total_votes": total_votes})
        
    except Exception as e:
        # En cas d'erreur, annuler les modifications et renvoyer un message d'erreur
        if cursor and cursor.connection:
            cursor.connection.rollback()
            cursor.close()
        return jsonify({"Erreur": str(e)}), 500













# from flask import Blueprint,jsonify
# from ..databases.connexion import get_cursor
# from datetime import datetime
# from .authentification import token_required

# voter_blpr = Blueprint("voter_blpr",__name__) 

# @voter_blpr.route("/prompt/<int:id_prompt>")
# @token_required
# def voter(current_user,id_prompt):
#     try:
#         cursor = get_cursor()
        
#         # Vérification du prompt
#         requete = "SELECT * FROM PROMPTS WHERE id_prompt=%s"
#         cursor.execute(requete, (id_prompt,))
#         prompt = cursor.fetchone()
        
#         if not prompt:
#             cursor.close()
#             return jsonify({"Message": "Prompt introuvable"})
            
#         if prompt.get("status") not in ("EN ATTENTE", "RAPPEL"):
#             cursor.close()
#             return jsonify({"Message": "Désolé, ce prompt ne peut pas être voté"})
        
#         # # Vérification de l'utilisateur votant
#         requete1 = "SELECT * FROM UTILISATEURS WHERE id_utilisateur=%s"
#         # cursor.execute(requete1, (current_user.id_utilisateur,))
#         # utilisateur_votant = cursor.fetchone()
        
#         # if not utilisateur_votant:
#         #     cursor.close()
#         #     return jsonify({"Message": "Utilisateur votant introuvable"})
        
#         # Vérification de l'utilisateur auteur du prompt
#         cursor.execute(requete1, (prompt.get("id_utilisateur"),))
#         utilisateur = cursor.fetchone()
        
#         # if not utilisateur:
#         #     cursor.close()
#         #     return jsonify({"Message": "Utilisateur auteur introuvable"})
        
#         # Vérification si l'utilisateur vote son propre prompt
#         if current_user.id_utilisateur == prompt.get("id_utilisateur"):
#             cursor.close()
#             return jsonify({"Message": "Désolé, vous ne pouvez pas voter pour votre propre prompt"})
        
#         # Vérification si l'utilisateur a déjà voté pour ce prompt
#         verif_vote = "SELECT * FROM VOTER WHERE id_utilisateur=%s AND id_prompt=%s"
#         cursor.execute(verif_vote, (current_user.id_utilisateur, id_prompt))
#         vote_existant = cursor.fetchone()
        
#         if vote_existant:
#             cursor.close()
#             return jsonify({"Message": "Vous avez déjà voté pour ce prompt"})
        
#         # Attribution du poids du vote selon le groupe
#         if utilisateur.get("id_groupe") == current_user.get("id_groupe"):
#             vote = 2
#         else:
#             vote = 1
        
#         # Enregistrement du vote
#         date_vote = datetime.now()
#         vote_requete = "INSERT INTO VOTER (id_utilisateur, id_prompt, vote, date_vote) VALUES (%s, %s, %s, %s)"
#         cursor.execute(vote_requete, (current_user.id_utilisateur, id_prompt, vote, date_vote))
        
#         # Calcul du total des votes
#         total_vote_requete = "SELECT sum(vote) as total_vote FROM VOTER WHERE id_prompt=%s"
#         cursor.execute(total_vote_requete, (id_prompt,))
#         result = cursor.fetchone()
#         total_vote = result.get("total_vote", 0) if result else 0
        
#         # Mise à jour du statut si le total des votes est suffisant
#         if total_vote.get("total_vote") >= 6:
#             update_requete = "UPDATE PROMPTS SET status=%s WHERE id_prompt=%s"
#             cursor.execute(update_requete, ("ACTIVE", id_prompt))
        
#         # Validation des modifications
#         cursor.connection.commit()
#         cursor.close()
        
#         return jsonify({"Reussi": True, "Total_votes": total_vote})
        
#     except Exception as e:
#         # En cas d'erreur, annuler les modifications et renvoyer un message d'erreur
#         if cursor and cursor.connection:
#             cursor.connection.rollback()
#             cursor.close()
#         return jsonify({"Erreur": str(e)}), 500
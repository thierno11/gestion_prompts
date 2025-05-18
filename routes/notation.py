from flask import Blueprint, jsonify, request
from .authentification import token_required
from ..services.noter_service import effectuer_notation
notation_bpr = Blueprint("notation_bpr", __name__)

@notation_bpr.route("/prompt/<int:id_prompt>", methods=["POST"])
@token_required
def noter_prompt(current_user, id_prompt):
    if current_user.get("nom_role") != "UTILISATEUR":
        return jsonify({"message": "Accès non autorisé"}), 403
    
    data = request.get_json()
    response,code = effectuer_notation(current_user,id_prompt,data)
    return jsonify(response),code
    




























# from flask import Blueprint,jsonify,request
# from ..databases.connexion import get_cursor
# from datetime import datetime
# from authentification import token_required

# notation_bpr = Blueprint("notation_bpr",__name__)

# @notation_bpr.route("/prompt/<int:id_prompt>",methods=["POST"])
# @token_required
# def noter_prompt(current_user,id_prompt,):
#     try:
#         data = request.get_json()
#         note = data.get("note")  # Correction: quotes autour de "note"
        
#         # Validation de la note (entre -10 et +10)
#         if note is None or not isinstance(note, (int, float)) or note < -10 or note > 10:
#             return jsonify({"Message": "La note doit être un nombre entre -10 et +10"}), 400
            
#         cursor = get_cursor()
        
#         # Vérification du prompt
#         requete = "SELECT * FROM PROMPTS WHERE id_prompt=%s"
#         cursor.execute(requete, (id_prompt,))
#         prompt = cursor.fetchone()
        
#         if not prompt:
#             cursor.close()
#             return jsonify({"Message": "Prompt introuvable"})
        
#         # Vérification de l'utilisateur qui note
#         requete1 = "SELECT * FROM UTILISATEURS WHERE id_utilisateur=%s"
#         cursor.execute(requete1, (id_utilisateur,))
#         utilisateur_note = cursor.fetchone()
        
#         if not utilisateur_note:
#             cursor.close()
#             return jsonify({"Message": "Utilisateur notant introuvable"})
        
#         # Vérification de l'utilisateur auteur du prompt
#         cursor.execute(requete1, (prompt.get("id_utilisateur"),))
#         utilisateur = cursor.fetchone()
        
#         if not utilisateur:
#             cursor.close()
#             return jsonify({"Message": "Utilisateur auteur introuvable"})
        
#         # Vérification si l'utilisateur note son propre prompt
#         if id_utilisateur == prompt.get("id_utilisateur"):
#             cursor.close()
#             return jsonify({"Message": "Désolé, vous ne pouvez pas noter votre propre prompt"})
        
#         # Vérification si l'utilisateur a déjà noté ce prompt
#         verif_note = "SELECT * FROM NOTATION WHERE id_utilisateur=%s AND id_prompt=%s"
#         cursor.execute(verif_note, (id_utilisateur, id_prompt))
#         note_existant = cursor.fetchone()
        
#         if note_existant:
#             cursor.close()
#             return jsonify({"Message": "Vous avez déjà noté ce prompt"})
        
#         # Application du coefficient selon le groupe
#         note_ponderee = note
#         if utilisateur.get("id_groupe") == utilisateur_note.get("id_groupe"):
#             coefficient = 0.6  # 60% pour les membres du même groupe
#         else:
#             coefficient = 0.4  # 40% pour les membres extérieurs
            
#         note_ponderee = note * coefficient
        
#         # Enregistrement de la notation
#         date_note = datetime.now()
#         note_requete = "INSERT INTO NOTATION (id_utilisateur, id_prompt, note, date_note) VALUES (%s, %s, %s, %s)"
#         cursor.execute(note_requete, (id_utilisateur, id_prompt, note_ponderee, date_note))
        
#         # Calcul de la nouvelle moyenne des notes pondérées
#         moyenne_requete = "SELECT AVG(note) as moyenne FROM NOTATION WHERE id_prompt=%s"
#         cursor.execute(moyenne_requete, (id_prompt,))
#         resultat = cursor.fetchone()
#         moyenne = resultat.get("moyenne", 0) if resultat and resultat.get("moyenne") is not None else 0
        
#         # Calcul du nouveau prix selon la formule
#         nouveau_prix = 1000 * (1 + moyenne)
        
#         # Mise à jour du prix du prompt
#         update_prix = "UPDATE PROMPTS SET prix=%s WHERE id_prompt=%s"
#         cursor.execute(update_prix, (nouveau_prix, id_prompt))
        
#         # Validation des modifications
#         # cursor.connection.commit()
#         cursor.close()
        
#         return jsonify({
#             "success": True,
#             "message": "Notation enregistrée avec succès",
#             "note_originale": note,
#             "note_ponderee": note_ponderee,
#             "nouvelle_moyenne": moyenne,
#             "nouveau_prix": nouveau_prix
#         })
        
#     except Exception as e:
#         # En cas d'erreur, annuler les modifications et renvoyer un message d'erreur
#         if 'cursor' in locals() and cursor and cursor.connection:
#             cursor.connection.rollback()
#             cursor.close()
#         return jsonify({"Erreur": str(e)}), 500


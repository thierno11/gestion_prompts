from flask import Blueprint, jsonify
from ..databases.connexion import get_cursor
from datetime import datetime
from .authentification import token_required
from ..services.voter_service import voter_prompt

voter_blpr = Blueprint("voter_blpr", __name__)

@voter_blpr.route("/prompt/<int:id_prompt>",methods=["POST"])
@token_required
def voter(current_user, id_prompt):
    if current_user.get("nom_role") != "UTILISATEUR":
        return jsonify({"message": "Accès non autorisé"}), 403
    
    response,code = voter_prompt(current_user,id_prompt)
    return jsonify(response),code

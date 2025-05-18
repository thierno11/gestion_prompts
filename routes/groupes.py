from flask import Blueprint, request, jsonify
from .authentification import token_required
from ..services.groupes_service import create_groupe,modifier_groupe,recuper_groupe_par_id,recuperer_groupes,supprimer_groupe

groupes_print = Blueprint("groupes_print", __name__)

@groupes_print.route("/", methods=["POST"])
@token_required
def creer_groupes(current_user):
    # Vérification des droits d'administrateur
    if current_user.get("nom_role") != "ADMINISTRATEUR":
        return jsonify({"message": "Accès non autorisé"}), 403
        
    #recuperation et la verification du groupe
    data = request.get_json()
    if not data or "nom_groupe" not in data:
        return jsonify({"message": "Le nom du groupe est requis"}), 400
    nom_groupe = data["nom_groupe"] 
    groupe,code = create_groupe(nom_groupe)
    return jsonify(groupe),code


@groupes_print.route("/<int:id>", methods=["PUT"])
@token_required  
def modifier_groupes(current_user, id):
    # Vérification des droits d'administrateur
    if current_user.get("nom_role") != "ADMINISTRATEUR":
        return jsonify({"message": "Accès non autorisé"}), 403
            
    data = request.get_json()
    if not data or "nom_groupe" not in data:
        return jsonify({"message": "Le nom du groupe est requis"}), 400
            
    nom_groupe = data["nom_groupe"]

    groupe,code =modifier_groupe(id,nom_groupe)
        
    return jsonify(groupe),code


@groupes_print.route("/")
@token_required
def recuperer_tout_groupe(current_user):

    # Vérification des droits d'administrateur
    if current_user.get("nom_role") != "ADMINISTRATEUR":
        return jsonify({"message": "Accès non autorisé"}), 403
    groupes = recuperer_groupes()
    return jsonify(groupes)
        
       

@groupes_print.route("/<int:id>")
@token_required
def recuperer_groupe_par_id(current_user, id):
    # Vérification des droits d'administrateur
    if current_user.get("nom_role") != "ADMINISTRATEUR":
            return jsonify({"message": "Accès non autorisé"}), 403
        
    groupe,code = recuper_groupe_par_id(id)
    return jsonify(groupe),code


@groupes_print.route("/<int:id>", methods=["DELETE"])
@token_required
def supprimer_groupes(current_user, id):
    # Vérification des droits d'administrateur
    if current_user.get("nom_role") != "ADMINISTRATEUR":
        return jsonify({"message": "Accès non autorisé"}), 403

    response,code = supprimer_groupe(id)
    return jsonify(response),code

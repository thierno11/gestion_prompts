from flask import Blueprint, request, jsonify
from .authentification import token_required
from ..services.prompt_services import create_prompt,update_prompt,get_all_prompts,get_prompt_by_id

prompt_bpr = Blueprint("prompt_bpr", __name__)

@prompt_bpr.route("/", methods=["POST"])
@token_required
def creer_prompt(current_user):
    if current_user.get("nom_role") != "UTILISATEUR":
        return jsonify({"message": "Accès non autorisé"}), 403
      
    data = request.get_json()
    response,code = create_prompt(current_user["id_utilisateur"],data)
    return jsonify(response),code

        

@prompt_bpr.route("/<int:id>", methods=["PUT"])
@token_required
def modifier_prompt(current_user, id):
    if current_user.get("nom_role") not in ("UTILISATEUR", "ADMINISTRATEUR"):
        return jsonify({"message": "Accès non autorisé"}), 403
    
    data = request.get_json()
    response,code = update_prompt(current_user,id,data)      
    return jsonify(response),code


@prompt_bpr.route("/")
@token_required
def recuperer_prompts(current_user):
    response,code = get_all_prompts(current_user)
    return jsonify(response),code


@prompt_bpr.route("/<int:id>")
@token_required
def recuperer_prompt_par_id(current_user, id):
    response,code = get_prompt_by_id(current_user,id)
    return jsonify(response,code)


# @prompt_bpr.route("/active")
# def recuperer_prompts_actifs():
#     cursor = None
#     try:
#         cursor = get_cursor()
#         requete = "SELECT * FROM PROMPTS WHERE status=%s"
#         cursor.execute(requete, ("ACTIVE",))
#         prompts_actifs = cursor.fetchall()
#         cursor.close()
        
#         if not prompts_actifs:
#             return jsonify([])
            
#         return jsonify(prompts_actifs)
#     except Exception as e:
#         if cursor:
#             cursor.close()
#         return jsonify({"erreur": str(e)}), 500

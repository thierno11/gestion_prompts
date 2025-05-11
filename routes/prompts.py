from flask import Blueprint, request, jsonify
from ..databases.connexion import get_cursor
from datetime import datetime
from .authentification import token_required

prompt_bpr = Blueprint("prompt_bpr", __name__)

@prompt_bpr.route("/", methods=["POST"])
@token_required
def creer_prompt(current_user):
    cursor = None
    try:
        if current_user.get("nom_role") != "UTILISATEUR":
            return jsonify({"message": "Accès non autorisé"}), 403
        
        data = request.get_json()
        if not data or "libelle" not in data:
            return jsonify({"message": "Le libellé du prompt est requis"}), 400
            
        libelle = data.get("libelle")
        date_creation = datetime.now()
        status = "EN ATTENTE"
        prix = 1000
        id_utilisateur = current_user.get("id_utilisateur")  # Utilisation de l'ID de l'utilisateur authentifié
        
        requete = "INSERT INTO PROMPTS (libelle, status, prix, date_creation, id_utilisateur) VALUES (%s, %s, %s, %s, %s) RETURNING *"
        cursor = get_cursor()
        cursor.execute(requete, (libelle, status, prix, date_creation, id_utilisateur))
        prompt = cursor.fetchone()
        cursor.connection.commit()
        cursor.close()
        
        return jsonify(prompt)
    except Exception as e:
        if cursor:
            cursor.connection.rollback()
            cursor.close()
        return jsonify({"erreur": str(e)}), 500

@prompt_bpr.route("/<int:id>", methods=["PUT"])
@token_required
def modifier_prompt(current_user, id):
    cursor = None
    try:
        if current_user.get("nom_role") not in ("UTILISATEUR", "ADMINISTRATEUR"):
            return jsonify({"message": "Accès non autorisé"}), 403
            
        cursor = get_cursor()
        
        # Vérification du prompt
        requete_check = "SELECT * FROM PROMPTS WHERE id_prompt=%s"
        cursor.execute(requete_check, (id,))
        prompt = cursor.fetchone()
        
        if not prompt:
            cursor.close()
            return jsonify({"message": "Prompt non trouvé"}), 404
            
        # Si utilisateur normal, vérifier qu'il est propriétaire du prompt
        if current_user.get("nom_role") == "UTILISATEUR" and prompt.get("id_utilisateur") != current_user.get("id_utilisateur"):
            cursor.close()
            return jsonify({"message": "Vous ne pouvez modifier que vos propres prompts"}), 403
            
        data = request.get_json()
        if not data:
            cursor.close()
            return jsonify({"message": "Aucune donnée fournie pour la mise à jour"}), 400
            
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
                return jsonify({"message": "Seul un administrateur peut modifier le statut"}), 403
            update_fields.append("status=%s")
            params.append(data.get("status"))
            
        if "prix" in data:
            # Restriction: seul admin peut changer le prix
            if current_user.get("nom_role") != "ADMINISTRATEUR" and data.get("prix") != prompt.get("prix"):
                cursor.close()
                return jsonify({"message": "Seul un administrateur peut modifier le prix"}), 403
            update_fields.append("prix=%s")
            params.append(data.get("prix"))
            
        if not update_fields:
            cursor.close()
            return jsonify({"message": "Aucun champ valide à mettre à jour"}), 400
            
        # Construction de la requête finale
        requete_update = "UPDATE PROMPTS SET " + ", ".join(update_fields) + " WHERE id_prompt=%s RETURNING *"
        params.append(id)
        
        cursor.execute(requete_update, tuple(params))
        new_prompt = cursor.fetchone()
        cursor.connection.commit()
        cursor.close()
        
        return jsonify(new_prompt)
    except Exception as e:
        if cursor:
            cursor.connection.rollback()
            cursor.close()
        return jsonify({"erreur": str(e)}), 500

@prompt_bpr.route("/")
@token_required
def recuperer_prompts(current_user):
    cursor = None
    try:
        if current_user.get("nom_role") not in ("ADMINISTRATEUR", "UTILISATEUR"):
            return jsonify({"message": "Accès non autorisé"}), 403
            
        cursor = get_cursor()
        
        # Les administrateurs voient tous les prompts, les utilisateurs ne voient que les prompts actifs et les leurs
        if current_user.get("nom_role") == "ADMINISTRATEUR":
            requete = "SELECT * FROM PROMPTS"
            cursor.execute(requete)
        else:
            requete = """
                SELECT * FROM PROMPTS 
                WHERE status = 'ACTIVE' 
                OR id_utilisateur = %s
            """
            cursor.execute(requete, (current_user.get("id_utilisateur"),))
            
        prompts = cursor.fetchall()
        cursor.close()
        
        return jsonify(prompts)
    except Exception as e:
        if cursor:
            cursor.close()
        return jsonify({"erreur": str(e)}), 500

@prompt_bpr.route("/<int:id>")
@token_required
def recuperer_prompt_par_id(current_user, id):
    cursor = None
    try:
        if current_user.get("nom_role") not in ("ADMINISTRATEUR", "UTILISATEUR"):
            return jsonify({"message": "Accès non autorisé"}), 403
            
        cursor = get_cursor()
        requete = "SELECT * FROM PROMPTS WHERE id_prompt=%s"
        cursor.execute(requete, (id,))
        prompt = cursor.fetchone()
        cursor.close()
        
        if not prompt:
            return jsonify({"message": "Prompt non trouvé"}), 404
            
        # # Vérifier l'accès au prompt (admins peuvent tout voir, utilisateurs uniquement les prompts actifs ou les leurs)
        # if current_user.get("nom_role") != "ADMINISTRATEUR":
        #     if prompt.get("status") in ("A SUPPRIMER","") and prompt.get("id_utilisateur") != current_user.get("id_utilisateur"):
        #         return jsonify({"message": "Accès non autorisé à ce prompt"}), 403
                
        return jsonify(prompt)
    except Exception as e:
        if cursor:
            cursor.close()
        return jsonify({"erreur": str(e)}), 500

@prompt_bpr.route("/active")
def recuperer_prompts_actifs():
    cursor = None
    try:
        cursor = get_cursor()
        requete = "SELECT * FROM PROMPTS WHERE status=%s"
        cursor.execute(requete, ("ACTIVE",))
        prompts_actifs = cursor.fetchall()
        cursor.close()
        
        if not prompts_actifs:
            return jsonify([])
            
        return jsonify(prompts_actifs)
    except Exception as e:
        if cursor:
            cursor.close()
        return jsonify({"erreur": str(e)}), 500












# from flask import Blueprint,request,jsonify
# from ..databases.connexion import get_cursor
# from datetime import datetime
# from .authentification import token_required

# prompt_bpr = Blueprint("prompt_bpr",__name__)

# @token_required
# @prompt_bpr.route("/",methods=["POST"])
# def creer_prompt(current_user):
#     if current_user.get("nom_role") != "UTILISATEUR":
#         return jsonify({"message": "Accès non autorisé"}), 403
    
#     data = request.get_json()
#     libelle = data.get("libelle")
#     date_creation = datetime.now()
#     status="EN ATTENTE"
#     prix = 1000
#     id_utilisateur = data.get("id_utilisateur")
    
#     requete = "INSERT INTO PROMPTS (libelle,status,prix,date_creation,id_utilisateur) values (%s,%s,%s,%s,%s) RETURNING *"
#     cursor = get_cursor()
#     cursor.execute(requete,(libelle,status,prix,date_creation,id_utilisateur))
#     prompt = cursor.fetchone()
#     cursor.connection.commit()
#     cursor.close()
#     return jsonify(prompt)

# @prompt_bpr.route("/<int:id>",methods=["PUT"])
# @token_required
# def modifier_prompt(current_user,id):
#     if current_user.get("nom_role") not in  ("UTILISATEUR","ADMINISTRATEUR"):
#         return jsonify({"message": "Accès non autorisé"}), 403
#     cursor = get_cursor()
#     requete1 = "SELECT * FROM PROMPTS WHERE id_prompt=%s"
#     cursor.execute(requete1,(id,))
#     prompt = cursor.fetchone()
#     if not prompt:
#         return jsonify({"Message":"Le prompt n'a pas ete trouvee"}),404
#     data = request.get_json()
#     libelle = data.get("libelle")
#     status=data.get("status")
#     prix = data.get("prix")
#     requete2 = "UPDATE PROMPTS SET "
#     parametre = []
#     if libelle :
#         requete2= requete2+"libelle=%s "
#         parametre.append(libelle)
    
#     if status :
#         requete2= requete2+"status=%s "
#         parametre.append(status)
    
#     if prix :
#         requete2= requete2+"prix=%s "
#         parametre.append(prix)
    
#     requete2 = requete2+"WHERE id_prompt =%s RETURNING *"
#     parametre.append(id)
#     cursor.execute(requete2,tuple(parametre))
#     new_prompt = cursor.fetchone()
#     cursor.connection.commit()
#     cursor.close()
#     return jsonify(new_prompt)


# @prompt_bpr.route("/")
# @token_required
# def recuperer_prompts(current_user):
#     if current_user.get("nom_role") not in ("ADMINISTRATEUR","UTILISATEUR"):
#         return jsonify({"message": "Accès non autorisé"}), 403
#     requete = "SELECT * FROM PROMPTS"
#     cursor = get_cursor()
#     cursor.execute(requete)
#     prompts = cursor.fetchall()
#     return jsonify(prompts)


# @prompt_bpr.route("/<int:id>")
# @token_required
# def recuperer_prompt_par_id(current_user,id):
#     if current_user.get("nom_role") not in ("ADMINISTRATEUR","UTILISATEUR"):
#         return jsonify({"message": "Accès non autorisé"}), 403
    
#     requete = "SELECT * FROM PROMPTS WHERE id_prompt=%s"
#     cursor = get_cursor()
#     cursor.execute(requete,(id,))
#     utilisateur = cursor.fetchone()
#     if not utilisateur:
#         return jsonify({"Message":"L'utilisateur n'a pas ete trouve"})
#     return jsonify(utilisateur)


# @prompt_bpr.route("/active")
# def recuperer_prompt_active():
#     requete = "SELECT * FROM PROMPTS WHERE status=%s"
#     cursor = get_cursor()
#     cursor.execute(requete,("ACTIVE",))
#     utilisateur = cursor.fetchall()
#     if not utilisateur:
#         return jsonify({"Message":"L'utilisateur n'a pas ete trouve"})
#     return jsonify(utilisateur)



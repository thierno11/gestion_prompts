from flask import Blueprint, request, jsonify
from ..databases.connexion import get_cursor
from .authentification import token_required

groupes_print = Blueprint("groupes_print", __name__)

@groupes_print.route("/", methods=["POST"])
@token_required
def creer_groupes(current_user):
    try:
        # Vérification des droits d'administrateur
        if current_user.get("nom_role") != "ADMINISTRATEUR":
            return jsonify({"message": "Accès non autorisé"}), 403
        
        data = request.get_json()
        if not data or "nom_groupe" not in data:
            return jsonify({"message": "Le nom du groupe est requis"}), 400
            
        nom_groupe = data["nom_groupe"]
        script = "INSERT INTO GROUPES(nom_groupe) VALUES(%s) RETURNING *"  
        
        cursor = get_cursor()  
        cursor.execute(script, (nom_groupe,))
        groupe = cursor.fetchone()  
        
        cursor.connection.commit()  
        cursor.close()  
        
        return jsonify(groupe)
    except Exception as e:
        if 'cursor' in locals() and cursor:
            cursor.connection.rollback()
            cursor.close()
        return jsonify({"erreur": str(e)}), 500

@groupes_print.route("/<int:id>", methods=["PUT"])
@token_required  
def modifier_groupe(current_user, id):
    cursor = None
    try:
        # Vérification des droits d'administrateur
        if current_user.get("nom_role") != "ADMINISTRATEUR":
            return jsonify({"message": "Accès non autorisé"}), 403
            
        data = request.get_json()
        if not data or "nom_groupe" not in data:
            return jsonify({"message": "Le nom du groupe est requis"}), 400
            
        nom_groupe = data["nom_groupe"]
        
        cursor = get_cursor()
        
        # Vérifier si le groupe existe
        check_query = "SELECT * FROM GROUPES WHERE id_groupe = %s"
        cursor.execute(check_query, (id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"message": "Groupe non trouvé"}), 404
        
        requete = "UPDATE GROUPES SET nom_groupe=%s WHERE id_groupe=%s RETURNING *"  
        cursor.execute(requete, (nom_groupe, id))
        groupe = cursor.fetchone()  
        
        cursor.connection.commit()  
        cursor.close()  
        
        return jsonify(groupe)
    except Exception as e:
        if cursor:
            cursor.connection.rollback()
            cursor.close()
        return jsonify({"erreur": str(e)}), 500

@groupes_print.route("/")
@token_required
def recuperer_tout_groupe(current_user):
    cursor = None
    try:
        # Vérification des droits d'administrateur
        if current_user.get("nom_role") != "ADMINISTRATEUR":
            return jsonify({"message": "Accès non autorisé"}), 403
        
        cursor = get_cursor()
        requete = "SELECT * FROM GROUPES"
        cursor.execute(requete)
        groupes = cursor.fetchall()
        cursor.close()
        return jsonify(groupes)
    except Exception as e:
        if cursor:
            cursor.close()
        return jsonify({"erreur": str(e)}), 500

@groupes_print.route("/<int:id>")
@token_required
def recuperer_groupe_par_id(current_user, id):
    cursor = None
    try:
        # Vérification des droits d'administrateur
        if current_user.get("nom_role") != "ADMINISTRATEUR":
            return jsonify({"message": "Accès non autorisé"}), 403
        
        cursor = get_cursor()
        requete = "SELECT * FROM GROUPES WHERE id_groupe = %s"
        cursor.execute(requete, (id,))
        groupe = cursor.fetchone()
        cursor.close()
        
        if not groupe:
            return jsonify({"message": "Groupe non trouvé"}), 404
        
        return jsonify(groupe)
    except Exception as e:
        if cursor:
            cursor.close()
        return jsonify({"erreur": str(e)}), 500

@groupes_print.route("/<int:id>", methods=["DELETE"])
@token_required
def supprimer_groupe(current_user, id):
    cursor = None
    try:
        # Vérification des droits d'administrateur
        if current_user.get("nom_role") != "ADMINISTRATEUR":
            return jsonify({"message": "Accès non autorisé"}), 403
        
        cursor = get_cursor()
        
        # Vérifier si le groupe existe avant de le supprimer
        check_query = "SELECT * FROM GROUPES WHERE id_groupe = %s"
        cursor.execute(check_query, (id,))
        groupe = cursor.fetchone()
        
        if not groupe:
            cursor.close()
            return jsonify({"message": "Groupe non trouvé"}), 404
            
        # Vérifier si des utilisateurs sont associés à ce groupe
        check_users = "SELECT COUNT(*) as count FROM UTILISATEURS WHERE id_groupe = %s"
        cursor.execute(check_users, (id,))
        user_count = cursor.fetchone().get("count", 0)
        
        if user_count > 0:
            cursor.close()
            return jsonify({"message": "Impossible de supprimer un groupe contenant des utilisateurs"}), 400
        
        # Procéder à la suppression
        delete_query = "DELETE FROM GROUPES WHERE id_groupe = %s"
        cursor.execute(delete_query, (id,))
        cursor.connection.commit()
        cursor.close()
        
        return jsonify({"message": "Groupe supprimé avec succès"})
    except Exception as e:
        if cursor:
            cursor.connection.rollback()
            cursor.close()
        return jsonify({"erreur": str(e)}), 500













# from flask import Blueprint, request, jsonify
# from ..databases.connexion import get_cursor
# from .authentification import token_required

# groupes_print = Blueprint("groupes_print", __name__)

# @groupes_print.route("/", methods=["POST"])
# @token_required
# def creer_groupes(current_user):
#     if current_user.get("nom_role") != "ADMINISTRATEUR":
#         return jsonify({"message": "Accès non autorisé"}), 403
    
#     data = request.get_json()
#     nom_groupe = data["nom_groupe"]
#     script = "INSERT INTO GROUPES(nom_groupe) VALUES(%s) RETURNING *"  
    
#     cursor = get_cursor()  
#     cursor.execute(script, (nom_groupe,))
#     groupe = cursor.fetchone()  
    
#     cursor.connection.commit()  
#     cursor.close()  
    
#     return jsonify(groupe)

# @groupes_print.route("/<int:id>", methods=["PUT"])  
# def modifier_groupe(id):
#     data = request.get_json()
#     nom_groupe = data["nom_groupe"]
#     requete = "UPDATE GROUPES SET nom_groupe=%s WHERE id_groupe=%s RETURNING *"  
    
#     cursor = get_cursor()  
#     cursor.execute(requete, (nom_groupe, id))
#     groupe = cursor.fetchone()  
    
#     cursor.connection.commit()  
#     cursor.close()  
    
#     return jsonify(groupe)



# @groupes_print.route("/")
# @token_required
# def recuperer_tout_membre(current_user):
#     if current_user.get("nom_role") != "ADMINISTRATEUR":
#         return jsonify({"message": "Accès non autorisé"}), 403
    
#     cursor = get_cursor()
#     requete = "SELECT * FROM GROUPES"
#     cursor.execute(requete)
#     groupes = cursor.fetchall()
#     return jsonify(groupes)



# @groupes_print.route("/<int:id>")
# @token_required
# def recuperer_membre_par_id(current_user,id):
#     if current_user.get("nom_role") != "ADMINISTRATEUR":
#         return jsonify({"message": "Accès non autorisé"}), 403
    
#     cursor = get_cursor()
#     requete = "SELECT * FROM GROUPES WHERE id_groupe = %s"
#     cursor.execute(requete,(id,))
#     groupe = cursor.fetchone()
#     if not groupe:
#         return jsonify(None),404
#     return jsonify(groupe)

# @groupes_print.route("/<int:id>",methods=["DELETE"])
# @token_required
# def delete_membre(current_user,id):
#     if current_user.get("nom_role") != "ADMINISTRATEUR":
#         return jsonify({"message": "Accès non autorisé"}), 403
    
#     cursor = get_cursor()
#     requete1 = "SELECT * FROM GROUPES WHERE id_groupe = %s"
#     requete = "DELETE FROM GROUPES WHERE id_groupe=%s"

#     cursor.execute(requete1,(id,))
#     groupe = cursor.fetchone()
#     if not groupe:
#         return jsonify({"Message":"Le groupe n'a pas ete trouvee"}),404
#     cursor.execute(requete,(id,))
#     cursor.connection.commit()
#     cursor.close()
#     return jsonify({"Message":"La supression a reussi"})
    
    



















# # from flask import Blueprint,request,jsonify
# # from databases.connexion import get_cursor

# # groupes_print = Blueprint("groupes_print",__name__)

# # cursor = get_cursor()

# # @groupes_print.route("/",methods=["POST"])
# # def creer_groupes():
# #     data = request.get_json()
# #     nom_groupe = data["nom_groupe"]
# #     script = "INSERT INTO GROUPES(nom_groupe) VALUES(%s)"
# #     cursor.execute(script,(nom_groupe,))
# #     groupe = cursor.fetchone()
# #     return jsonify(groupe)

# # @groupes_print.route("/<int:id>")
# # def modifier_groupe(id):
# #     data = request.get_json()
# #     nom_groupe = data["nom_groupe"]
# #     requete = "UPDATE GROUPES SET nom_groupe=%s WHERE id_groupe=%s"
# #     cursor.execute(requete,(nom_groupe,id))
# #     groupe = cursor.fetchone()
# #     return jsonify(groupe)


    
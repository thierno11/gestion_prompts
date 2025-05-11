from flask import Blueprint, request, jsonify
from ..databases.connexion import get_cursor
from werkzeug.security import generate_password_hash
from .authentification import token_required
import re

utilisateur_bpr = Blueprint("utilisateur_bpr", __name__)

def validate_email(email):
    """Valide le format d'une adresse email"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_input(data, required_fields=None):
    """Valide les données d'entrée"""
    if not data:
        return False, "Aucune donnée fournie"
    
    if required_fields:
        missing_fields = [field for field in required_fields if field not in data or not data.get(field)]
        if missing_fields:
            return False, f"Champs obligatoires manquants: {', '.join(missing_fields)}"
    
    if "email" in data and data.get("email") and not validate_email(data.get("email")):
        return False, "Format d'email invalide"
    
    if "password" in data and data.get("password") and len(data.get("password")) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    
    return True, ""

@utilisateur_bpr.route("/register", methods=["POST"])
@token_required
def creer_utilisateur(current_user):
    # Vérifier si l'utilisateur actuel a les droits d'administrateur
    if current_user.get("nom_role") != "ADMIN":
        return jsonify({"message": "Accès non autorisé"}), 403
    
    data = request.get_json()
    
    # Validation des données
    valid, message = validate_input(data, ["nom", "prenom", "email", "password", "role"])
    if not valid:
        return jsonify({"message": message}), 400
    
    nom = data.get("nom")
    prenom = data.get("prenom")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")
    id_groupe = data.get("id_groupe")
    
    # Vérifier si l'email existe déjà
    cursor = get_cursor()
    check_query = "SELECT * FROM UTILISATEURS WHERE email = %s"
    cursor.execute(check_query, (email,))
    if cursor.fetchone():
        cursor.close()
        return jsonify({"message": "Cet email est déjà utilisé"}), 409
    
    try:
        hashed_password = generate_password_hash(password)
        
        requete = """
            INSERT INTO UTILISATEURS(nom, prenom, email, password, nom_role, id_groupe) 
            VALUES (%s, %s, %s, %s, %s, %s) 
            RETURNING id_utilisateur, nom, prenom, email, nom_role, id_groupe
        """
        
        cursor.execute(requete, (nom, prenom, email, hashed_password, role, id_groupe))
        utilisateur = cursor.fetchone()
        cursor.connection.commit()
        
        return jsonify({"message": "Utilisateur créé avec succès", "utilisateur": utilisateur}), 201
    except Exception as e:
        cursor.connection.rollback()
        return jsonify({"message": f"Erreur lors de la création de l'utilisateur: {str(e)}"}), 500
    finally:
        cursor.close()


@utilisateur_bpr.route("/<int:id>", methods=["PUT"])
@token_required
def modifier_utilisateur(current_user, id):
    # Vérifier si l'utilisateur actuel est admin ou modifie son propre profil
    if current_user.get("nom_role") != "ADMINISTRATEUR" and current_user.get("id_utilisateur") != id:
        return jsonify({"message": "Accès non autorisé"}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({"message": "Aucune donnée fournie"}), 400
    
    cursor = get_cursor()
    
    try:
        # Vérifier si l'utilisateur existe
        requet = "SELECT * FROM UTILISATEURS WHERE id_utilisateur = %s"
        cursor.execute(requet, (id,))
        utilisateur = cursor.fetchone()
        
        if not utilisateur:
            return jsonify({"message": "L'utilisateur que vous voulez modifier n'existe pas"}), 404
        
        # Construire la requête UPDATE correctement
        update_params = []
        update_fields = []
        
        if "nom" in data and data["nom"]:
            update_fields.append("nom = %s")
            update_params.append(data["nom"])
        
        if "prenom" in data and data["prenom"]:
            update_fields.append("prenom = %s")
            update_params.append(data["prenom"])
        
        if "email" in data and data["email"]:
            if not validate_email(data["email"]):
                return jsonify({"message": "Format d'email invalide"}), 400
                
            # Vérifier si l'email est déjà utilisé par un autre utilisateur
            check_query = "SELECT * FROM UTILISATEURS WHERE email = %s AND id_utilisateur != %s"
            cursor.execute(check_query, (data["email"], id))
            if cursor.fetchone():
                return jsonify({"message": "Cet email est déjà utilisé"}), 409
                
            update_fields.append("email = %s")
            update_params.append(data["email"])
        
        if "password" in data and data["password"]:
            if len(data["password"]) < 8:
                return jsonify({"message": "Le mot de passe doit contenir au moins 8 caractères"}), 400
            
            hashed_password = generate_password_hash(data["password"])
            update_fields.append("password = %s")
            update_params.append(hashed_password)
        
        if "nom_role" in data and data["nom_role"]:
            # Seul un admin peut modifier le rôle
            if current_user.get("nom_role") != "ADMININISTRATEUR":
                return jsonify({"message": "Vous n'avez pas les droits pour modifier le rôle"}), 403
            
            update_fields.append("nom_role = %s")
            update_params.append(data["nom_role"])
        if "id_groupe" in data and  data["id_groupe"]:
            cursor.execute("SELECT * GROUPES WHERE id_groupe=%s",(data["id_groupe"]))
            groupe = cursor.fetchone()
            if not groupe:
                return jsonify({"Message":"Le groupe n'existe pas"})
            update_fields.append("id_groupe")
            update_params.append(data["id_groupe"])
        
        if not update_fields:
            return jsonify({"message": "Aucun champ à mettre à jour"}), 400
        
        # Construire la requête UPDATE avec les champs à mettre à jour
        update_requete = f"UPDATE UTILISATEURS SET {', '.join(update_fields)} WHERE id_utilisateur = %s RETURNING id_utilisateur, nom, prenom, email, nom_role, id_groupe"
        update_params.append(id)
        
        cursor.execute(update_requete, tuple(update_params))
        updated_user = cursor.fetchone()
        cursor.connection.commit()
        
        return jsonify({"message": "Utilisateur mis à jour avec succès", "utilisateur": updated_user})
    
    except Exception as e:
        cursor.connection.rollback()
        return jsonify({"message": f"Erreur lors de la mise à jour de l'utilisateur: {str(e)}"}), 500
    finally:
        cursor.close()


@utilisateur_bpr.route("/<int:id>", methods=["DELETE"])
@token_required
def supprimer_utilisateur(current_user, id):
    # Seul un administrateur peut supprimer un utilisateur
    if current_user.get("nom_role") != "ADMINISTRATEUR":
        return jsonify({"message": "Accès non autorisé"}), 403
    
    cursor = get_cursor()
    
    try:
        # Vérifier si l'utilisateur existe
        requete1 = "SELECT * FROM UTILISATEURS WHERE id_utilisateur = %s"
        cursor.execute(requete1, (id,))
        utilisateur = cursor.fetchone()
        
        if not utilisateur:
            return jsonify({"message": "L'utilisateur n'a pas été trouvé"}), 404
        
        # Empêcher la suppression du propre compte de l'administrateur
        if id == current_user.get("id_utilisateur"):
            return jsonify({"message": "Vous ne pouvez pas supprimer votre propre compte"}), 403
        
        requete2 = "DELETE FROM UTILISATEURS WHERE id_utilisateur = %s"
        cursor.execute(requete2, (id,))
        cursor.connection.commit()
        
        return jsonify({"message": "L'utilisateur a été supprimé avec succès"})
    
    except Exception as e:
        cursor.connection.rollback()
        return jsonify({"message": f"Erreur lors de la suppression de l'utilisateur: {str(e)}"}), 500
    finally:
        cursor.close()


@utilisateur_bpr.route("/")
@token_required
def recuperer_utilisateurs(current_user):
    # Contrôle d'accès: seul un admin peut voir tous les utilisateurs
    if current_user.get("nom_role") != "ADMINISTRATEUR":
        return jsonify({"message": "Accès non autorisé"}), 403
    
    try:
        requete = "SELECT id_utilisateur, nom, prenom, email, nom_role, id_groupe FROM UTILISATEURS"
        cursor = get_cursor()
        cursor.execute(requete)
        utilisateurs = cursor.fetchall()
        cursor.close()
        
        return jsonify(utilisateurs)
    except Exception as e:
        return jsonify({"message": f"Erreur lors de la récupération des utilisateurs: {str(e)}"}), 500


@utilisateur_bpr.route("/<int:id>")
@token_required
def recuperer_utilisateur(current_user, id):
    # Un utilisateur peut voir son propre profil, un admin peut voir tous les profils
    if current_user.get("nom_role") != "ADMINISTRATEUR" and current_user.get("id_utilisateur") != id:
        return jsonify({"message": "Accès non autorisé"}), 403
    
    try:
        requete = "SELECT id_utilisateur, nom, prenom, email, nom_role, id_groupe FROM UTILISATEURS WHERE id_utilisateur = %s"
        cursor = get_cursor()
        cursor.execute(requete, (id,))
        utilisateur = cursor.fetchone()
        cursor.close()
        
        if not utilisateur:
            return jsonify({"message": "Utilisateur non trouvé"}), 404
        
        return jsonify(utilisateur)
    except Exception as e:
        return jsonify({"message": f"Erreur lors de la récupération de l'utilisateur: {str(e)}"}), 500


















# from flask import Blueprint,request,jsonify
# from ..databases.connexion import get_cursor
# from werkzeug.security import generate_password_hash
# from .authentification import token_required

# utilisateur_bpr = Blueprint("utilisateur_bpr",__name__)

# @utilisateur_bpr.route("/register",methods=["POST"])
# def creer_utilisateur():
#     data = request.get_json()
#     nom = data.get("nom")
#     prenom = data.get("prenom")
#     email = data.get("email")
#     password = data.get("password")
#     role = data.get("role")
#     id_groupe = data.get("id_groupe")
#     hashed_password = generate_password_hash(password,)
#     print(hashed_password)
#     cursor = get_cursor()
#     requete = "INSERT INTO UTILISATEURS(nom,prenom,email,password,nom_role,id_groupe) values (%s,%s,%s,%s,%s,%s) RETURNING *"

#     cursor.execute(requete,(nom,prenom,email,hashed_password,role,id_groupe))
#     utilisateur = cursor.fetchone()
#     cursor.connection.commit()
#     cursor.close()
#     return jsonify(utilisateur)


# @utilisateur_bpr.route("/<int:id>",methods=["PUT"])
# def modifier_utilisateur(id):
#     data = request.get_json()
#     nom = data.get("nom")
#     prenom = data.get("prenom")
#     email = data.get("email")
#     password = data.get("password")
#     role = data.get("nom_role")
#     requet = "SELECT * FROM UTILISATEURS WHERE id_utilisateur=%s"
#     cursor = get_cursor()
#     cursor.execute(requet,(id,))
#     utilisateur = cursor.fetchone()
#     update_requete = "UPDATE UTILISATEURS SET "
#     prarametre = []
#     if  not utilisateur:
#         return jsonify({"Message":"L'utilisateur aue vous voulez modier n'existe pas "}),404
#     if nom:
#         update_requete = update_requete + "nom=%s "
#         prarametre.append(nom)
#     if prenom:
#         update_requete = update_requete + "prenom=%s "
#         prarametre.append(prenom)
#     if email :
#         update_requete = update_requete+"email=%s "
#         prarametre.append(email)
#     if password :
#         update_requete = update_requete+"password=%s "
#         prarametre.append(password)
#     if role:
#         update_requete = update_requete+"nom_role=%s "
#         prarametre.append(role)

#     update_requete= update_requete+"WHERE id_utilisateur=%s RETURNING *"
#     prarametre.append(id)
#     cursor.execute(update_requete,tuple(prarametre))
#     updated_user = cursor.fetchone()
#     cursor.connection.commit()
#     cursor.close()
#     return jsonify(updated_user)

# @utilisateur_bpr.route("/<int:id>",methods=["DELETE"])
# def supprimer_utilisateur(id):
#     cursor = get_cursor()
#     requete1 = "SELECT * FROM UTILISATEURS WHERE id_utilisateur=%s"
#     requete2 = "DELETE FROM UTILISATEURS WHERE id_utilisateur=%s"

#     cursor.execute(requete1,(id,))
#     utilisateur = cursor.fetchone()
#     if not utilisateur:
#         return jsonify({"Message":"L'utilisateur n'a pas ete trouvee"})
#     cursor.execute(requete2,(id,))
#     cursor.connection.commit()
#     cursor.close()
#     return jsonify({"Message":"L'utilisateur a ete suprimee avec succes"})


# @utilisateur_bpr.route("/")
# @token_required
# def recuperer_utilisateurs():
#     requete = "SELECT * FROM UTILISATEURS"
#     cursor = get_cursor()
#     cursor.execute(requete)
#     utilisateurs = cursor.fetchall()
#     return jsonify(utilisateurs)


# @utilisateur_bpr.route("/<int:id>")
# def recuperer_utilisateur(id):
#     requete = "SELECT * FROM UTILISATEURS WHERE id_utilisateur=%s"
#     cursor = get_cursor()
#     cursor.execute(requete,(id,))
#     utilisateur = cursor.fetchone()
#     if not utilisateur:
#         return jsonify({"Message":"Utilisateur not found"}),401
#     return jsonify(utilisateur)
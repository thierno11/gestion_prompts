from flask import Blueprint, request, jsonify
from ..databases.connexion import get_cursor
from werkzeug.security import generate_password_hash
from .authentification import token_required
import re

from ..services.utilisateurs_service import create_utilisateur_service,get_all_users,delete_user,get_user_by_id,update_user

utilisateur_bpr = Blueprint("utilisateur_bpr", __name__)


@utilisateur_bpr.route("/register", methods=["POST"])
@token_required
def creer_utilisateur(current_user):
    # Vérifier si l'utilisateur actuel a les droits d'administrateur
    if current_user.get("nom_role") != "ADMINISTRATEUR":
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
    
    utilisateur,code = create_utilisateur_service(nom,prenom,email,password,role,id_groupe)
    return jsonify(utilisateur),code
    

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
        
        
        response,code = update_user(id,update_params,update_fields)
        return jsonify(response),code
    
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
      
    response,code = delete_user(id,current_user)
    return jsonify(response),code


@utilisateur_bpr.route("/")
@token_required
def recuperer_utilisateurs(current_user):
    # Contrôle d'accès: seul un admin peut voir tous les utilisateurs
    if current_user.get("nom_role") != "ADMINISTRATEUR":
        return jsonify({"message": "Accès non autorisé"}), 403
    response,code=get_all_users()    
    return jsonify(response),code

@utilisateur_bpr.route("/<int:id>")
@token_required
def recuperer_utilisateur(current_user, id):
    # Un utilisateur peut voir son propre profil, un admin peut voir tous les profils
    if current_user.get("nom_role") != "ADMINISTRATEUR" and current_user.get("id_utilisateur") != id:
        return jsonify({"message": "Accès non autorisé"}), 403
    
    response,code = get_user_by_id(id) 
    return jsonify(response),code

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
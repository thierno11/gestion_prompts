from flask import request, Flask, jsonify, Blueprint
from ..databases.connexion import get_cursor
from functools import wraps
import jwt
from werkzeug.security import check_password_hash
import os
from datetime import datetime, timezone, timedelta


auth_blp = Blueprint("auth_blp", __name__)

@auth_blp.route("/", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("username")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"message": "Email et mot de passe requis"}), 400
    
    requete1 = "SELECT * FROM UTILISATEURS WHERE email=%s"
    cursor = get_cursor()
    cursor.execute(requete1, (email,))
    utilisateur = cursor.fetchone()
    
    if not utilisateur or not check_password_hash(utilisateur.get("password"), password):
        return jsonify({"message": "Identifiant ou mot de passe incorrect"}), 401
    
    payload = {
        "id": utilisateur.get("id_utilisateur"),  # Ajout de l'ID pour la vérification
        "nom": utilisateur.get("nom"),
        "prenom": utilisateur.get("prenom"),
        "nom_role": utilisateur.get("nom_role"),
        "email": email,
        "groupe": utilisateur.get("id_groupe"),
        'exp': datetime.now(timezone.utc) + timedelta(hours=1)
    }
    
    token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")
    
    return jsonify({"token": token})


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            # Format attendu: "Bearer <token>"
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        
        if not token:
            return jsonify({'message': 'Token manquant!'}), 401
        
        try:
            data = jwt.decode(token, os.getenv
                              ('SECRET_KEY'), algorithms=["HS256"])
            print(data)
            email = data["email"]
            # Utilisation de l'ID utilisateur pour la recherche
            user_id = data.get("email")
            requete = "SELECT * FROM UTILISATEURS WHERE email=%s"
            cursor = get_cursor()
            cursor.execute(requete, (email,))
            current_user = cursor.fetchone()
            print(current_user)
            if not current_user:
                return jsonify({'message': 'Utilisateur non trouvé!'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expiré!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token invalide!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated



def admin(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        data = request.headers.get("Authorization")
        if not data or len(data.split(" "))<1:
            return jsonify("Token not found")
        token = data.split(" ")[1]
        data = jwt.decode(token,os.getenv("SECRET_KEY"),algorithms=["HS256"])
        print(data)
        
    return decorated




# from flask import request,Flask,jsonify,Blueprint
# from ..databases.connexion import get_cursor
# from functools import wraps
# import jwt
# from werkzeug.security import check_password_hash
# import os
# from datetime import datetime, timezone, timedelta


# auth_blp = Blueprint("auth_blp",__name__)

# @auth_blp.route("/",methods=["POST"])
# def login():
#     data = request.get_json()
#     email = data.get("username")
#     password = data.get("password")
#     requete1 = "SELECT * FROM UTILISATEURS WHERE email=%s"
#     cursor = get_cursor()
#     cursor.execute(requete1,(email,))
#     utilisateur = cursor.fetchone()
#     if not utilisateur  or not check_password_hash(utilisateur.get("password"),password):
#         return jsonify({"Message":"Identifiant ou Mot de passe incorrect"})
    
#     payload ={
#         "nom":utilisateur.get("nom"),
#         "prenom":utilisateur.get("prenom"),
#         "nom_role":utilisateur.get("nom_role"),
#         "email":email,
#         "groupe":utilisateur.get("id_groupe"),
#         'exp': datetime.now(timezone.utc) + timedelta(hours=1)
#     }
#     token = jwt.encode(payload,os.getenv("SECRET_KEY"),algorithm="HS256")

#     return jsonify({"token":token})



# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.authorization
#         if not token:
#             return jsonify({'message': 'Token is missing!'}), 401
#         # token = str(token)
#         # token = token.split()[1]
#         try:
#             data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])

#             username = data.get("email")
#             requete = "SELECT * FROM UTILISATEUR WHERE id_utilisateur=%s"
#             cursor = get_cursor()
#             cursor.execute(requete,(username,))
#             current_user = cursor.fetchone()
#         except:
#             return jsonify({'message': 'Token is invalid!'}), 401

#         return f(current_user, *args, **kwargs)

#     return decorated
    
from flask import Blueprint,request,jsonify
from ..databases.connexion import get_cursor

utilisateur_bpr = Blueprint("utilisateur_bpr",__name__)

@utilisateur_bpr.route("/register",methods=["POST"])
def creer_utilisateur():
    data = request.get_json()
    nom = data.get("nom")
    prenom = data.get("prenom")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")
    id_groupe = data.get("id_groupe")
    cursor = get_cursor()
    requete = "INSERT INTO UTILISATEURS(nom,prenom,email,password,nom_role,id_groupe) values (%s,%s,%s,%s,%s,%s) RETURNING *"

    cursor.execute(requete,(nom,prenom,email,password,role,id_groupe))
    utilisateur = cursor.fetchone()
    cursor.connection.commit()
    cursor.close()
    return jsonify(utilisateur)


@utilisateur_bpr.route("/<int:id>",methods=["PUT"])
def modifier_utilisateur(id):
    data = request.get_json()
    nom = data.get("nom")
    prenom = data.get("prenom")
    email = data.get("email")
    password = data.get("password")
    role = data.get("nom_role")
    requet = "SELECT * FROM UTILISATEURS WHERE id_utilisateur=%s"
    cursor = get_cursor()
    cursor.execute(requet,(id,))
    utilisateur = cursor.fetchone()
    update_requete = "UPDATE UTILISATEURS SET "
    prarametre = []
    if  not utilisateur:
        return jsonify({"Message":"L'utilisateur aue vous voulez modier n'existe pas "}),404
    if nom:
        update_requete = update_requete + "nom=%s "
        prarametre.append(nom)
    if prenom:
        update_requete = update_requete + "prenom=%s "
        prarametre.append(prenom)
    if email :
        update_requete = update_requete+"email=%s "
        prarametre.append(email)
    if password :
        update_requete = update_requete+"password=%s "
        prarametre.append(password)
    if role:
        update_requete = update_requete+"nom_role=%s "
        prarametre.append(role)

    update_requete= update_requete+"WHERE id_utilisateur=%s RETURNING *"
    prarametre.append(id)
    cursor.execute(update_requete,tuple(prarametre))
    updated_user = cursor.fetchone()
    cursor.connection.commit()
    cursor.close()
    return jsonify(updated_user)

@utilisateur_bpr.route("/<int:id>",methods=["DELETE"])
def supprimer_utilisateur(id):
    cursor = get_cursor()
    requete1 = "SELECT * FROM UTILISATEURS WHERE id_utilisateur=%s"
    requete2 = "DELETE FROM UTILISATEURS WHERE id_utilisateur=%s"

    cursor.execute(requete1,(id,))
    utilisateur = cursor.fetchone()
    if not utilisateur:
        return jsonify({"Message":"L'utilisateur n'a pas ete trouvee"})
    cursor.execute(requete2,(id,))
    cursor.connection.commit()
    cursor.close()
    return jsonify({"Message":"L'utilisateur a ete suprimee avec succes"})


@utilisateur_bpr.route("/")
def recuperer_utilisateurs():
    requete = "SELECT * FROM UTILISATEURS"
    cursor = get_cursor()
    cursor.execute(requete)
    utilisateurs = cursor.fetchall()
    return jsonify(utilisateurs)


@utilisateur_bpr.route("/<int:id>")
def recuperer_utilisateur(id):
    requete = "SELECT * FROM UTILISATEURS WHERE id_utilisateur=%s"
    cursor = get_cursor()
    cursor.execute(requete,(id,))
    utilisateur = cursor.fetchone()
    if not utilisateur:
        return jsonify({"Message":"Utilisateur not found"}),401
    return jsonify(utilisateur)
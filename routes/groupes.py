from flask import Blueprint, request, jsonify
from ..databases.connexion import get_cursor

groupes_print = Blueprint("groupes_print", __name__)

@groupes_print.route("/", methods=["POST"])
def creer_groupes():
    data = request.get_json()
    nom_groupe = data["nom_groupe"]
    script = "INSERT INTO GROUPES(nom_groupe) VALUES(%s) RETURNING *"  
    
    cursor = get_cursor()  
    cursor.execute(script, (nom_groupe,))
    groupe = cursor.fetchone()  
    
    cursor.connection.commit()  
    cursor.close()  
    
    return jsonify(groupe)

@groupes_print.route("/<int:id>", methods=["PUT"])  
def modifier_groupe(id):
    data = request.get_json()
    nom_groupe = data["nom_groupe"]
    requete = "UPDATE GROUPES SET nom_groupe=%s WHERE id_groupe=%s RETURNING *"  
    
    cursor = get_cursor()  
    cursor.execute(requete, (nom_groupe, id))
    groupe = cursor.fetchone()  
    
    cursor.connection.commit()  
    cursor.close()  
    
    return jsonify(groupe)



@groupes_print.route("/")
def recuperer_tout_membre():
    cursor = get_cursor()
    requete = "SELECT * FROM GROUPES"
    cursor.execute(requete)
    groupes = cursor.fetchall()
    return jsonify(groupes)



@groupes_print.route("/<int:id>")
def recuperer_membre_par_id(id):
    cursor = get_cursor()
    requete = "SELECT * FROM GROUPES WHERE id_groupe = %s"
    cursor.execute(requete,(id,))
    groupe = cursor.fetchone()
    if not groupe:
        return jsonify(None),404
    return jsonify(groupe)

@groupes_print.route("/<int:id>",methods=["DELETE"])
def delete_membre(id):
    cursor = get_cursor()
    requete1 = "SELECT * FROM GROUPES WHERE id_groupe = %s"
    requete = "DELETE FROM GROUPES WHERE id_groupe=%s"

    cursor.execute(requete1,(id,))
    groupe = cursor.fetchone()
    if not groupe:
        return jsonify({"Message":"Le groupe n'a pas ete trouvee"}),404
    cursor.execute(requete,(id,))
    cursor.connection.commit()
    cursor.close()
    return jsonify({"Message":"La supression a reussi"})
    
    



















# from flask import Blueprint,request,jsonify
# from databases.connexion import get_cursor

# groupes_print = Blueprint("groupes_print",__name__)

# cursor = get_cursor()

# @groupes_print.route("/",methods=["POST"])
# def creer_groupes():
#     data = request.get_json()
#     nom_groupe = data["nom_groupe"]
#     script = "INSERT INTO GROUPES(nom_groupe) VALUES(%s)"
#     cursor.execute(script,(nom_groupe,))
#     groupe = cursor.fetchone()
#     return jsonify(groupe)

# @groupes_print.route("/<int:id>")
# def modifier_groupe(id):
#     data = request.get_json()
#     nom_groupe = data["nom_groupe"]
#     requete = "UPDATE GROUPES SET nom_groupe=%s WHERE id_groupe=%s"
#     cursor.execute(requete,(nom_groupe,id))
#     groupe = cursor.fetchone()
#     return jsonify(groupe)


    
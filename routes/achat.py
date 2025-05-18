from  flask import Blueprint,request,jsonify
from ..databases.connexion import get_cursor
from .authentification import admin

achat_blp = Blueprint("achat_blp",__name__)

@achat_blp.route("/<int:id_prompt>",methods=["POST"])
@admin
def acheter_prompt(id_prompt):
    cursor = get_cursor()
    cursor.execute("SELECT * FROM PROMPTS WHERE id_prompt=%s",(id_prompt,))
    prompts = cursor.fetchone()
    if not prompts:
        return jsonify("Le prompt aue vous afficher n'existe pas")
    
    data = request.get_json()
    nom = data.get("nom") if data.get("nom") else ""
    email = data.get("email") if data.get("email") else ""
    montant = data.get("montant")
    if not montant or montant<prompts.get("prix"):
        return jsonify("Le montant est insuffisant")
    cursor.execute("INSERT INTO ACHATS (nom_acheteur,email_acheteur,montant,id_prompt) values(%s,%s,%s,%s)RETURNING * ",(nom,email,montant,id_prompt))
    achat = cursor.fetchone()
    if not achat:
        return jsonify("L'achat n'a pas reussi")

    return jsonify(achat)


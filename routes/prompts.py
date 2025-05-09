from flask import Blueprint,request,jsonify
from ..databases.connexion import get_cursor
from datetime import datetime

prompt_bpr = Blueprint("prompt_bpr",__name__)

@prompt_bpr.route("/",methods=["POST"])
def creer_prompt():
    data = request.get_json()
    libelle = data.get("libelle")
    date_creation = datetime.now()
    status="EN ATTENTE"
    prix = 1000
    id_utilisateur = data.get("id_utilisateur")
    
    requete = "INSERT INTO PROMPTS (libelle,status,prix,date_creation,id_utilisateur) values (%s,%s,%s,%s,%s) RETURNING *"
    cursor = get_cursor()
    cursor.execute(requete,(libelle,status,prix,date_creation,id_utilisateur))
    prompt = cursor.fetchone()
    cursor.connection.commit()
    cursor.close()
    return jsonify(prompt)

@prompt_bpr.route("/<int:id>",methods=["PUT"])
def modifier_prompt(id):
    cursor = get_cursor()
    requete1 = "SELECT * FROM PROMPTS WHERE id_prompt=%s"
    cursor.execute(requete1,(id,))
    prompt = cursor.fetchone()
    if not prompt:
        return jsonify({"Message":"Le prompt n'a pas ete trouvee"}),404
    data = request.get_json()
    libelle = data.get("libelle")
    status=data.get("status")
    prix = data.get("prix")
    requete2 = "UPDATE PROMPTS SET "
    parametre = []
    if libelle :
        requete2= requete2+"libelle=%s "
        parametre.append(libelle)
    
    if status :
        requete2= requete2+"status=%s "
        parametre.append(status)
    
    if prix :
        requete2= requete2+"prix=%s "
        parametre.append(prix)
    
    requete2 = requete2+"WHERE id_prompt =%s RETURNING *"
    parametre.append(id)
    cursor.execute(requete2,tuple(parametre))
    new_prompt = cursor.fetchone()
    cursor.connection.commit()
    cursor.close()
    return jsonify(new_prompt)


@prompt_bpr.route("/")
def recuperer_prompts():
    requete = "SELECT * FROM PROMPTS"
    cursor = get_cursor()
    cursor.execute(requete)
    prompts = cursor.fetchall()
    return jsonify(prompts)

@prompt_bpr.route("/<int:id>")
def recuperer_prompt_par_id(id):
    requete = "SELECT * FROM PROMPTS WHERE id_prompt=%s"
    cursor = get_cursor()
    cursor.execute(requete,(id,))
    utilisateur = cursor.fetchone()
    if not utilisateur:
        return jsonify({"Message":"L'utilisateur n'a pas ete trouve"})
    return jsonify(utilisateur)


@prompt_bpr.route("/<status>")
def recuperer_prompt_active(status):
    requete = "SELECT * FROM PROMPTS WHERE status=%s"
    cursor = get_cursor()
    cursor.execute(requete,(status,))
    utilisateur = cursor.fetchall()
    if not utilisateur:
        return jsonify({"Message":"L'utilisateur n'a pas ete trouve"})
    return jsonify(utilisateur)



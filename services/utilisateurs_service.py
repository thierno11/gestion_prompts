from ..databases.connexion import get_cursor
from werkzeug.security import generate_password_hash


def create_utilisateur_service(nom,prenom,email,password,role,id_groupe):
    cursor = get_cursor()
    #verifier si le groupe existe 
    if id_groupe:
        check_groupe_query = "SELECT * FROM GROUPES WHERE id_groupe=%s"
        cursor.execute(check_groupe_query,(id_groupe,))
        groupe = cursor.fetchone()
        if not groupe:
            return {"message": "Le groupe n'existe pas "}, 404
        
    # verification de l'adresse email
    check_query = "SELECT * FROM UTILISATEURS WHERE email = %s"
    cursor.execute(check_query, (email,))
    if cursor.fetchone():
        cursor.close()
        return {"message": "Cet email est déjà utilisé"}, 409
    
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
        
        return utilisateur, 201
    except Exception as e:
        cursor.connection.rollback()
        return {"message": f"Erreur lors de la création de l'utilisateur: {str(e)}"}, 500
    finally:
        cursor.close()
    
def delete_user(id,current_user):
    cursor = get_cursor()
    
    try:
        # Vérifier si l'utilisateur existe
        requete1 = "SELECT * FROM UTILISATEURS WHERE id_utilisateur = %s"
        cursor.execute(requete1, (id,))
        utilisateur = cursor.fetchone()
        
        
        if not utilisateur:
            return {"message": "L'utilisateur n'a pas été trouvé"}, 404
        

        # Empêcher la suppression du propre compte de l'administrateur
        if id == current_user.get("id_utilisateur"):
            return {"message": "Vous ne pouvez pas supprimer votre propre compte"}, 403
        

        requete2 = "DELETE FROM UTILISATEURS WHERE id_utilisateur = %s"
        cursor.execute(requete2, (id,))
        cursor.connection.commit()
        
        return {"message": "L'utilisateur a été supprimé avec succès"},200
    
    except Exception as e:
        cursor.connection.rollback()
        return {"message": f"Erreur lors de la suppression de l'utilisateur: {str(e)}"}, 500
    finally:
        cursor.close()

def get_all_users():
    try:
        requete = "SELECT * FROM UTILISATEURS"
        cursor = get_cursor()
        cursor.execute(requete)
        utilisateurs = cursor.fetchall()
        cursor.close()
        return utilisateurs,200
    except Exception as e:
        return {"message": f"Erreur lors de la récupération des utilisateurs: {str(e)}"}, 500
    
def get_user_by_id(id):    
    try:
        requete = "SELECT id_utilisateur, nom, prenom, email, nom_role, id_groupe FROM UTILISATEURS WHERE id_utilisateur = %s"
        cursor = get_cursor()
        cursor.execute(requete, (id,))
        utilisateur = cursor.fetchone()
        cursor.close()
        
        if not utilisateur:
            return {"message": "Utilisateur non trouvé"}, 404
        
        return utilisateur,200
    except Exception as e:
        return {"message": f"Erreur lors de la récupération de l'utilisateur: {str(e)}"}, 500

def update_user(id,update_params,update_fields):
    
    cursor = get_cursor()
    
    try:
        # Vérifier si l'utilisateur existe
        requet = "SELECT * FROM UTILISATEURS WHERE id_utilisateur = %s"
        cursor.execute(requet, (id,))
        utilisateur = cursor.fetchone()
        
        if not utilisateur:
            return {"message": "L'utilisateur que vous voulez modifier n'existe pas"}, 404
        
        # Construire la requête UPDATE correctement
        

        if not update_fields:
            return {"message": "Aucun champ à mettre à jour"}, 400
        
        # Construire la requête UPDATE avec les champs à mettre à jour
        update_requete = f"UPDATE UTILISATEURS SET {', '.join(update_fields)} WHERE id_utilisateur = %s RETURNING id_utilisateur, nom, prenom, email, nom_role, id_groupe"
        update_params.append(id)
        
        cursor.execute(update_requete, tuple(update_params))
        updated_user = cursor.fetchone()
        cursor.connection.commit()
        
        return {"utilisateur": updated_user},200
    
    except Exception as e:
        cursor.connection.rollback()
        return {"message": f"Erreur lors de la mise à jour de l'utilisateur: {str(e)}"}, 500
    finally:
        cursor.close()
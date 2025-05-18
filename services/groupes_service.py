from ..databases.connexion import get_cursor


def create_groupe(nom_groupe):
    try:
        script = "INSERT INTO GROUPES(nom_groupe) VALUES(%s) RETURNING *"  
        cursor = get_cursor()  
        cursor.execute(script, (nom_groupe,))
        groupe = cursor.fetchone()  
        cursor.connection.commit()  
        cursor.close() 
        if not groupe:
               return None
        return groupe,200
    except Exception as e:
        cursor.connection.rollback()
        cursor.close()
        return {"erreur": str(e)}, 500


def modifier_groupe(id,nom_groupe):
    try:
        cursor = get_cursor()
        requete = "UPDATE GROUPES SET nom_groupe=%s WHERE id_groupe=%s RETURNING *"  
        cursor.execute(requete, (nom_groupe, id))
        groupe = cursor.fetchone()  
        cursor.connection.commit()  
        cursor.close()
        return groupe,200
    except Exception as e:
        cursor.connection.rollback()
        cursor.close()
        return {"Erreur":str(e)},500

def supprimer_groupe(id):
    try:
        cursor = get_cursor()
        
        # Vérifier si le groupe existe avant de le supprimer
        # check_query = "SELECT * FROM GROUPES WHERE id_groupe = %s"
        # cursor.execute(check_query, (id,))
        # groupe = cursor.fetchone()
        groupe,code = recuper_groupe_par_id(id)
        if code == 404:
            return groupe,code
            
        # Vérifier si des utilisateurs sont associés à ce groupe
        check_users = "SELECT COUNT(*) as count FROM UTILISATEURS WHERE id_groupe = %s"
        cursor.execute(check_users, (id,))
        user_count = cursor.fetchone().get("count", 0)
        
        if user_count > 0:
            cursor.close()
            return {"message": "Impossible de supprimer un groupe contenant des utilisateurs"},500
        
        # Procéder à la suppression
        delete_query = "DELETE FROM GROUPES WHERE id_groupe = %s"
        cursor.execute(delete_query, (id,))
        cursor.connection.commit()
        cursor.close()
        return {"Message":"Suppression du groupe reussi"},200
    except Exception as ex:
        cursor.connection.rollback()
        cursor.close()
        return {"Erreur":str(ex)},500

def recuperer_groupes():        
    cursor = get_cursor()
    requete = "SELECT * FROM GROUPES"
    cursor.execute(requete)
    groupes = cursor.fetchall()
    cursor.close()
    return groupes

def recuper_groupe_par_id(id):
        cursor = get_cursor()
        requete = "SELECT * FROM GROUPES WHERE id_groupe = %s"
        cursor.execute(requete, (id,))
        groupe = cursor.fetchone()
        cursor.close()
        
        if not groupe:
            return {"Message":"Le groupe n'existe pas"},404
        
        return groupe,200
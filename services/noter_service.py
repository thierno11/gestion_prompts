from ..databases.connexion import get_cursor
from datetime import datetime

def effectuer_notation(current_user, id_prompt,data):
    cursor = None
    try:
        note = data.get("note")
        
        # Validation de la note (entre -10 et +10)
        if note is None or not isinstance(note, (int, float)) or note < -10 or note > 10:
            return {"Message": "La note doit être un nombre entre -10 et +10"}, 400
            
        cursor = get_cursor()
        
        # Vérification du prompt
        requete = "SELECT * FROM PROMPTS WHERE id_prompt=%s"
        cursor.execute(requete, (id_prompt,))
        prompt = cursor.fetchone()

        if not prompt:
            cursor.close()
            return {"Message": "Prompt introuvable"},404
        if prompt.get("status") !="ACTIVE":
            cursor.close()
            return {"Message": "Le prompte n'est pas active"},101
        # Récupération de l'ID utilisateur
        id_utilisateur = current_user.get("id_utilisateur")
        
        # # Vérification de l'utilisateur qui note
        requete_utilisateur = "SELECT * FROM UTILISATEURS WHERE id_utilisateur=%s"
        
        # Vérification de l'utilisateur auteur du prompt
        cursor.execute(requete_utilisateur, (prompt.get("id_utilisateur"),))
        utilisateur_auteur = cursor.fetchone()
        
        if not utilisateur_auteur:
            cursor.close()
            return {"Message": "Utilisateur auteur introuvable"}
        
        # Vérification si l'utilisateur note son propre prompt
        if id_utilisateur == prompt.get("id_utilisateur"):
            cursor.close()
            return {"Message": "Désolé, vous ne pouvez pas noter votre propre prompt"},404
        
        # Vérification si l'utilisateur a déjà noté ce prompt
        verif_note = "SELECT * FROM NOTATION WHERE id_utilisateur=%s AND id_prompt=%s"
        cursor.execute(verif_note, (id_utilisateur, id_prompt))
        note_existant = cursor.fetchone()
        
        if note_existant:
            cursor.close()
            return {"Message": "Vous avez déjà noté ce prompt"},101
        
        # Application du coefficient selon le groupe
        if utilisateur_auteur.get("id_groupe") == current_user.get("id_groupe"):
            coefficient = 0.6  # 60% pour les membres du même groupe
        else:
            coefficient = 0.4  # 40% pour les membres extérieurs
            
        note_ponderee = note * coefficient
        
        # Enregistrement de la notation
        date_note = datetime.now()
        note_requete = "INSERT INTO NOTATION (id_utilisateur, id_prompt, note, date_note) VALUES (%s, %s, %s, %s) RETURNING *"
        cursor.execute(note_requete, (id_utilisateur, id_prompt, note_ponderee, date_note))
        notes = cursor.fetchone()
        # Calcul de la nouvelle moyenne des notes pondérées
        moyenne_requete = "SELECT AVG(note) as moyenne FROM NOTATION WHERE id_prompt=%s"
        cursor.execute(moyenne_requete, (id_prompt,))
        resultat = cursor.fetchone()
        moyenne = resultat.get("moyenne", 0) if resultat and resultat.get("moyenne") is not None else 0
        
        # Calcul du nouveau prix selon la formule
        nouveau_prix = 1000 * (1 + moyenne)
        
        # Mise à jour du prix du prompt
        update_prix = "UPDATE PROMPTS SET prix=%s WHERE id_prompt=%s"
        cursor.execute(update_prix, (nouveau_prix, id_prompt))
        
        # Validation des modifications
        cursor.connection.commit()
        cursor.close()
        return notes,200
        
    except Exception as e:
        # En cas d'erreur, annuler les modifications et renvoyer un message d'erreur
        if cursor and cursor.connection:
            cursor.connection.rollback()
            cursor.close()
        return {"Erreur": str(e)}, 500


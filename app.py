from flask import Flask
from .databases.connexion import init_database
from .routes.groupes import groupes_print
from .routes.utilisateurs import utilisateur_bpr
from .routes.prompts import prompt_bpr
# init_database()
app = Flask(__name__)



app.register_blueprint(groupes_print,url_prefix="/groupes")
app.register_blueprint(utilisateur_bpr,url_prefix="/utilisateurs")
app.register_blueprint(prompt_bpr,url_prefix="/prompts")
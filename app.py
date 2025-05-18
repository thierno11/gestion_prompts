from flask import Flask
from .databases.connexion import init_database
from .routes.groupes import groupes_print
from .routes.utilisateurs import utilisateur_bpr
from .routes.prompts import prompt_bpr
from .routes.voter import voter_blpr
from .routes.notation import notation_bpr
from .routes.authentification import auth_blp
from .routes.achat import achat_blp
init_database()

app = Flask(__name__)



app.register_blueprint(groupes_print,url_prefix="/groupes")

app.register_blueprint(utilisateur_bpr,url_prefix="/utilisateurs")
app.register_blueprint(prompt_bpr,url_prefix="/prompts")
app.register_blueprint(voter_blpr,url_prefix="/votes")
app.register_blueprint(notation_bpr,url_prefix="/notes")
app.register_blueprint(auth_blp,url_prefix="/login")
app.register_blueprint(achat_blp,url_prefix="/achat")
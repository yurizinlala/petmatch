# -*- coding: utf-8 -*-
# Entry point for the Flask application (for deployment)
from src.app import create_app, db
# from src.app.models import User, Pet, Adoption # Import models if needed for shell context or commands

app = create_app()

# Optional: Add shell context processor for Flask shell commands
@app.shell_context_processor
def make_shell_context():
    # return {'db': db, 'User': User, 'Pet': Pet, 'Adoption': Adoption}
    return {'db': db} # Keep it simple for now

# Note: This file is primarily for the deployment tool to find the app instance.
# Running the development server is usually done via 'flask run' command
# after setting FLASK_APP=src/main.py and FLASK_ENV=development.


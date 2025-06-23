# -*- coding: utf-8 -*-
from flask import Blueprint

# Define the blueprint
bp = Blueprint("adoptions", __name__, template_folder="templates/adoptions") # Specify template folder if needed

# Import routes at the end to avoid circular dependencies
from src.app.adoptions import routes # Uncomment when routes.py is created

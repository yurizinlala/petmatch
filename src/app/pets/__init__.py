# -*- coding: utf-8 -*-
from flask import Blueprint

# Define the blueprint
bp = Blueprint("pets", __name__, template_folder="templates/pets") # Specify template folder if needed

# Import routes at the end to avoid circular dependencies
from src.app.pets import routes


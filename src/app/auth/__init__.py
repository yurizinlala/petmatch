# -*- coding: utf-8 -*-
from flask import Blueprint

# Define the blueprint
bp = Blueprint("auth", __name__, template_folder="templates/auth") # Specify template folder if needed

# Import routes at the end to avoid circular dependencies
from src.app.auth import routes


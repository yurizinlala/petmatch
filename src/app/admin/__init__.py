# -*- coding: utf-8 -*-
from flask import Blueprint

# Define the blueprint
bp = Blueprint("admin", __name__, template_folder="templates/admin") # Specify template folder if needed

# Import routes at the end to avoid circular dependencies
from src.app.admin import routes


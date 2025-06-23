# -*- coding: utf-8 -*-
from flask import Blueprint

# Define the blueprint
bp = Blueprint("main", __name__, template_folder="templates")

# Import routes at the end to avoid circular dependencies
from src.app.main import routes


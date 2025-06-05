# -*- coding: utf-8 -*-
# Entry point for the Flask application (for deployment)
from src.app import create_app, db
from src.app import models # Import models to access seed_data
import click

app = create_app()

# Optional: Add shell context processor for Flask shell commands
@app.shell_context_processor
def make_shell_context():
    # return {"db": db, "User": User, "Pet": Pet, "Adoption": Adoption}
    return {"db": db, "models": models} # Add models for easier access in shell

# Custom CLI command to seed the database
@app.cli.command("seed")
def seed_db():
    """Populates the database with initial pet data."""
    click.echo("Seeding database...")
    models.seed_data(app) # Call the seed function from models
    click.echo("Database seeded!")

# Note: This file is primarily for the deployment tool to find the app instance.
# Running the development server is usually done via "flask run" command
# after setting FLASK_APP=src/main.py and FLASK_ENV=development.


# SED-Assignment

## About
This repository contains my assignment coursework for the Software Engineering & DevOps module. The application is an asset management tool that is built using FastAPI and SQLite3.

### Development
For development, it is recommended that you setup a python Virtual Environment (venv). To begin development, activate it and install the project requirements located in the [requirements.txt](requirements.txt)

Run `fastapi dev app/main.py` from the root of the project

The application should now be accessible on `http://localhost:8000`, with Swagger API docs available at `http://localhost:8000/docs`

### Tests
Run `pytest tests/` from the root of the project

### Deployment
To run the application server use `fastapi run app/main.py`
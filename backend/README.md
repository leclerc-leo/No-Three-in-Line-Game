

# Install

installer les dependances
- `sudo apt update && sudo apt install -y python3-pip python3-venv python-is-python3`
- `pip3 install pipx`
- `pipx install poetry && pipx ensurepath`

installer le projet, les dependances, l'environnement virtuel python
- `poetry install`

lancer les tests pour verifier le fonctionnement
- `make premerge`

Pour faire tourner le programme principal
- `poetry run main`

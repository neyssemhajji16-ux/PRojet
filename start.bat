@echo off
echo ===================================
echo  Startup Stress-Test TN - Demarrage
echo ===================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH.
    echo Veuillez installer Python 3.8+ depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/2] Installation des dependances...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERREUR] Echec de l'installation des dependances.
    pause
    exit /b 1
)

echo.
echo [2/2] Lancement du serveur...
echo.
echo Le serveur est accessible sur http://localhost:5000
echo Appuyez sur Ctrl+C pour arreter le serveur.
echo.
python app.py
pause

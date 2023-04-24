import subprocess
import os
import sys

def run_django_server():
    try:
        directorio = os.getcwd()
        os.chdir(directorio)  # ruta servidor django
        subprocess.Popen(["python", "manage.py", "runserver"])
        print("Servidor Django ejecutándose...")
    except Exception as e:
        print("Error al ejecutar el servidor Django:", e)

def run_flask_server():
    try:
        directorio = os.getcwd()
        os.chdir(directorio+"/api_back")  # ruta servidor flask
        os.environ["FLASK_APP"] = "app.py"
        subprocess.Popen(["flask", "run"])
        print("Servidor Flask ejecutándose...")
    except Exception as e:
        print("Error al ejecutar el servidor Flask:", e)

def main():
    run_django_server()
    run_flask_server()

    print("Presione Ctrl+C para terminar los servidores.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Terminando servidores...")
        sys.exit(0)

if __name__ == "__main__":
    main()
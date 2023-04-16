from django.shortcuts import render
from django.http import HttpResponse
from django.http import FileResponse
import os
import requests
import xml.etree.ElementTree as ET

#obtener la ruta del pdf 
def get_file_path(filename):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'ventana/templates', filename)
    return file_path

# Create your views here.

def home(request):
    return render(request, 'home.html')

def info_estudiante(request):
    return render(request, 'estudiante_info.html')

def documentacion(request):
    filename = 'DocumentacionOficial_202110509.pdf'
    file_path = get_file_path(filename)
    return FileResponse(open(file_path, 'rb'), content_type='application/pdf')

def index(request):
    # Hacer una solicitud HTTP a la ruta de Flask
    url = 'http://localhost:5000'
    response = requests.get(url)

    # Parsear el archivo XML
    root = ET.fromstring(response.content)
    msg = root.find('msg').text
    status = root.find('status').text

    return render(request, 'index.html', {'msg': msg, 'status': status})
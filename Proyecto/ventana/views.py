from django.shortcuts import render
from django.http import HttpResponse
from django.http import FileResponse
import os
import requests
import xml.etree.ElementTree as ET
from collections import defaultdict



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

def enviar_mensaje(request):
    return render(request, 'enviar_mensaje.html')

def documentacion(request):
    filename = 'DocumentacionOficial_202110509.pdf'
    file_path = get_file_path(filename)
    return FileResponse(open(file_path, 'rb'), content_type='application/pdf')


def r_servicio1(request):
    response = requests.get('http://localhost:5000/servicio1Respuesta_xml')
    if response.status_code == 200:
        contenido = response.text
    else:
        contenido = f"Error: {response.status_code} - {response.text}"
    return render(request, 'r_servicio1.html', {'contenido': contenido})

def r_servicio2(request):
    response = requests.get('http://localhost:5000/servicio2Respuesta_xml')
    if response.status_code == 200:
        contenido = response.text
    else:
        contenido = f"Error: {response.status_code} - {response.text}"
    return render(request, 'r_servicio2.html', {'contenido': contenido})

def r_mensajes(request):
    response = requests.get('http://localhost:5000/mensajeRespuesta')
    if response.status_code == 200:
        contenido = response.text
    else:
        contenido = f"Error: {response.status_code} - {response.text}"
    return render(request, 'r_mensajes.html', {'contenido': contenido})

def parse_base2_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    data = {}

    for message in root.findall('mensaje'):
        timestamp = message.find('lugar_fecha').text
        username = message.find('usuario').text
        perfiles = message.find('perfiles')
        
        profile_data = {}
        for perfil in perfiles.findall('perfil'):
            profile_name = perfil.find('nombre').text
            if profile_name is not None and profile_name.lower() != '"none"':
                profile_percentage = perfil.find('porcentaje').text
                profile_data[profile_name] = profile_percentage

        if username not in data:
            data[username] = []

        msg_data = {
            'timestamp': timestamp,
            'perfiles': profile_data
        }
        data[username].append(msg_data)

    return data

def tabla_probabilidades(request):
    data = parse_base2_xml('api_back/base2.xml')
    context = {'data': data}
    return render(request, 'tabla_probabilidades.html', context)


def calcular_peso_promedio(perfil_porcentajes):
    suma_porcentajes = 0
    contador = 0

    for porcentaje in perfil_porcentajes:
        if porcentaje != 0:
            suma_porcentajes += porcentaje
            contador += 1

    peso_promedio = suma_porcentajes / contador if contador > 0 else 0
    return peso_promedio


def calcular_pesos_promedio(data):
    pesos_promedio = {}

    for username, messages in data.items():
        perfiles_suma = defaultdict(int)
        perfiles_cantidad = defaultdict(int)

        for message in messages:
            for perfil, porcentaje in message['perfiles'].items():
                porcentaje_numerico = float(porcentaje.rstrip('%'))

                if porcentaje_numerico != 0:
                    perfiles_suma[perfil] += porcentaje_numerico
                    perfiles_cantidad[perfil] += 1

        perfil_pesos = {}
        for perfil, suma in perfiles_suma.items():
            cantidad = perfiles_cantidad[perfil]
            peso_promedio = suma / cantidad if cantidad > 0 else 0
            perfil_pesos[perfil] = round(peso_promedio, 2)

        pesos_promedio[username] = perfil_pesos

    return pesos_promedio

def tabla_pesos(request):
    data = parse_base2_xml('api_back/base2.xml')
    pesos_promedio = calcular_pesos_promedio(data)
    lista_perfiles = list(pesos_promedio.values())[0].keys()  # Convierte las claves en una lista
    num_columns = len(lista_perfiles) + 1
    context = {'pesos_promedio': pesos_promedio, 'lista_perfiles': lista_perfiles, 'num_columns': num_columns}
    return render(request, 'tabla_pesos.html', context)
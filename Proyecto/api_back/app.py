from flask import Flask, Response, make_response
from flask_cors import CORS
#importar jsonfy para convertir a json
from flask import jsonify
import xml.etree.ElementTree as ET
from flask import Flask, request
from servicio1 import XMLProcessor
from servicio2 import MessageProcessor
import os
import datetime
processor = MessageProcessor()

app = Flask(__name__)
CORS(app)

#ver si funciona el servidor
@app.route('/')
def index():
    msj = {
        'msg':'Servidor funcionando correctamente',
        'status':200
    }
    # Crear un elemento raíz para el archivo XML
    root = ET.Element('mensaje')
    # Agregar los elementos del diccionario a los elementos del archivo XML
    for key, value in msj.items():
        ET.SubElement(root, key).text = str(value)
    # Crear la respuesta con el archivo XML y el tipo de contenido adecuado
    xml_string = ET.tostring(root, encoding='utf-8', method='xml')
    response = make_response(xml_string)
    response.headers.set('Content-Type', 'application/xml')
    return response


respuesta = ""

#servicio 1, agregar, actualizar perfiles y palabras descartadas
@app.route('/servicio1_xml', methods=['POST'])
def servicio1_xml():
    global respuesta
    # Verifica si se ha enviado un archivo
    if not request.files:
        return 'No se encontró el archivo', 400

    # Obtiene el primer archivo enviado
    xml_file = next(iter(request.files.values()))

    # Procesa el archivo XML
    data = XMLProcessor.process_xml(xml_file)

    # Añade la información procesada a la base de datos (el archivo XML)
    response = XMLProcessor.add_baseDatos(data)
    respuesta = response
    return response

def ReiniciarServicio1():
    # Contenido básico del archivo XML
    global respuesta
    contenido_basico = '''<?xml version="1.0" encoding="UTF-8"?>
    <configuracion>
        <perfiles>
            <perfil>
                <nombre></nombre>
                <palabrasClave>
                <palabra></palabra>
                </palabrasClave>
            </perfil>
        </perfiles>
        <descartadas>
            <palabra></palabra>
        </descartadas>
    </configuracion>
    '''
    with open('base1.xml', 'w', encoding='utf-8') as file:
        file.write(contenido_basico)
    respuesta = f"""<?xml version="1.0"?>
                <respuesta>
                   <perfilesNuevos>
                     Se han creado {0} perfiles nuevos
                   </perfilesNuevos>
                   <perfilesExistentes>
                     Se han actualizado {0} perfiles existentes
                   </perfilesExistentes>
                   <descartadas>
                     Se han creado {0} nuevas palabras a descartar
                   </descartadas>
                </respuesta>"""

@app.route('/reiniciar', methods=['GET'])
def api_reiniciar_base_datos():
    ReiniciarServicio1()
    reiniciarServicio2()
    #Base de datos reiniciada,
    return 'Base de datos reiniciada',200

@app.route('/servicio1Respuesta_xml', methods=['GET'])
def servicio1_xml_get():
    return respuesta


#servicio 2, procesar mensajes
respuesta1 = ""
@app.route('/servicio2_xml', methods=['POST'])
def servicio2_xml():
    if not request.files:
        return 'No se encontró el archivo', 400
    
    xml_file = next(iter(request.files.values()))
    
    if xml_file.filename == '':
        return 'No se seleccionó ningún archivo', 400

    if xml_file and xml_file.filename.lower().endswith('.xml'):
        xml_content = xml_file.read().decode('utf-8')
        processor.process_messages(xml_content)
    
    global respuesta1
    respuesta = processor.regresarRespuesta()
    respuesta1 = respuesta
    return respuesta


@app.route('/servicio2Respuesta_xml', methods=['GET'])
def servicio2_xml_get():
    return respuesta1


def reiniciarServicio2():
    global respuesta1
    respuesta1 = f"""<?xml version="1.0" ?>
<mensajes_procesados>
</mensajes_procesados>"""

    with open('base2.xml', 'w', encoding='utf-8') as file:
        file.write(respuesta1)

# @app.route('/mensajePrueba', methods=['POST'])
# def mensajePrueba():
#     xml_content = request.data.decode()
#     processor.process_messages(xml_content)
#     return 'Mensajes procesados', 200


@app.route('/mensajePrueba', methods=['POST'])
def mensajePrueba():
    xml_content = request.data.decode()
    processor.process_messages(xml_content)
    infoMsj = processor.procesarRespuesta(xml_content)


    fecha = infoMsj['fecha']
    usuario = infoMsj['usuario']
    perf = processor.quitarDescartadas_numeros(infoMsj['contenido'])
    perfiles = processor.calculate_profile_percentages(perf)

    processed_data = {
        'fecha': fecha,
        'usuario': usuario,
        'perfiles': perfiles
    }
    

    salida_parts = [f"""
    <?xml version="1.0" ?>
        <respuesta>
            <fechaHora> {processed_data['fecha']} </fechaHora>
            <usuario> {processed_data['usuario']} </usuario>
            <perfiles>"""
    ]

    for perfil, porcentaje in processed_data['perfiles'].items():
        if perfil and perfil.lower() != 'none':
            salida_parts.append(
                f"""
                <perfil nombre={perfil}>
                    <porcentajeProbabilidad> {porcentaje:.2f}% </porcentajeProbabilidad>
                </perfil>""")

    salida_parts.append(f"""
            </perfiles>\n         </respuesta>""")

    global salida
    salida = ''.join(salida_parts)
    
    return 'Mensajes procesados', 200

@app.route('/mensajeRespuesta', methods=['GET'])
def mensajeRespuesta():
    return salida


if __name__ == '__main__':
    app.run(debug=True, port=5000)
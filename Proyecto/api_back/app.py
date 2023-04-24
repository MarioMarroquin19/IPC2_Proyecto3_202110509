from flask import Flask, make_response
from flask_cors import CORS
#importar jsonfy para convertir a json
from flask import jsonify
import xml.etree.ElementTree as ET
from flask import Flask, request
from servicio1 import XMLProcessor
from servicio2 import MessageProcessor

app = Flask(__name__)
CORS(app)

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

@app.route('/horaActual', methods=['GET'])
def horaActual():
    return 'La Hora Actual'

@app.route('/ConsultarDatos', methods=['GET'])
def ConsultarDatos():
    return 'Los datos consultados son:'

@app.route('/ActualizarDatos', methods=['POST'])
def ActualizarDatos():
    return 'Datos Actualizados'

@app.route('/servicio1_xml', methods=['POST'])
def servicio1_xml():
    if not request.files:
        return 'No se encontró el archivo', 400

    xml_file = next(iter(request.files.values()))

    try:
        processor = XMLProcessor(xml_file)  # Crea una instancia de XMLProcessor con el archivo XML
        data = processor.process_xml()  # Procesa el archivo XML utilizando el método process_xml
        return f"Archivo XML procesado y almacenado: {data}", 200

    except Exception as e:
        return f"Error al procesar el archivo XML: {e}", 400

@app.route('/servicio2_xml', methods=['POST'])
def servicio2_xml():
    if not request.files:
        return 'No se encontró el archivo', 400
    
    xml_file = next(iter(request.files.values()))
    
    if xml_file.filename == '':
        return 'No se seleccionó ningún archivo', 400

    if xml_file and xml_file.filename.lower().endswith('.xml'):
        xml_content = xml_file.read().decode('utf-8')
        processor = MessageProcessor()
        processor.process_messages(xml_content)
        return 'Archivo XML procesado correctamente', 200
    else:
        return 'Archivo no válido. Por favor, suba un archivo XML.', 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
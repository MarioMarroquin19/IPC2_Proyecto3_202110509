from flask import Flask, make_response
from flask_cors import CORS
#importar jsonfy para convertir a json
from flask import jsonify
import xml.etree.ElementTree as ET


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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
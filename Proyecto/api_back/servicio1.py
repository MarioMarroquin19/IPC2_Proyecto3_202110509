import xml.etree.ElementTree as ET
import xml.dom.minidom
import re


def prettify(element):
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    # Elimina líneas en blanco adicionales
    pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
    
    # Agrega un espacio en blanco entre las etiquetas vacías
    pretty_xml = re.sub(r'<(\w+)/>', r'<\1></\1>', pretty_xml)

    return pretty_xml


class XMLProcessor:
    def __init__(self, xml_file):
        self.xml_data = ET.parse(xml_file)
        self.root = self.xml_data.getroot()
        self.data = {}

    def parse_profiles(self, element):
        profiles = {}
        for profile in element.findall('perfil'):
            name = profile.find('nombre').text
            keywords = [keyword.text for keyword in profile.findall('palabrasClave/palabra')]
            profiles[name] = keywords
        return profiles

    def parse_discarded_words(self, element):
        return [word.text for word in element.findall('palabra')]

    def process_xml(xml_file):
    # Carga el archivo XML
        tree = ET.parse(xml_file)
        root = tree.getroot()

        data = {
            "perfiles": [],
            "descartadas": set()
        }

        for perfil in root.findall('perfiles/perfil'):
            nombre = perfil.find('nombre').text
            palabras_clave = [palabra.text for palabra in perfil.findall('palabrasClave/palabra')]
            data["perfiles"].append({"nombre": nombre, "palabrasClave": palabras_clave})

        for palabra in root.findall('descartadas/palabra'):
            data["descartadas"].add(palabra.text)

        # Devuelve las estructuras de datos procesadas como resultado de la función
        return data
    
    def add_baseDatos(data):
        tree = ET.parse('base1.xml')
        root = tree.getroot()

    # Procesa los perfiles y las palabras descartadas del archivo XML de entrada (data)
        perfiles_nuevos = 0
        perfiles_existentes = 0
        palabras_descartadas_nuevas = 0

        # Procesa los perfiles
        perfiles = root.find('perfiles')
        for perfil in data['perfiles']:
            nombre = perfil['nombre']
            palabras_clave = perfil['palabrasClave']

            # Busca si el perfil ya existe en la base de datos
            perfil_existente = perfiles.find(f"perfil[nombre='{nombre}']")

            if perfil_existente is not None:
                # El perfil ya existe, actualiza las palabras clave
                palabras_clave_existente = perfil_existente.find('palabrasClave')
                for palabra_clave in palabras_clave:
               
                    #verificar si la palabra clave ya existe y si no existe agregarla
                    if not any(p.text == palabra_clave for p in palabras_clave_existente.findall('palabra')):     
                        ET.SubElement(palabras_clave_existente, 'palabra').text = palabra_clave
                        perfiles_existentes += 1
            else:
                # El perfil no existe, crea un nuevo perfil y añade las palabras clave
                nuevo_perfil = ET.SubElement(perfiles, 'perfil')
                ET.SubElement(nuevo_perfil, 'nombre').text = nombre
                palabras_clave_nuevo = ET.SubElement(nuevo_perfil, 'palabrasClave')
                for palabra_clave in palabras_clave:
                    ET.SubElement(palabras_clave_nuevo, 'palabra').text = palabra_clave
                perfiles_nuevos += 1

        # Procesa las palabras descartadas
        descartadas = root.find('descartadas')
        for palabra in data['descartadas']:
            if not any(p.text == palabra for p in descartadas.findall('palabra')):
                ET.SubElement(descartadas, 'palabra').text = palabra
                palabras_descartadas_nuevas += 1

        # Guarda el archivo XML sin el perfil vacío
        #tree.write('base1.xml',encoding='utf-8', xml_declaration=True)
        with open('base1.xml', 'wb') as f:
            f.write(prettify(root).encode('utf-8'))

        # Devuelve un mensaje con el resumen de los cambios
        return f"""<?xml version="1.0"?>
                <respuesta>
                   <perfilesNuevos>
                     Se han creado {perfiles_nuevos} perfiles nuevos
                   </perfilesNuevos>
                   <perfilesExistentes>
                     Se han actualizado {perfiles_existentes} perfiles existentes
                   </perfilesExistentes>
                   <descartadas>
                     Se han creado {palabras_descartadas_nuevas} nuevas palabras a descartar
                   </descartadas>
                </respuesta>"""
    
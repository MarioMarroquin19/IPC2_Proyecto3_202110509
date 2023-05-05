import re
import xml.etree.ElementTree as ET
import xml.dom.minidom
import datetime

def prettify(element):
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

respuesta = ""

class MessageProcessor:
    def __init__(self):
        self.lugar_fecha_pattern = r'Lugar y Fecha: ([^,]+), (\d{2}/\d{2}/\d{4} \d{2}:\d{2})'
        self.usuario_pattern = r'Usuario: (.*?)\s*$' 
        self.red_social_pattern = r'Red social: (\w+)'
        #self.configuracionMensaje('base1.xml')
        self.respuesta = ""

    def validarUsuario(self, username):
        if ' ' in username or '\t' in username or '\n' in username:
            return False
        return True
    
    def extract_message_info(self, text):
        lines = text.split('\n')
        lugar_fecha_line = lines[0].strip()
        usuario_line = lines[1].strip()
        red_social_line = lines[2].strip()

        lugar_fecha_match = re.match(self.lugar_fecha_pattern, lugar_fecha_line)
        usuario_match = re.match(self.usuario_pattern, usuario_line)
        red_social_match = re.match(self.red_social_pattern, red_social_line)

        if lugar_fecha_match and usuario_match and red_social_match:
            lugar = lugar_fecha_match.group(1)
            fecha = lugar_fecha_match.group(2)
            usuario = usuario_match.group(1)
            red_social = red_social_match.group(1)

            contenido = '\n'.join(lines[3:]).strip()

            if not self.validarUsuario(usuario):  # Verifica si el usuario es válido
                return None
            
            return {
                'lugar': lugar,
                'fecha': fecha,
                'usuario': usuario,
                'red_social': red_social,
                'contenido': contenido,
            }
        else:
            return None

    def process_messages(self, xml_string):
        root = ET.fromstring(xml_string)
        user_set = set()
        message_count = 0
        processed_messages = []  # Lista para almacenar los mensajes procesados
        for mensaje in root.findall('mensaje'):
            message_text = mensaje.text.strip()
            message_info = self.extract_message_info(message_text)
            if message_info:
                user_set.add(message_info['usuario'])
                message_count += 1
                self.configuracionMensaje('base1.xml')
                processed_messages.append(self.ProcesarElementosXML(message_info))
            else:
                print('Información faltante en el mensaje')
        self.guardarXML(processed_messages)
        self.generarRespuesta(len(user_set), message_count)
        #ACÁ
        


    def ProcesarElementosXML(self, message_info):
        mensaje = ET.Element('mensaje')
        lugar_fecha = ET.SubElement(mensaje, 'lugar_fecha')
        lugar_fecha.text = f"{message_info['lugar']}, {message_info['fecha']}"
        usuario = ET.SubElement(mensaje, 'usuario')
        usuario.text = message_info['usuario']
        red_social = ET.SubElement(mensaje, 'red_social')
        red_social.text = message_info['red_social']
        #contenido = ET.SubElement(mensaje, 'contenido')
        msgAnalizado = self.quitarDescartadas_numeros(message_info['contenido'])
        #print(f'Mensaje analizado: {msgAnalizado}')  # Imprime el mensaje analizado
        profile_percentages = self.calculate_profile_percentages(msgAnalizado)
        contenido = ET.SubElement(mensaje, 'contenido')
        contenido.text = msgAnalizado

        perfiles_element = ET.SubElement(mensaje, 'perfiles')
        for profile, percentage in profile_percentages.items():
            perfil_element = ET.SubElement(perfiles_element, 'perfil')
            nombre_element = ET.SubElement(perfil_element, 'nombre')
            nombre_element.text = profile
            porcentaje_element = ET.SubElement(perfil_element, 'porcentaje')
            porcentaje_element.text = f"{percentage:.2f}%"
        #print(mensaje)
        return mensaje
    
    def cargarXML(self, archivo):
        try:
            tree = ET.parse(archivo)
            root = tree.getroot()
            return root
        except FileNotFoundError:
            return None


    def guardarXML(self, processed_messages):
        root = self.cargarXML('base2.xml')
        if root is None:
            mensajes_procesados = ET.Element('mensajes_procesados')
        else:
            mensajes_procesados = root

        # Agrega los nuevos mensajes procesados al elemento raíz existente o nuevo
        for mensaje in processed_messages:
            mensajes_procesados.append(mensaje)

        # Guarda el archivo XML actualizado
        xml_string = ET.tostring(mensajes_procesados, 'utf-8')
        pretty_xml_string = prettify(mensajes_procesados)
        with open('base2.xml', 'w', encoding='utf-8') as f:
            f.write(pretty_xml_string)

    def generarRespuesta(self, user_count, message_count):
        self.respuesta = ET.Element('respuesta')
        usuarios = ET.SubElement(self.respuesta, 'usuarios')
        usuarios.text = f'Se procesaron mensajes para {user_count} usuarios distintos'
        mensajes = ET.SubElement(self.respuesta, 'mensajes')
        mensajes.text = f'Se procesaron {message_count} mensajes en total'
        xml_string = ET.tostring(self.respuesta, encoding='unicode', method='xml')
        resp =  f"""<?xml version="1.0"?>
                        <respuesta>
                            <usuarios>
                                Se procesaron mensajes para {user_count} usuarios distintos
                            </usuarios>
                            <mensajes>
                                Se procesaron {message_count} mensajes en total
                            </mensajes>
                        </respuesta>"""
        self.respuesta = resp
    
    def regresarRespuesta(self):
        return self.respuesta
    
    #verificar perfiles y palabras claves y descartadas
    def configuracionMensaje(self, config_file):
        tree = ET.parse(config_file)
        root = tree.getroot()

        self.descartadas = set()
        for palabra in root.find('descartadas').findall('palabra'):
            if palabra.text:  # Verifica si la etiqueta <palabra> contiene texto
                self.descartadas.add(palabra.text.lower().strip())

        self.perfiles = {}
        for perfil in root.find('perfiles').findall('perfil'):
            nombre = perfil.find('nombre').text
            palabras_clave = set()
            for palabra in perfil.find('palabrasClave').findall('palabra'):
                if palabra.text:  # Verifica si la etiqueta <palabra> contiene texto
                    palabras_clave.add(palabra.text.lower().strip())
            self.perfiles[nombre] = palabras_clave

    def quitarDescartadas_numeros(self, text):
        for phrase in self.descartadas:
            text = re.sub(r'\b' + re.escape(phrase) + r'\b', '', text, flags=re.IGNORECASE)

        text = re.sub(r'\b\d+\b', '', text)  # Elimina números
        return text.strip()

    
    def calculate_profile_percentages(self, analyzed_message):
        total_phrases = 0
        profile_phrase_counts = {profile: 0 for profile in self.perfiles.keys()}

        for profile, keywords in self.perfiles.items():
            for phrase in keywords:
                count = len(re.findall(r'\b' + re.escape(phrase) + r'\b', analyzed_message, flags=re.IGNORECASE))
                profile_phrase_counts[profile] += count
                total_phrases += count

        # Cambia la forma en que se calculan los porcentajes de perfil
        total_words = len(re.findall(r'\w+', analyzed_message))
        profile_percentages = {
            profile: (phrase_count / total_words) * 100
            for profile, phrase_count in profile_phrase_counts.items()
        }

        return profile_percentages

    def procesarRespuesta(self, msj):
        root = ET.fromstring(msj)
        for mensaje in root.findall('mensaje'):
            message_text = mensaje.text.strip()
            return self.extract_info(message_text)

    def extract_info(self, text):        
        lines = text.split('\n')
        lugar_fecha_line = lines[0].strip()
        usuario_line = lines[1].strip()
        red_social_line = lines[2].strip()

        lugar_fecha_match = re.match(self.lugar_fecha_pattern, lugar_fecha_line)
        usuario_match = re.match(self.usuario_pattern, usuario_line)
        red_social_match = re.match(self.red_social_pattern, red_social_line)

        if lugar_fecha_match and usuario_match and red_social_match:
            lugar = lugar_fecha_match.group(1)
            fecha = lugar_fecha_match.group(2)
            usuario = usuario_match.group(1)
            red_social = red_social_match.group(1)

            contenido = '\n'.join(lines[3:]).strip()

            if not self.validarUsuario(usuario):  # Verifica si el usuario es válido
                return None
            
            return {
                'fecha': fecha,
                'usuario': usuario,
                'contenido': contenido,
            }
        else:
            return None
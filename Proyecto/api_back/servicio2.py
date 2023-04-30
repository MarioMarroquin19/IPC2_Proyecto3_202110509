import re
import xml.etree.ElementTree as ET
import xml.dom.minidom

def prettify(element):
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

respuesta = ""

class MessageProcessor:
    def __init__(self):
        self.lugar_fecha_pattern = r'Lugar y Fecha: ([^,]+), (\d{2}/\d{2}/\d{4} \d{2}:\d{2})'
        self.usuario_pattern = r'Usuario: (.*?)\s*$'  # Cambia esta línea
        self.red_social_pattern = r'Red social: (\w+)'

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
                processed_messages.append(self.ProcesarElementosXML(message_info))
            else:
                print('Información faltante en el mensaje')
        self.guardarXML(processed_messages)
        self.generarRespuesta(len(user_set), message_count)

    def ProcesarElementosXML(self, message_info):
        mensaje = ET.Element('mensaje')
        lugar_fecha = ET.SubElement(mensaje, 'lugar_fecha')
        lugar_fecha.text = f"{message_info['lugar']}, {message_info['fecha']}"
        usuario = ET.SubElement(mensaje, 'usuario')
        usuario.text = message_info['usuario']
        red_social = ET.SubElement(mensaje, 'red_social')
        red_social.text = message_info['red_social']
        contenido = ET.SubElement(mensaje, 'contenido')
        contenido.text = message_info['contenido']
        return mensaje
    
    def guardarXML(self, processed_messages):
        mensajes_procesados = ET.Element('mensajes_procesados')
        for mensaje in processed_messages:
            mensajes_procesados.append(mensaje)
        tree = ET.ElementTree(mensajes_procesados)
        tree.write('base2.xml', encoding='utf-8', xml_declaration=True)

    def generarRespuesta(self, user_count, message_count):
        global respuesta
        respuesta = ET.Element('respuesta')
        usuarios = ET.SubElement(respuesta, 'usuarios')
        usuarios.text = f'Se procesaron mensajes para {user_count} usuarios distintos'
        mensajes = ET.SubElement(respuesta, 'mensajes')
        mensajes.text = f'Se procesaron {message_count} mensajes en total'
        xml_string = ET.tostring(respuesta, encoding='unicode', method='xml')
        resp =  f"""<?xml version="1.0"?>
                        <respuesta>
                            <usuarios>
                                Se procesaron mensajes para {user_count} usuarios distintos
                            </usuarios>
                            <mensajes>
                                Se procesaron {message_count} mensajes en total
                            </mensajes>
                        </respuesta>"""
        respuesta = resp

        #print(xml_string)
    
    def regresarRespuesta(self):
        global respuesta
        return respuesta
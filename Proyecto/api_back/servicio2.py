import re
import xml.etree.ElementTree as ET

class MessageProcessor:
    def __init__(self):
        self.lugar_fecha_pattern = r'Lugar y Fecha: ([^,]+), (\d{2}/\d{2}/\d{4} \d{2}:\d{2})'
        self.usuario_pattern = r'Usuario: (\S+)'
        self.red_social_pattern = r'Red social: (\w+)'

    def extract_message_info(self, text):
        lugar_fecha_match = re.search(self.lugar_fecha_pattern, text)
        usuario_match = re.search(self.usuario_pattern, text)
        red_social_match = re.search(self.red_social_pattern, text)

        if lugar_fecha_match and usuario_match and red_social_match:
            lugar = lugar_fecha_match.group(1)
            fecha = lugar_fecha_match.group(2)
            usuario = usuario_match.group(1)
            red_social = red_social_match.group(1)

            return {
                'lugar': lugar,
                'fecha': fecha,
                'usuario': usuario,
                'red_social': red_social,
            }
        else:
            return None

    def process_messages(self, xml_string):
        root = ET.fromstring(xml_string)
        for mensaje in root.findall('mensaje'):
            message_text = mensaje.text.strip()
            message_info = self.extract_message_info(message_text)
            if message_info:
                print(message_info)
            else:
                print('Información faltante en el mensaje')

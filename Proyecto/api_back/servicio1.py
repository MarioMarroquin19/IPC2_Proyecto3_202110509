import xml.etree.ElementTree as ET

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

    def process_xml(self):
        self.data = {
            'perfiles': self.parse_profiles(self.root.find('perfiles')),
            'descartadas': self.parse_discarded_words(self.root.find('descartadas')),
        }

        return self.data
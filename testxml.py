from elementtree import ElementTree as ET


with open('mqpar.xml') as f:
		tree = ET.parse(f)
		root = getroot()
		
		for elem in root.iter('string name="file1"'):
			elem.text = 'NEW TEXT'

tree.write('mqpar_batch1.xml', xml_declaration=True, method='xml', encoding='UTF-8')

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LAParams

FILE = "BL05012022.pdf"
# FILE = "http://www.tfca.gob.mx/work/models/TFCA/Resource/81/2/images/BL04012022.pdf"
                      
Fecha = []
Juzgado = []
Expediente = []
Actor = []
Demandado = []
Acuerdos = []

Juzgado_start = None # Juzgado flag. If this flag is True, new record start
Exp_start = True # Expediente flag

_LA_PARAMS = LAParams(line_margin=0.0000001)
pages_list = []
# for page_layout in extract_pages(FILE, laparams=_LA_PARAMS):
for page_layout in extract_pages(FILE,'', [0], laparams=_LA_PARAMS):
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            elText = element.get_text()
            if elText.startswith('Página'):
                print(elText[6:])
                pages_list.append(elText[7:-2])
                
                
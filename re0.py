from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LAParams

FILE = "Repair_Order_132435_RedactedClaim01182022_122540.pdf"
# FILE = "http://www.tfca.gob.mx/work/models/TFCA/Resource/81/2/images/BL04012022.pdf"
                      
_LA_PARAMS = LAParams(line_margin=0.0000001)

for page_layout in extract_pages(FILE, laparams=_LA_PARAMS):
# for page_layout in extract_pages(FILE,'', [7], laparams=_LA_PARAMS):
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            elText = element.get_text()
            with open('re.txt', 'a', encoding='UTF-8', newline='') as file:
                file.write(str(element))
                
            for text_line in element:
                # print(text_line)
                for character in text_line:
                    if isinstance(character, LTChar):
                        with open('re.txt', 'a', encoding='UTF-8',) as file:
                            file.write('character = ' + str(character) + ' :size = ' + str(character.size) + '\n')
                            
                            
        


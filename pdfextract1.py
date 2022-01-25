from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LAParams
import json
import datetime

FILE = "BL05012022.pdf"
                      
Fecha = []
Juzgado = ''
Expediente = []
Actor = []
Demandado = []
Acuerdos = []

Juzgado_start = None # Juzgado flag. If this flag is True, new record start
Exp_start = True # Expediente flag

_LA_PARAMS = LAParams(line_margin=0.0000001)

FECHA_FONTSIZE = 10
FECHA_FONTNAME = 'ABCDEE+Eras Medium ITC'
JUZGADO_FONTSIZE = 16
JUZGADO_FONTNAME = 'ABCDEE+Copperplate Gothic Bold'
AMPAROS_FONTSIZE = 10
AMPAROS_FONTNAME = 'ABCDEE+Franklin Gothic Medium'
AUDIENCIAS_FONTSIZE = 10
AUDIENCIAS_FONTNAME = 'ABCDEE+Franklin Gothic Medium'

recordIndex = [] ## check the record number and y-coordinate of each record.
data_json = []
c, d, e, f = [], [], [], []
def complex_list_sort(c):    
    yCoord = []
    cc = []
    for cItem in c:
        yCoord.append(cItem['y'])
    
    yCoord.sort(reverse = True)
    
    for y in yCoord:
        for cItem in c:
            if y == cItem['y']:
                cc.append(cItem)
                break
    return cc

def get_result(recordIndex, c, key):
    result = []
    item = ''
    if len(recordIndex) == len(c):
        result.append('')
        for cc in c:
            result.append(cc['text'])
    else:
        ## In order to get information breaken by page breaks
        y0 = recordIndex[0]['y']
        for cc in c:        
            if y0 < round(cc['y'], 3):
                print(cc['text'])
                print(data_json[-1][key])
                data_json[-1][key] += cc['text']
                print(data_json[-1][key])
            else:
                break    
        ## Get by recordIndex
        for r in recordIndex:
            while r['y'] < round(c[0]['y'],3):
                item += c[0]['text']
                c.pop(0)
            else:
                if r['y'] == round(c[0]['y'],3):
                    result.append(item)
                    item = c[0]['text']
                    c.pop(0)

        if c:
            last_item = item
            while c:
                last_item += c[0]['text']
                c.pop(0)
            result.append(last_item)            
        else:
            result.append(item)
    return result

# create natural sequence list
def createList(r1, r2):
    if (r1 == r2):
        return [r1]
    else:
        res = []  
        while(r1 < r2+1 ):              
            res.append(r1)
            r1 += 1
        return res
    
def create_dic(recordIndex,b,c,d,e,f):
    i = 0
    for r in recordIndex:
        i += 1
        dic = {
            "actor" : d[i].upper(),
            "demandado" : e[i].upper(),
            "entidad" : 'CIUDAD DE MEXICO',
            "expediente" :c[i].upper(),
            "fecha" : Fecha[0].upper(),
            "fuero" : 'FEDERAL',
            "juzgado" : Juzgado.upper(),
            "tipo" : '',
            "acuerdos" : f[i].upper() if f else '',
            "monto": '',
            "fecha_presentacion": '',
            "actos_reclamados": '',
            "actos_reclamados_especificos": '',
            "Naturaleza_procedimiento": '',
            "Prestación_demandada": '',
            "Organo_jurisdiccional_origen": '',
            "expediente_origen": b[i].upper() if b else '',
            "materia": 'LABORAL',
            "submateria": '',
            "fecha_sentencia": '',
            "sentido_sentencia": '',
            "resoluciones": '',
            "origen": 'TRIBUNAL FEDERAL DE CONCILIACION Y ARBITRAJE',
            "Fecha insercion": str(datetime.datetime.now()),
        }
        data_json.append(dic)
        
page_number = 0

pages_list = []
# get page index list in 0 page:
for page_layout in extract_pages(FILE,'', [0], laparams=_LA_PARAMS):
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            elText = element.get_text()
            if elText.startswith('Página'):
                print(elText[6:])
                pages_list.append(elText[7:-2])
                
######################################
## P R I M E R A     Start
######################################
for page_layout in extract_pages(FILE, laparams=_LA_PARAMS):
# for page_layout in extract_pages(FILE,'', [9], laparams=_LA_PARAMS):
    page_number += 1
    if page_number > 2 and Juzgado_start != 2: ## Juz_start
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                elText = element.get_text()
                ## check the record number and y-coordinate of each record.
                if (elText == '1 \n' or elText == '2 \n' or elText == '3 \n') and round(element.bbox[0]) == 566:
                    recordIndex.append({'y': round(element.bbox[1],3)})
                elif element.bbox[0] == 41.400:
                    c.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText})
                elif round(element.bbox[0]) == 98:
                    d.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText})
                elif round(element.bbox[0]) == 254:
                    e.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText})
                elif round(element.bbox[0]) == 410:
                    f.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText})
                
                for text_line in element:
                    for character in text_line:
                        if isinstance(character, LTChar):                            
                            ## find out losted record (c and d)
                            if round(character.bbox[0]) == 98 and element.bbox[0] == 41.400:
                                print(elText)
                                temp = ''
                                for cha in text_line:
                                    if type(cha) == LTChar:
                                        if cha.bbox[0] >= character.bbox[0]:
                                            temp += cha._text
                                
                                c = c[:-1]
                                c.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                d.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp + '\n'})
                                break
                            
                            ## find out losted record (d and e)
                            elif round(character.bbox[0]) == 254 and round(element.bbox[0]) == 98:
                                print(elText)
                                temp = ''
                                for cha in text_line:
                                    if type(cha) == LTChar:
                                        if cha.bbox[0] >= character.bbox[0]:
                                            temp += cha._text
                                
                                d = d[:-1]
                                d.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                e.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp + '\n'})
                                break
                              
                            ## find out losted record (e and f)
                            elif round(character.bbox[0]) == 410 and round(element.bbox[0]) == 254:
                                print(elText)
                                temp = ''
                                for cha in text_line:
                                    if type(cha) == LTChar:
                                        if cha.bbox[0] >= character.bbox[0]:
                                            temp += cha._text
                                
                                e = e[:-1]
                                e.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                f.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp + '\n'})
                                break
                            
                            ## find out losted record (f and recordIndex)
                            elif round(character.bbox[0]) == 566 and round(element.bbox[0]) == 410:
                                print(elText)
                                temp = ''
                                for cha in text_line:
                                    if type(cha) == LTChar:
                                        if cha.bbox[0] >= character.bbox[0]:
                                            temp += cha._text
                                
                                f = f[:-1]
                                f.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                recordIndex.append({'y': round(element.bbox[1],3)})
                                break
                            
                            elif round(character.size) ==  FECHA_FONTSIZE and character.fontname == FECHA_FONTNAME:
                                Fecha.append(elText)
                                break
                            elif round(character.size) ==  JUZGADO_FONTSIZE and character.fontname == JUZGADO_FONTNAME:
                                if elText.startswith('P R I M E R A')>0:
                                    Juzgado_start = 1
                                    Juzgado = elText.replace(' ', '')
                                    break
                            elif round(character.size) ==  10 and character.fontname == 'ABCDEE+Franklin Gothic Medium':
                                if elText.startswith('ACUERDOS DICTADOS EN AUDIENCIAS CELEBRADAS EL')>0:
                                    Juzgado_start = 2
                                    break
        
        if len(recordIndex) > 0:
            ## sort mixed list
            c = complex_list_sort(c)
            d = complex_list_sort(d)
            e = complex_list_sort(e)
            f = complex_list_sort(f)
            recordIndex = complex_list_sort(recordIndex)
        
            c_result = get_result(recordIndex, c, 'expediente')
            d_result = get_result(recordIndex, d, 'actor')
            e_result = get_result(recordIndex, e, 'demandado')
            f_result = get_result(recordIndex, f, 'acuerdos')
            
            create_dic(recordIndex, None, c_result, d_result, e_result, f_result)
            
        c, d, e, f = [], [], [], []
        recordIndex = []
    elif Juzgado_start  == 2:
        break
##########################################################
## ACUERDOS DICTADOS EN AUDIENCIAS CELEBRADAS EL     Start
##########################################################
acuerdos_page_number = page_number - 2
page_number = 0
for page_layout in extract_pages(FILE, laparams=_LA_PARAMS):
    page_number += 1
    if page_number > acuerdos_page_number: ## acuerdos_start
        for element in page_layout:
            if Juzgado_start == 3:                
                break
            if isinstance(element, LTTextContainer):
                elText = element.get_text()
                
                ## check the record number and y-coordinate of each record.
                if round(element.bbox[0]) == 36:
                    recordIndex.append({'y': round(element.bbox[1],3)})
                    c.append({'x': round(element.bbox[0]), 'y':element.bbox[1], 'text':elText})
                elif round(element.bbox[0]) == 91:
                    d.append({'x': round(element.bbox[0]), 'y':element.bbox[1], 'text':elText})
                elif round(element.bbox[0]) == 332:
                    e.append({'x': round(element.bbox[0]), 'y':element.bbox[1], 'text':elText})
                
                for text_line in element:                    
                    for character in text_line:
                        if isinstance(character, LTChar):                            
                            ## find out losted record (c and d)
                            if round(character.bbox[0]) == 91 and round(element.bbox[0]) == 36:
                                print(elText)
                                temp = ''
                                for cha in text_line:
                                    if type(cha) == LTChar:
                                        if cha.bbox[0] >= character.bbox[0]:
                                            temp += cha._text
                                
                                c = c[:-1]
                                c.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                d.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp + '\n'})
                                break
                            
                            ## find out losted record (d and e)
                            elif round(character.bbox[0]) == 332 and round(element.bbox[0]) == 91:
                                print(elText)
                                temp = ''
                                for cha in text_line:
                                    if type(cha) == LTChar:
                                        if cha.bbox[0] >= character.bbox[0]:
                                            temp += cha._text
                                
                                d = d[:-1]
                                d.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                e.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp + '\n'})
                                break
                                                     
                            elif round(character.size) ==  FECHA_FONTSIZE and character.fontname == FECHA_FONTNAME:
                                Fecha.append(elText)
                                break
                            elif round(character.size) ==  10 and character.fontname == 'ABCDEE+Franklin Gothic Medium':
                                if elText.startswith('ACUERDOS DICTADOS EN AUDIENCIAS CELEBRADAS EL')>0:
                                    f_result = elText
                                    Juzgado_start = 2
                                    c, d, e = [], [], []
                                    recordIndex = []
                                    break
                                elif elText.startswith('AUDIENCIAS PROGRAMADAS')>0:
                                    Juzgado_start = 3
                                    break
        
        if len(recordIndex) > 0:
            ## sort mixed list
            c = complex_list_sort(c)
            d = complex_list_sort(d)
            e = complex_list_sort(e)
            recordIndex = complex_list_sort(recordIndex)
        
            c_result = get_result(recordIndex, c, 'expediente')
            d_result = get_result(recordIndex, d, 'actor')
            e_result = get_result(recordIndex, e, 'demandado')
            
            create_dic(recordIndex, None, c_result, d_result, e_result, None)

        c, d, e = [], [], []
        recordIndex = []
        
        if Juzgado_start == 3:
            break

###################################
## AUDIENCIAS PROGRAMADAS     Start
###################################
audiencias_page_number = page_number - 1
page_number = 0
for page_layout in extract_pages(FILE, laparams=_LA_PARAMS):
    page_number += 1
    if page_number > audiencias_page_number: ## audiencias_start
        for element in page_layout:
            if Juzgado_start == 4:                
                break
            if isinstance(element, LTTextContainer):
                elText = element.get_text()
                
                ## check the record number and y-coordinate of each record.
                if round(element.bbox[0]) == 77:
                    recordIndex.append({'y': round(element.bbox[1])})
                    c.append({'x': round(element.bbox[0]), 'y':element.bbox[1], 'text':elText})
                elif round(element.bbox[0], 1) == 126.5:
                    d.append({'x': round(element.bbox[0],1), 'y':element.bbox[1], 'text':elText})
                elif round(element.bbox[0], 2) == 353.35:
                    e.append({'x': round(element.bbox[0],2), 'y':element.bbox[1], 'text':elText})
                
                for text_line in element:                    
                    for character in text_line:
                        if isinstance(character, LTChar):
                            
                            ## find out losted record (xx and c)
                            if round(character.bbox[0]) == 77 and round(element.bbox[0],1) == 41.4:
                                print(elText)
                                temp, temp1 = '', ''
                                for cha in text_line:
                                    if type(cha) == LTChar:
                                        if cha.bbox[0] >= character.bbox[0]:
                                            temp += cha._text
                                        if round(cha.bbox[0],1) >= 126.5:
                                            temp1 += cha._text
                                recordIndex.append({'y': round(element.bbox[1])})
                                if temp1 == '':
                                    c.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp + '\n'})
                                else:
                                    c.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp.split(temp1)[0] + '\n'})
                                    d.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp1 + '\n'})
                                
                            ## find out losted record (c and d)
                            if round(character.bbox[0],1) == 126.5 and round(element.bbox[0]) == 77:
                                print(elText)
                                temp = ''
                                for cha in text_line:
                                    if type(cha) == LTChar:
                                        if cha.bbox[0] >= character.bbox[0]:
                                            temp += cha._text
                                
                                c = c[:-1]
                                c.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                d.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp + '\n'})
                                break
                                
                            ## find out losted record (d and e)
                            elif round(character.bbox[0],2) == 353.35 and round(element.bbox[0],1) == 126.5:
                                print(elText)
                                temp = ''
                                for cha in text_line:
                                    if type(cha) == LTChar:
                                        if cha.bbox[0] >= character.bbox[0]:
                                            temp += cha._text
                                
                                d = d[:-1]
                                d.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                e.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp + '\n'})
                                break
                                                      
                            elif round(character.size) ==  FECHA_FONTSIZE and character.fontname == FECHA_FONTNAME:
                                Fecha.append(elText)
                                break
                            elif round(character.size) ==  10 and character.fontname == 'ABCDEE+Franklin Gothic Medium':
                                if elText.startswith('AUDIENCIAS PROGRAMADAS')>0:
                                    f_result = elText
                                    Juzgado_start = 3
                                    c, d, e = [], [], []
                                    recordIndex = []
                                    break
                            elif round(character.size) ==  JUZGADO_FONTSIZE and character.fontname == JUZGADO_FONTNAME:
                                if elText.startswith('S E G U N D A')>0:
                                    Juzgado_start = 4
                                    # Juzgado = elText.replace(' ', '')
                                    break
        
        if len(recordIndex) > 0:
            ## sort mixed list
            c = complex_list_sort(c)
            d = complex_list_sort(d)
            e = complex_list_sort(e)
            recordIndex = complex_list_sort(recordIndex)
        
            c_result = get_result(recordIndex, c, 'expediente')
            d_result = get_result(recordIndex, d, 'actor')
            e_result = get_result(recordIndex, e, 'demandado')
            
            create_dic(recordIndex, None, c_result, d_result, e_result, None)

        c, d, e = [], [], []
        recordIndex = []
        
        if Juzgado_start == 4:
            break
               
######################################
## S E G U N D A     Start
######################################
segunda_page_number = page_number - 1
page_number = 0
for page_layout in extract_pages(FILE, laparams=_LA_PARAMS):
    page_number += 1
    if page_number > segunda_page_number: ## Seg_start
        for element in page_layout:
            if Juzgado_start == 5:                
                break
            if isinstance(element, LTTextContainer):
                elText = element.get_text()
                
                ## check the record number and y-coordinate of each record.
                if (elText == '1 \n' or elText == '2 \n' or elText == '3 \n') and round(element.bbox[0]) == 566:
                    recordIndex.append({'y': round(element.bbox[1],3)})
                    
                elif element.bbox[0] == 41.400:
                    c.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText})
                elif round(element.bbox[0]) == 98:
                    d.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText})
                elif round(element.bbox[0]) == 233:
                    e.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText})
                elif round(element.bbox[0]) == 431:
                    f.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText})
                
                for text_line in element:
                    for character in text_line:
                        if isinstance(character, LTChar):
                            ## find out losted record (c and d)
                            if round(character.bbox[0]) == 98 and element.bbox[0] == 41.400:
                                print(elText)
                                temp = ''
                                for cha in text_line:
                                    if type(cha) == LTChar:
                                        if cha.bbox[0] >= character.bbox[0]:
                                            temp += cha._text
                                
                                c = c[:-1]
                                c.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                d.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp + '\n'})
                                break
                            
                            ## find out losted record (d and e)
                            elif round(character.bbox[0]) == 233 and round(element.bbox[0]) == 98:
                                print(elText)
                                temp = ''
                                for cha in text_line:
                                    if type(cha) == LTChar:
                                        if cha.bbox[0] >= character.bbox[0]:
                                            temp += cha._text
                                
                                d = d[:-1]
                                d.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                e.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp + '\n'})
                                break
                            
                            ## find out losted record (e and xx)
                            elif round(character.bbox[0], 1) == 367.5 and round(element.bbox[0]) == 233:
                                print(elText)
                                temp = ''
                                for cha in text_line:
                                    if type(cha) == LTChar:
                                        if cha.bbox[0] >= character.bbox[0]:
                                            temp += cha._text
                                
                                e = e[:-1]
                                e.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                break
                                
                            ## find out losted record (xx and f)
                            elif round(character.bbox[0]) == 431 and round(element.bbox[0], 1) == 367.5:
                                print(elText)
                                temp = ''
                                for cha in text_line:
                                    if type(cha) == LTChar:
                                        if cha.bbox[0] >= character.bbox[0]:
                                            temp += cha._text
                                
                                f.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp + '\n'})
                                break
                            
                            ## find out losted record (f and recordIndex)
                            elif round(character.bbox[0]) == 566 and round(element.bbox[0]) == 431:
                                print(elText)
                                temp = ''
                                for cha in text_line:
                                    if type(cha) == LTChar:
                                        if cha.bbox[0] >= character.bbox[0]:
                                            temp += cha._text
                                
                                f = f[:-1]
                                f.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                recordIndex.append({'y': round(element.bbox[1],3)})
                                break
                            
                            elif round(character.size) ==  JUZGADO_FONTSIZE and character.fontname == JUZGADO_FONTNAME:
                                if elText.startswith('S E G U N D A')>0:
                                    Juzgado_start = 4
                                    c, d, e, f = [], [], [], []
                                    recordIndex = []
                                    Juzgado = elText.replace(' ', '')
                                    break
                            elif round(character.size) ==  AMPAROS_FONTSIZE and character.fontname == AMPAROS_FONTNAME:
                                Fecha.append(elText)
                                if elText.startswith('AMPAROS')>0:
                                    Juzgado_start = 5
                                    break
        if len(recordIndex) > 0:                    
            ## sort mixed list
            c = complex_list_sort(c)
            d = complex_list_sort(d)
            e = complex_list_sort(e)
            f = complex_list_sort(f)
            recordIndex = complex_list_sort(recordIndex)

            c_result = get_result(recordIndex, c, 'expediente')
            d_result = get_result(recordIndex, d, 'actor')
            e_result = get_result(recordIndex, e, 'demandado')
            f_result = get_result(recordIndex, f, 'acuerdos')
            
            create_dic(recordIndex, None, c_result, d_result, e_result, f_result)

        c, d, e, f = [], [], [], []
        recordIndex = []
        
        if Juzgado_start == 5:
            break

######################################
## AMPAROS     Start
######################################
AMPAROS_page_number = page_number - 1
page_number = 0
b = []
for page_layout in extract_pages(FILE, laparams=_LA_PARAMS):
    page_number += 1
    if page_number > AMPAROS_page_number: ## AMPAROS_start
        for element in page_layout:
            if Juzgado_start == 6: 
                break
                                
            
            if isinstance(element, LTTextContainer):
                elText = element.get_text()                    
                ## check the record number and y-coordinate of each record.
                if (elText == '1 \n' or elText == '2 \n' or elText == '3 \n') and round(element.bbox[0], 2) == 565.44:
                    recordIndex.append({'y': round(element.bbox[1],3)})
                    
                elif element.bbox[0] == 41.400:
                    b.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText})
                elif round(element.bbox[0], 1) == 103.6:
                    c.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText})
                elif round(element.bbox[0], 1) == 168.5:
                    d.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText})
                elif round(element.bbox[0]) == 303:
                    e.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText})
                elif round(element.bbox[0]) == 438:
                    f.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText})
                
                for text_line in element:
                        for character in text_line:
                            if isinstance(character, LTChar):                                
                                ## find out losted record (b and c)
                                if round(character.bbox[0], 1) == 103.6 and element.bbox[0] == 41.400:
                                    print(elText)
                                    temp = ''
                                    for cha in text_line:
                                        if type(cha) == LTChar:
                                            if cha.bbox[0] >= character.bbox[0]:
                                                temp += cha._text
                                    
                                    b = b[:-1]
                                    b.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                    c.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp + '\n'})
                                    break
                                
                                ## find out losted record (c and d)
                                elif round(character.bbox[0], 1) == 168.5 and round(element.bbox[0], 1) == 103.6:
                                    print(elText)
                                    temp = ''
                                    for cha in text_line:
                                        if type(cha) == LTChar:
                                            if cha.bbox[0] >= character.bbox[0]:
                                                temp += cha._text
                                    
                                    c = c[:-1]
                                    c.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                    d.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp + '\n'})
                                    break
                                    
                                ## find out losted record (d and e)
                                elif round(character.bbox[0]) == 303 and round(element.bbox[0], 1) == 168.5:
                                    print(elText)
                                    temp = ''
                                    for cha in text_line:
                                        if type(cha) == LTChar:
                                            if cha.bbox[0] >= character.bbox[0]:
                                                temp += cha._text
                                    
                                    d = d[:-1]
                                    d.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                    e.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp + '\n'})
                                    break
                                
                                ## find out losted record (e and f)
                                elif round(character.bbox[0], 1) == 438 and round(element.bbox[0]) == 303:
                                    print(elText)
                                    temp = ''
                                    for cha in text_line:
                                        if type(cha) == LTChar:
                                            if cha.bbox[0] >= character.bbox[0]:
                                                temp += cha._text
                                    
                                    e = e[:-1]
                                    e.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                    f.append({'x': character.bbox[0], 'y':element.bbox[1], 'text':temp + '\n'})
                                    break
                                
                                ## find out losted record (f and recordIndex)
                                elif round(character.bbox[0]) == 566 and round(element.bbox[0]) == 438:
                                    print(elText)
                                    temp = ''
                                    for cha in text_line:
                                        if type(cha) == LTChar:
                                            if cha.bbox[0] >= character.bbox[0]:
                                                temp += cha._text
                                    
                                    f = f[:-1]
                                    f.append({'x': element.bbox[0], 'y':element.bbox[1], 'text':elText.split(temp)[0] + '\n'})
                                    recordIndex.append({'y': round(element.bbox[1],3)})
                                    break
                                
                                elif round(character.size) ==  AMPAROS_FONTSIZE and character.fontname == AMPAROS_FONTNAME:
                                    Fecha.append(elText)
                                    if elText.startswith('AMPAROS')>0:
                                        Juzgado_start = 5
                                        b,c,d,e,f = [],[],[],[],[]
                                        recordIndex = []
                                        break
                                    
                                elif round(character.size) ==  12 and character.fontname == 'ABCDEE+Eras Medium ITC':
                                    Juzgado_start = 6
                                    break
        if len(recordIndex) > 0:                    
            ## sort mixed list
            b = complex_list_sort(b)
            c = complex_list_sort(c)
            d = complex_list_sort(d)
            e = complex_list_sort(e)
            f = complex_list_sort(f)
            recordIndex = complex_list_sort(recordIndex)

            b_result = get_result(recordIndex, b, 'expediente')
            c_result = get_result(recordIndex, c, 'expediente_origen')
            d_result = get_result(recordIndex, d, 'actor')
            e_result = get_result(recordIndex, e, 'demandado')
            f_result = get_result(recordIndex, f, 'acuerdos')
            
            create_dic(recordIndex, c_result, b_result, d_result, e_result, f_result)
            
        b, c, d, e, f = [], [], [], [], []
        recordIndex = []
        
        if Juzgado_start == 6:
            break

                               
json_object = json.dumps(data_json)

# Writing to sample.json
with open("sample.json", "w") as outfile:
    outfile.write(json_object)
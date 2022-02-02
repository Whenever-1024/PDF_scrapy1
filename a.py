from email import header
import re
import mysql.connector
from mysql.connector import errorcode
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LAParams
import json
import datetime

FILE = "BL05012022.pdf"
# FILE = "BL04102021.pdf"
_LA_PARAMS = LAParams(line_margin=0.0000001)

Fecha, Juzgado = '', ''
headers, rest = [], []
recordIndex = [] ## check the record number and y-coordinate of each record.
data_json = []

def complex_list_sort(c):    
    yCoord, cc = [], []
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
            "fecha" : Fecha,
            "fuero" : 'FEDERAL',
            "juzgado" : Juzgado,
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
            "Fecha insercion": datetime.datetime.now().strftime("%d/%m/%Y"),
        }
        data_json.append(dic)

def record0000(e, i, l, content):
    if len(e) == 4:
        sql = "INSERT INTO `%s` SET `'y'`=%s, `%s`=%s"
        cursor.execute(sql, (i+1000, l[2], content[0], l[3]))
    elif len(e) == 5:
        sql = "INSERT INTO `%s` SET `'y'`=%s, `%s`=%s, `%s`=%s"
        cursor.execute(sql, (i+1000, l[2], content[0], l[3], content[1], l[4]))
    elif len(e) == 6:
        sql = "INSERT INTO `%s` SET `'y'`=%s, `%s`=%s, `%s`=%s, `%s`=%s"
        cursor.execute(sql, (i+1000, l[2], content[0], l[3], content[1], l[4], content[2], l[5]))
    elif len(e) == 7:
        sql = "INSERT INTO `%s` SET `'y'`=%s, `%s`=%s, `%s`=%s, `%s`=%s, `%s`=%s"
        cursor.execute(sql, (i+1000, l[2], content[0], l[3], content[1], l[4], content[2], l[5], content[3], l[6]))
    elif len(e) == 8:
        sql = "INSERT INTO `%s` SET `'y'`=%s, `%s`=%s, `%s`=%s, `%s`=%s, `%s`=%s, `%s`=%s"
        cursor.execute(sql, (i+1000, l[2], content[0], l[3], content[1], l[4], content[2], l[5], content[3], l[6], content[4], l[7]))
    elif len(e) == 9:
        sql = "INSERT INTO `%s` SET `'y'`=%s, `%s`=%s, `%s`=%s, `%s`=%s, `%s`=%s, `%s`=%s, `%s`=%s"
        cursor.execute(sql, (i+1000, l[2], content[0], l[3], content[1], l[4], content[2], l[5], content[3], l[6], content[4], l[7], content[5], l[8]))
    elif len(e) == 10:
        sql = "INSERT INTO `%s` SET `'y'`=%s, `%s`=%s, `%s`=%s, `%s`=%s, `%s`=%s, `%s`=%s, `%s`=%s, `%s`=%s"
        cursor.execute(sql, (i+1000, l[2], content[0], l[3], content[1], l[4], content[2], l[5], content[3], l[6], content[4], l[7], content[5], l[8], content[6], l[9]))
    cnx.commit()
    
cnx = mysql.connector.connect(user='root', database='mydatabase')
cursor = cnx.cursor()
# '''
############################################
## delete all the records on all the tables.
############################################``
sql = ("DELETE FROM headers WHERE 1")
cursor.execute(sql)
cnx.commit()
sql = ("DELETE FROM contentofheaders WHERE 1")
cursor.execute(sql)
cnx.commit()

sql = ("DELETE FROM juzgado WHERE 1")
cursor.execute(sql)
cnx.commit()
sql = ("DELETE FROM elements WHERE 1")
cursor.execute(sql)
cnx.commit()
#######################################
## Create headers and all the elements.
#######################################
hearderNo, pageNo = 0, 0
# a_x, b_x, c_x, b_x, e_x = 41, 98, 254, 410, 566 # default x of table with 5 fields
for page_layout in extract_pages(FILE, laparams=_LA_PARAMS):
    pageNo += 1
    if pageNo < 3:
        continue
    samepage_headers = []
    for element in page_layout:
        first_field = True
        insert_otherfield = False
        if isinstance(element, LTTextContainer):
            elText = element.get_text()
            print(elText)
            x = round(element.bbox[0])
            y = round(element.bbox[1])
            # filling headers field
            if (elText == 'EXP/LAB \n' or elText == 'HORA \n' or elText == 'AMP/NO \n') and x < 55:
                # if not first field,
                for h in samepage_headers:
                    if y == h['y']:
                        headers[h['No']]['header'].insert(0, {'x': x, 'text': elText[:-2]})
                        first_field = False
                        break
                # if first field
                if first_field == True:
                    headers.append({'No': hearderNo, 'page': pageNo, 'y': y, 'header': [{'x': x, 'text': elText[:-2]}]})
                    samepage_headers.append({'No': hearderNo, 'y': y, 'header': [elText[:-2]]})
                    hearderNo += 1
                continue
            # filling other field
            for h in samepage_headers:
                if y == h['y']:
                    headers[h['No']]['header'].append({'x': x, 'text': elText[:-2]})
                    insert_otherfield = True
                    break
            # if 'Actor' or 'demandado' values appear first              
            if insert_otherfield == False and (elText == 'ACTOR \n'):
                headers.append({'No': hearderNo, 'page': pageNo, 'y': y, 'header': [{'x': x, 'text': elText[:-2]}]})
                samepage_headers.append({'No': hearderNo, 'y': y, 'header': [elText[:-2]]})
                hearderNo += 1
                continue
            elif insert_otherfield == False and elText == 'DEMANDADO \n':
                rest.append({'page': pageNo, 'y': y, 'header': [{'x': x, 'text': elText[:-2]}]})

            for text_line in element:
                for character in text_line:
                    if isinstance(character, LTChar):
                        if round(character.size) == 16:
                            Juzgado = elText
                            sql = ("INSERT INTO Juzgado "
                                    "(page, y, text) "
                                    "VALUES (%s, %s, %s)")
                            val = (pageNo, y, elText)
                            cursor.execute(sql, val)
                            cnx.commit()
                            break
                        elif round(character.size) == 10 and character.fontname == 'ABCDEE+Eras Medium ITC':
                            Fecha = elText
                            break
                        elif round(character.size) == 9 and re.findall('^\d \n$', elText): # '1 \n' '2 \n' ....
                            e_x = element.bbox[0]
                            sql = "INSERT INTO elements (page, x, y, text) VALUES (%s, %s, %s, %s)"
                            cursor.execute(sql, (pageNo, x, y, elText))
                            cnx.commit()
                            break
                        elif round(character.size) == 9 and elText != ' \n' and elText != '  \n':
                            # 'LIC. EMMA LAURA MARTINEZ SOTO' ....
                            if elText.startswith('LIC.'):
                                print('EXCLUDED : {}'.format(elText))
                                break
                            # '...  1 \n'
                            elif re.findall('  \d \n$', elText): 
                                sql = "INSERT INTO elements (page, x, y, text) VALUES (%s, %s, %s, %s)"
                                cursor.execute(sql, (pageNo, x, y, elText))
                                cnx.commit()
                            # 6789/20, 10.30, 09:00 ...
                            elif x < 70 and (re.findall('^\d+\/.+', elText) or re.findall('^\d+\..+', elText) or re.findall('^\d+\:.+', elText)):
                                sql = "INSERT INTO elements (page, x, y, text) VALUES (%s, %s, %s, %s)"
                                cursor.execute(sql, (pageNo, x, y, elText))
                                cnx.commit()
                            else:
                                sql = ("INSERT INTO elements "
                                        "(page, x, y, text) "
                                        "VALUES (%s, %s, %s, %s)")
                                val = (pageNo, x, y, elText)
                                cursor.execute(sql, val)
                                cnx.commit()
                            break
                                
print("create primary table!")

# sort the headers list by page and y
a, b, c = [], [], []
for i in createList(1, pageNo):
    a = []
    for h in headers:
        if h['page'] == i:
            a.append(h)
    
    b = complex_list_sort(a)
    c += b
headers = c    
##################################
## rest field & reversed field.
##################################
for h in headers: 
    page = h['page']
    y = h['y']
    # fix reversed field
    if h['header'][-2]['text'] == 'FECHA DE' and h['header'][-3]['text'] == 'ACUERDO':
        h['header'][-2]['text'] = 'ACUERDO'
        h['header'][-3]['text'] = 'FECHA DE'
        temp = h['header'][-2]['x']
        h['header'][-2]['x'] = h['header'][-3]['x']
        h['header'][-3]['x'] = temp
        #####################################
        # delete the header record 'ACUERDO' in the image '1.jpg'
        #####################################
        sql = "DELETE FROM elements WHERE page=(%s) AND x=(%s) AND text=(%s);"
        val = (page, h['header'][-3]['x'], 'ACUERDO \n')
        cursor.execute(sql, val)
        cnx.commit()
    for r in rest:   
        if r['page'] == page:
            if r['y'] == y:
                # append rest field
                h['header'].append(r['header'][0])
                break

print("rest field & reversed field!")
# a = ''
# headers = json.loads(a)

############################################
## insert headers and contentofheaders table.
#############################################
for i in range(len(headers)):
    page = headers[i]['page']
    y = headers[i]['y']
    
    sql = ("INSERT INTO headers "
               "(page, y) "
               "VALUES (%s, %s)")
    val = (page, y)
    cursor.execute(sql, val)
    cnx.commit()
    headers_id = cursor.lastrowid
    # record the content of headers (table in pdf)
    for c in headers[i]['header']:
        sql = ("INSERT INTO contentofheaders "
              "(id, content, x) "
              "VALUES (%(id)s, %(content)s, %(x)s)")
        val = {
                'id': headers_id,
                'content': c['text'],
                'x': c['x'],
                }
        cursor.execute(sql, val)
        cnx.commit()
    
    # id of elements table
    if i==0:
        sql = "UPDATE elements SET id=(%s) WHERE (%s);"
        val = (headers_id, 1)
    else:
        sql = "UPDATE elements SET id=(%s) WHERE (page=(%s) AND y<=(%s)) OR page>(%s);"
        val = (headers_id, page, y, page)    
    cursor.execute(sql, val)
    cnx.commit()
        
    # delete the header record
    sql = "DELETE FROM elements WHERE page=(%s) AND y=(%s);"
    val = (page, y)
    cursor.execute(sql, val)
    cnx.commit()
    
print("insert headers and contentofheaders table!")

# json_object = json.dumps(headers)
# # Writing to sample.json
# if os.path.exists("headers.json"):
#   os.remove("headers.json")
# else:
#   print("The file does not exist")
  
# with open("headers.json", "w") as outfile:
#     outfile.write(json_object)

print("Write the headers.json file successfully!")

sql = "SELECT id FROM headers WHERE 1"
cursor.execute(sql)
ds = cursor.fetchall()

for i in range(len(ds)):
    sql = "SELECT x FROM elements WHERE id=(%s) GROUP BY x;"
    cursor.execute(sql, ds[i])
    data1 = cursor.fetchall()
    sql = "SELECT x, content FROM contentofheaders WHERE id=(%s) GROUP BY x;"
    cursor.execute(sql, ds[i])
    data2 = cursor.fetchall()
    #######################################
    # get all the elements' x coordinate in table and update contentofheaders
    #######################################
    poplen = 0 # popped item number
    for j in range(len(data2)+1):
        if j < len(data2)-1: # if isn't lastest item
            ## When values smaller than the smallest value in data2 are 2 or more in data1
            if data1[j-poplen] <= data2[j-poplen]:
                if data2[j-poplen] < data1[j-poplen+1]:
                    cursor.execute("UPDATE contentofheaders SET record_x=(%s) WHERE id=(%s) and x=(SELECT x FROM contentofheaders WHERE id=(%s) LIMIT %s,1)",(data1[j-poplen][0], ds[i][0], ds[i][0], j-poplen))
                    cnx.commit()
                else:
                    data1.pop(0)
                    poplen += 1
            else:
                data1.insert(j-poplen, '')
        elif j == len(data2)-1: # if lastest item.
            if data1[j-poplen] <= data2[j-poplen]:
                cursor.execute("UPDATE contentofheaders SET record_x=(%s) WHERE id=(%s) and x=(SELECT x FROM contentofheaders WHERE id=(%s) LIMIT %s,1)",(data1[j-poplen][0], ds[i][0], ds[i][0], j-poplen))
                cnx.commit()
            else:
                data1.insert(j-poplen, '')
        elif poplen > 0: # loop one more to consider the pushing and pulling
        # else: # loop one more to consider the pushing and pulling
            
            if data1[j-poplen] <= data2[j-poplen]:
                cursor.execute("UPDATE contentofheaders SET record_x=(%s) WHERE id=(%s) and x=(SELECT x FROM contentofheaders WHERE id=(%s) LIMIT %s,1)",(data1[j-poplen][0], ds[i][0], ds[i][0], j-poplen))
                cnx.commit()
    print('DONE ' + str(i))


####################################### 
## Split the ones merged with 2 more elements
#######################################
print("START to split the ones merged with 2 more elements!!!")
pageNo = 0
for page_layout in extract_pages(FILE, laparams=_LA_PARAMS):
    pageNo += 1
    if pageNo < 3:
        continue
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            elText = element.get_text()
            # if elText == '07/12/2021  DEMANDADO PRESENTA \n':
            #     print(elText)
            # else:
            #     continue
            x = round(element.bbox[0])
            y = round(element.bbox[1])
            x1 = round(element.bbox[2])
            sql = "SELECT id FROM elements WHERE page=%s AND x=%s AND y=%s AND text=%s"
            cursor.execute(sql, (pageNo, x, y, elText))
            result1 = cursor.fetchall()
            if len(result1) == 0:
                continue
            else:
                cursor.execute("SELECT content, record_x FROM contentofheaders WHERE id=%s ORDER BY x", (result1[0][0],))
                result2 = cursor.fetchall()
                content = [sel[0] for sel in result2]
                record_x = [sel[1] for sel in result2]
                
            ################################
            # Add those where the record_x field of contentofheaders is none
            # fill empty 'record_x' field in contentofheaders
            # Temporarily fill '77' on each 'EXP/LAB' records in ['HORA', 'EXP/LAB', 'ACTOR', 'DEMANDADO'] header
            # Temporarily fill '104' on each 'EXP/LAB' records in ['AMP/NO', 'EXP/LAB', 'QUEJOSO', 'TERCERO INTERESADO', 'ACUERDO'] header
            ###################################################### And fill empty juzgado_id field in headers ##########################
            ################################
            if content == ['HORA', 'EXP/LAB', 'ACTOR', 'DEMANDADO'] and record_x[1] == None:
                sql = "UPDATE contentofheaders SET record_x=%s WHERE id=%s AND content=%s"
                cursor.execute(sql, (77, result1[0][0], content[1]))
                cnx.commit()
                record_x[1] = 77
                print("Filling 77 in 'record_x' field " + str(result1[0][0]) + "th 'id' of 'contentofheaders' table.")
            elif content == ['AMP/NO', 'EXP/LAB', 'QUEJOSO', 'TERCERO INTERESADO', 'ACUERDO'] and record_x[1] == None:
                sql = "UPDATE contentofheaders SET record_x=%s WHERE id=%s AND content=%s"
                cursor.execute(sql, (104, result1[0][0], content[1]))
                cnx.commit()
                record_x[1] = 104
                print("Filling 104 in 'record_x' field " + str(result1[0][0]) + "th 'id' of 'contentofheaders' table.")
            
            if x in record_x:
                index = record_x.index(x)
            else:
                continue
            if index == len(record_x)-1: # if last index, 
                continue
            elif x1 < record_x[index+1]:
                continue
            elif x1 >= record_x[index+1]:
                how = 2 # case of merged with 2 elements
            if index <= len(record_x)-3:
                if x1 >= record_x[index+2]:
                    how = 3 # case of merged with 3 elements 
                            # assume that there is no case of 4 more
            

            for text_line in element:
                for character in text_line:
                    if isinstance(character, LTChar):
                        # find out losted record's first letter
                        if round(character.bbox[0]) == record_x[index+1] and x == record_x[index]:
                            print(elText)
                            temp, temp1 = '', ''
                            for cha in text_line:
                                if type(cha) == LTChar:
                                    if how == 3 and round(cha.bbox[0]) >= record_x[index+2]:
                                        temp1 += cha._text
                                    elif cha.bbox[0] >= character.bbox[0]:
                                        temp += cha._text
                            # trim the origion text and update it
                            sql = "UPDATE elements SET text=%s WHERE id=%s AND page=%s AND x=%s AND y=%s"
                            cursor.execute(sql, (elText.split(temp)[0], result1[0][0], pageNo, x, y))
                            cnx.commit()
                            # trim the origion text and insert the rest
                            sql = "INSERT INTO elements (id, page, x, y, text) VALUES (%s, %s, %s, %s, %s)"
                            cursor.execute(sql, (result1[0][0], pageNo, record_x[index+1], y, temp))
                            cnx.commit()
                            if how == 3:
                                # trim the origion text and insert the rest
                                sql = "INSERT INTO elements (id, page, x, y, text) VALUES (%s, %s, %s, %s, %s)"
                                cursor.execute(sql, (result1[0][0], pageNo, record_x[index+2], y, temp1))
                                cnx.commit()
                            break
# '''
################################
# First Step of Arrangement
################################
sql = "SELECT * FROM headers WHERE 1 ORDER BY id"
cursor.execute(sql)
headers = cursor.fetchall()
cnx.commit()
TABLES = {}
i = 0
for id, page, header_y, juzgado in headers:
    i += 1
    ########################
    # get content of header
    ########################
    cursor.execute("SELECT content, record_x FROM contentofheaders WHERE id=%s", (id,))
    contents = cursor.fetchall()
    record_x = [record_x for content, record_x in contents]
    content = [content for content, record_x in contents]
    print(record_x)
    cnx.commit()
    
    ########################
    ## Create Table for each 1, 2, 3 ...
    ########################    
    try:
        cursor.execute("DROP TABLE `%s`", (i,))
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("Deleting table {}: ".format(i), end='')
    cnx.commit()
    
    TABLES[''] = "CREATE TABLE `%s` (`id` int(11) NOT NULL AUTO_INCREMENT" + ",  `%s` varchar(255)" + ",  `%s` varchar(255)"
    later = ", PRIMARY KEY (`id`)) ENGINE=InnoDB"
    for l in content:
        TABLES[''] += ",  `%s` varchar(255)"
    TABLES[''] += later    
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(i), end='')
            cursor.execute(table_description, ((i,'page','y')+tuple(content)))
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")
            
    ######################
    # write the record in each table
    ######################
    
    sql = "SELECT * FROM elements WHERE id=%s ORDER BY page, y DESC, x"
    cursor.execute(sql, (id,))
    elements = cursor.fetchall()
    cnx.commit()
    for e in elements:
        if e[2] in record_x:
            cursor.execute("SELECT * FROM `%s` WHERE `'y'`=%s AND `'page'`=%s", (i, e[-2], e[1]))
            selected = cursor.fetchall()
            index = record_x.index(e[2])
            if len(selected) > 0:
                sql = "UPDATE `%s` SET `%s`=%s WHERE `'y'`=%s AND `'page'`=%s"
            else:
                sql = "INSERT INTO `%s` SET `%s`=%s, `'y'`=%s, `'page'`=%s"
            cursor.execute(sql, (i, content[index], e[-1], e[-2], e[1]))
            cnx.commit()
    print(id)

    ########################
    ## Create Table again for each 1001, 1002, 1003 ...
    ########################    
    try:
        cursor.execute("DROP TABLE `%s`", (i+1000,))
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("Deleting table {}: ".format(i+1000), end='')
    cnx.commit()
    
    TABLES[''] = "CREATE TABLE `%s` (`id` int(11) NOT NULL AUTO_INCREMENT" + ",  `%s` varchar(255)"
    later = ", PRIMARY KEY (`id`)) ENGINE=InnoDB"
    for l in content:
        TABLES[''] += ",  `%s` varchar(255)"
    TABLES[''] += later    
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(i+1000), end='')
            cursor.execute(table_description, ((i+1000,'y')+tuple(content)))
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")
            
    ######################
    # write the record in each table 1001, 1002, ...
    ######################
    
    sql = "SELECT * FROM `%s` WHERE 1 ORDER BY id"
    cursor.execute(sql, (i,))
    elements = cursor.fetchall()
    cnx.commit()
    
    for e in elements:
        e = list(e)
        
        if None in e:
            if e[0] == elements[0][0]:
                continue
            e[2] = ''
            for t in range(len(e)-2):
                if e[t+2] == None:
                    e[t+2] = ''
                l[t+2] += e[t+2]
            if e[0] == elements[-1][0]: # if the latest colume,
                record0000(e, i, l, content)
        elif None not in e:
            if '' not in l:
                record0000(e, i, l, content)
                l = e
            if e[0] == elements[0][0]: # if the fist colume, 
                l = e
            elif e[0] == elements[-1][0]:
                record0000(e, i, l, content)
            
    print(id)
    


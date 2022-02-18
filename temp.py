def complex_list_sort(c):    
    xCoord, cc = [], []
    for cItem in c:
        xCoord.append(cItem['x'])
    
    xCoord.sort()
    
    for x in xCoord:
        for cItem in c:
            if x == cItem['x']:
                cc.append(cItem)
                break
    return cc
    
h = {'No': 36, 'page': 23, 'y': 671, 'header': [{'x': 42, 'text': 'HORA'}, {'x': 221, 'text': 'ACTOR'}, {'x': 79, 'text': 'EXP/LAB'}, {'x': 435, 'text': 'DEMANDADO'}]}
h['header'] = complex_list_sort(h['header'])

print(h)
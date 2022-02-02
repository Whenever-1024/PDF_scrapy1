1. run model.py
2. contents to check before starting
    # 'LIC. EMMA LAURA MARTINEZ SOTO', like this, ones which is not included in the table, excluded.
    delete the header record 'ACUERDO'
    Add those where the record_x field of contentofheaders is none
    Temporarily fill '77' on each 'EXP/LAB' records in ['HORA', 'EXP/LAB', 'ACTOR', 'DEMANDADO'] header
    Temporarily fill '104' on each 'EXP/LAB' records in ['AMP/NO', 'EXP/LAB', 'QUEJOSO', 'TERCERO INTERESADO', 'ACUERDO'] header


    SELECT x FROM elements WHERE id=(%s) GROUP BY x;"
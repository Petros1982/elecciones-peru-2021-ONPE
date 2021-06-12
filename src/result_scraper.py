from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, AsIs
from selenium.common.exceptions import NoSuchElementException

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from datetime import datetime

import psycopg2
import psycopg2.extras
import time
import pprint
import argparse


def check_return_numeric(webdriver, db_cursor, xpathsearch, errorMesg):
    field_value = webdriver.find_element_by_xpath(xpathsearch).text

    if field_value.isnumeric() == False:
        db_record = {
            'skip_reason' : errorMesg,
            'last_updated' : datetime.now()
        }

        sql_template = "UPDATE actas SET ({}) = %s WHERE id = {}"
        sql = sql_template.format(', '.join(db_record.keys()), row['id'])
        params = (tuple(db_record.values()),)
        print(db_cursor.mogrify(sql, params))
        db_cursor.execute(sql, params)
        return ''
    else:
        return field_value



parser = argparse.ArgumentParser()
parser.add_argument("min_id", help="minimum id to consider",type=int)
parser.add_argument("max_id", help="maximum id to consider",type=int)
args = parser.parse_args()

try:
    conn = psycopg2.connect("dbname='elections'")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
except:
    print("I am unable to connect to the database")

driver = webdriver.Chrome('/usr/local/bin/chromedriver')


# fetch info from actas that have not been processed

sql = "SELECT * FROM actas WHERE acta_url is NULL AND skip_reason is NULL AND id BETWEEN " + str(args.min_id) + ' AND ' + str(args.max_id)
cur.execute(sql)
results = cur.fetchall()

for row in results:
    url = row['url_mesa']
    print("URL Mesa: {}".format(url))
    driver.get(url)
    time.sleep(3)

    try:
        acta_url = driver.find_element_by_xpath("//span[contains(@class, 'glyphicon-eye-open')]/..").get_attribute("href")
    except NoSuchElementException as exc:
        print("No se encontró la acta para " + url)
        print("Marking record to skip in the future...")

        db_record = {
            'skip_reason' : "No existen actas escaneadas",
            'last_updated' : datetime.now()
        }

        sql_template = "UPDATE actas SET ({}) = %s WHERE id = {}"
        sql = sql_template.format(', '.join(db_record.keys()), row['id'])
        params = (tuple(db_record.values()),)
        print(cur.mogrify(sql, params))
        cur.execute(sql, params)
        continue

    total_votantes = check_return_numeric(driver, cur, "//th[contains(text(), 'Total Votantes')]/../../tr[2]/td[2]", 
                            'Simbolo # en total votantes')
    if (total_votantes == ''):
        continue

    votos_en_blanco = check_return_numeric(driver, cur, "//td[contains(text(), 'VOTOS EN BLANCO')]/following-sibling::td", 
                            'Simbolo # en votos en blanco')
    if (votos_en_blanco == ''):
        continue
    
    votos_pl = check_return_numeric(driver, cur, "//td[contains(text(), 'PARTIDO POLITICO NACIONAL PERU LIBRE')]/following-sibling::td", 
                            'Simbolo # en votos_pl')
    if (votos_pl == ''):
        continue
    
    votos_fp = check_return_numeric(driver, cur, "//td[contains(text(), 'FUERZA POPULAR')]/following-sibling::td", 
                            'Simbolo # en votos_fp')
    if (votos_fp == ''):
        continue
    
    votos_nulos = check_return_numeric(driver, cur, "//td[contains(text(), 'VOTOS NULO')]/following-sibling::td", 
                            'Simbolo # en votos_nulos')
    if (votos_nulos == ''):
        continue

    votos_validos = check_return_numeric(driver, cur, "//td[contains(text(), 'TOTAL VOTOS VALIDOS')]/following-sibling::td", 
                            'Simbolo # en votos_validos')
    if (votos_validos == ''):
        continue

    votos_impugnados = check_return_numeric(driver, cur, "//td[contains(text(), 'VOTOS IMPUGNADOS')]/following-sibling::td", 
                            'Simbolo # en votos_impugnados')
    if (votos_impugnados == ''):
        continue

    votos_emitidos = check_return_numeric(driver, cur, "//td[contains(text(), 'TOTAL VOTOS EMITIDOS')]/following-sibling::td", 
                            'Simbolo # en votos_emitidos')
    if (votos_emitidos == ''):
        continue

    num_electores = check_return_numeric(driver, cur, "//th[contains(text(), 'Total Votantes')]/../../tr[2]/td", 
                            'Simbolo # en num_electores')
    if (num_electores == ''):
        continue

    db_record = {
        #'departamento' : department['DESC_DEP'],
        #'provincia' : province['DESC_PROV'],
        #'distrito' : district['DESC_DIST'],
        #'nombre_local' : local['local_name'],                                    
        #'mesa' : mesa_entry['mesa_name'],
        #'codigo_departamento' : department['CDGO_DEP'],
        #'codigo_provincia' : province['CDGO_PROV'],
        #'codigo_distrito' : district['CDGO_DIST'],
        #'codigo_local' : local['local_code'],
        #'url_local' : local['local_url'],
        #'url_mesa' : mesa_entry['mesa_url'],
        'acta_numero_copia' : driver.find_element_by_xpath("//table[contains(@class, 'tabla_resultado')]/tr[2]/td[2]").text,
        'direccion' : driver.find_element_by_xpath("//div[contains(@class, 'table-responsive')]/table/tr[2]/td[5]").text,
        'acta_url' : acta_url,
        'num_electores' : num_electores,
        'total_votantes' : total_votantes,
        'estado_del_acta' : driver.find_element_by_xpath("//th[contains(text(), 'Total Votantes')]/../../tr[2]/td[3]").text,
        'votos_pl' : votos_pl,
        'votos_fp' : votos_fp,
        'votos_validos' : votos_validos,
        'votos_en_blanco' : votos_en_blanco,
        'votos_nulos' : votos_nulos,
        'votos_impugnados' : votos_impugnados,
        'votos_emitidos' : votos_emitidos,
        'last_updated' : datetime.now()
    }

    pprint.pprint(db_record)

    sql_template = "UPDATE actas SET ({}) = %s WHERE id = {}"
    sql = sql_template.format(', '.join(db_record.keys()), row['id'])
    params = (tuple(db_record.values()),)
    print(cur.mogrify(sql, params))
    cur.execute(sql, params)
    

    #print(len(mesas_procesadas_elements))
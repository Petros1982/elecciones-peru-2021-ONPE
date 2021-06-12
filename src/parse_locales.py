import json
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, AsIs

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

try:
    conn = psycopg2.connect("dbname='elections'")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
except:
    print("I am unable to connect to the database")

driver = webdriver.Chrome('/usr/local/bin/chromedriver')

url_base = 'https://www.resultadossep.eleccionesgenerales2021.pe/SEP2021/Actas/Ubigeo/P'
with open('ubigeos.json') as f:
    config = json.load(f)
    #print(config['ubigeos']['departments'])

    for department in config['ubigeos']['departments']:

        for province in config['ubigeos']['provinces']:

            for district in config['ubigeos']['districts']:

                if province['CDGO_PADRE'] == department['CDGO_DEP']:

                    if district['CDGO_PADRE'] == province['CDGO_PROV']:

                        # check if we have processed that district and if so, skip
                        sql = "SELECT * FROM actas WHERE codigo_distrito = '" + district['CDGO_DIST'] + "'"
                        cur.execute(sql)
                        print(sql)
                        

                        if (len(cur.fetchall()) > 0):
                            print("Skipping " + district['CDGO_DIST'])
                            continue
                        else:
                            print(district['CDGO_DIST'] + " not found")

                        url = url_base + '/' + department['CDGO_DEP'] + '/' + province['CDGO_PROV'] + '/' + district['CDGO_DIST']
                        #print(department['DESC_DEP'] + " [" + province['DESC_PROV'] + "][" + district['DESC_DIST'] + "] : " + url)
                        
                        driver.get(url)
                        time.sleep(1.5)
                        select_element = driver.find_element_by_xpath("//select[@name = 'cod_local']")
                        option_elements = select_element.find_elements_by_xpath('.//*')                        
                        #print(len(option_elements))

                        locales = []

                        for element in option_elements:                       

                            option_value = element.get_attribute('value')

                            #print(option_value)
                            if option_value == '0':
                                continue
                            
                            # local_name = element.text <======= name of local
                            new_url = url + '/' + option_value

                            local_entry = { 
                                'local_name' : element.text, 
                                'local_code' : option_value, 
                                'local_url' : new_url
                            }

                            locales.append(local_entry)

                        # fetch mesas urls

                        for local in locales:

                            # Get in local and search mesas
                            driver.get(local['local_url'])
                            time.sleep(2.5)
                            mesas_procesadas_elements = driver.find_elements_by_xpath("//div[contains(@class,'mesas procesada_sin')]")
                            print(len(mesas_procesadas_elements))
                            
                            mesas = []

                            for mesa_element in mesas_procesadas_elements:
                                mesa_entry = {
                                    'local' : local,
                                    'mesa_name' : mesa_element.text,
                                    'mesa_url' : local['local_url'] + '/' + mesa_element.text
                                }

                                mesas.append(mesa_entry)

                                # insert into db

                                db_record = {
                                    'departamento' : department['DESC_DEP'],
                                    'provincia' : province['DESC_PROV'],
                                    'distrito' : district['DESC_DIST'],
                                    'nombre_local' : local['local_name'],                                    
                                    'mesa' : mesa_entry['mesa_name'],
                                    'codigo_departamento' : department['CDGO_DEP'],
                                    'codigo_provincia' : province['CDGO_PROV'],
                                    'codigo_distrito' : district['CDGO_DIST'],
                                    'codigo_local' : local['local_code'],
                                    'url_local' : local['local_url'],
                                    'url_mesa' : mesa_entry['mesa_url'],
                                    'acta_numero_copia' : None,
                                    'direccion' : None,
                                    'acta_url' : None,
                                    'num_electores' : None,
                                    'total_votantes' : None,
                                    'estado_del_acta' : None,
                                    'votos_pl' : None,
                                    'votos_fp' : None,
                                    'votos_validos' : None,
                                    'votos_en_blanco' : None,
                                    'votos_nulos' : None,
                                    'votos_impugnados' : None,
                                    'votos_emitidos' : None,
                                    'last_updated' : None
                                }

                                columns = db_record.keys()
                                values = [db_record[column] for column in columns]

                                insert_statement = 'insert into actas (%s) values %s'
                                cur.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
                                print(cur.mogrify(insert_statement, (AsIs(','.join(columns)), tuple(values))))                                    
driver.close()

                        
                        
                        



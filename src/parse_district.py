import json

url_base = 'https://www.resultadossep.eleccionesgenerales2021.pe/SEP2021/Actas/Ubigeo/P'
with open('ubigeos.json') as f:
    config = json.load(f)
    #print(config['ubigeos']['departments'])

    for department in config['ubigeos']['departments']:

        for province in config['ubigeos']['provinces']:

            for district in config['ubigeos']['districts']:

                if province['CDGO_PADRE'] == department['CDGO_DEP']:

                    if district['CDGO_PADRE'] == province['CDGO_PROV']:

                        url = url_base + '/' + department['CDGO_DEP'] + '/' + province['CDGO_PROV'] + '/' + district['CDGO_DIST']
                        #print(department['DESC_DEP'] + " [" + province['DESC_PROV'] + "][" + district['DESC_DIST'] + "] : " + url)
                        print(url)
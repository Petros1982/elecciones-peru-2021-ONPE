# elecciones-peru-2021-ONPE
Resultados (data) de elecciones 2021 y código para extraer data de la ONPE

# Data
Licencia liberal, pero si vas a usarlo por favor un tweet a `@rburhum` y `@tagacat` avisando que as así. Un #SinCienciaNoHayFuturo es inclusive mejor ;-)

Folder: `/data`:
* `result_resumen_por_ubigeo.csv`: En formato csv. Con ubigeos. Campos de primera vuelta y segunda vuelta a nivel de *distrito*
* `result_resumen_por_mesa.csv`: En formato csv. Con ubigeos. Campos de primera vuelta y segunda vuelta a nivel de *mesa/acta*

Nota, se han procesado 77983 records hasta esta mañana. Actualización pronto con los records restantes.

# Código

Folder: `/src/`
Algo de paciencia - escrito a la rápida y sin el cariño típico que le doy. Funciona, pero obviamente puede ser mejorado.

```bash

# create a database in postgres
createdb elections
psql elections < ./src/create_tables.sql


# run code (need to have Chromium driver installed)
cd src
pip install -r requirements.txt
python parse_locales.py # to scrape all locales and get a list of mesas in db

# then, as you get those filled, you can execute as many browsers processes 
# as you want to scrape and divide by id. for example, to execute 9 processes in parallel:

python result_scraper.py 1 10000 &
python result_scraper.py 10001 20000 &
python result_scraper.py 20001 30000 &
python result_scraper.py 30001 40000 &
python result_scraper.py 40001 50000 &
python result_scraper.py 50001 60000 &
python result_scraper.py 60001 70000 &
python result_scraper.py 70001 80000 &
python result_scraper.py 80001 90000 &

```
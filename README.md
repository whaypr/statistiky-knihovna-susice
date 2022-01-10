# Vizualizace otevřených dat Městské knihovny Sušice

Aplikace dynamicky a interaktivně vizualizuje [otevřená data Městské knihovny Sušice](https://susice.tritius.cz/statistics)

Data k vizualizaci jsou skriptem parsována z webu knihovny a ukládána do csv souborů, které aplikace načítá a zpracovává

Dostupné [online](http://whaypr.ml:50)

## Pro vývojáře

Veškeré části aplikace se spouští z **kořenového adresáře projektu**

Vygenerování dat:
```
$ python app/parsing.py
```
* V místě zavolání skriptu vytvoří adresářovou strukturu a naplní ji daty v csv formátu
* Skript lze zavolat z jakéhokoliv adresáře, ale data pro aplikaci je nutné vytvořit v **kořenovém adresáři projektu**
* Není potřeba dělat, data jsou již k dispozici, ale může sloužit k získání aktuálních dat (znovu se zparsují všechna data, ne jen nová)
* Data není potřeba před zavoláním skriptu mazat
* Skript se používá i v aplikaci, kde každou hodinu automaticky stáhne nová data

Spuštění aplikace:
```
$ python3 app/visualization
```
* Spustí Flask server s aplikací
* Dostupný lokálně na adrese [127.0.0.1:8050](http://127.0.0.1:8050/)

Provedení testů:
```
$ pytest tests/test_parsing.py
```

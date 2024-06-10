# Introduccció

Aquest document descriu com funciona el sistema per aquelles persones que en vulguin fer modificacions.

# Fonts de dades

Usem tres fonts de dades.

## catalan-dict-tools

Els verbs es generen a partir de les dades lingüístiques del diccionari _catalan-dict-tools_ de Softcatalà.

Les dades tenen el format: forma, lemma, postag. Per exemple:
	
> cantaria cantar VMIC1S00

El significat del _postag_ està documentat a: https://freeling-user-manual.readthedocs.io/en/latest/tagsets/tagset-ca/#part-of-speech-verb

Sempre assumim que hi ha una tripleta.

## Viccionari

Les definicions dels verbs provenen del bolcat del Viccionari en format XML. Les definicions dins del XML usen el format de Wikimedia,
com ara enllaços estil _[[:de:|Deutsch (alemany)]]_ que netegem per quedar-nos només el text de la descripció.


## Dades específiques del conjugador

Dades específiques del conjugador:
* El fitxer _replace_diacritics_iec.txt_ conté els diacrítics que es van eliminar en la reforma de 2017. Usem aquesta informació per complementar el diccionari i poder mostrar la forma amb diacrític i sense.
* El fitxer _reflexius.txt_ que conté els verbs que són reflexius (informació que no conté el diccionari). S'usa per indicar les formes -se ('s) en l'infinitiu.

# Descripció general de la preparació de les dades

El resultat del procés de generació de dades és una col·lecció d'uns 10.000 fitxers (un per infinitiu) en format JSON que contenen tota la informació del verb combinada de les diferents fonts. Aquests fitxers són els mateixos que retorna el servidor quan se li demana un verb, és a dir, els JSON amb la informació dels verbs està generada estàticament.

## Extract

L'aplicació extract.py té dos objectius:

 a) Extreu només els infinitius en un fitxer de text

 b) Genera les formes verbals en format JSON

Els infinitius a) són necessaris després per poder importar les definicions des del buidatge de dades del Viccionari.

## Defintion

L'aplicació _definitions/extract-to-json.py_ té com a objectiu extreure les definicions del Viccionari en un JSON amb les definicions que després l'ordre extract.py usarà.

# Index

L'aplicació _indexer/index_creation.py_ s'encarrega de generar un índex amb el motor de cerca Whoosh que després usarem per oferir la cerca i l'autocomplete a la web.

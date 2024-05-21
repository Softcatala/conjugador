# Introduccció


# Fonts de dades

Usem tres fonts de dades.

## catalan-dict-tools

La font principal de dades lingüístiques és el diccionari _catalan-dict-tools_ de Softcatalà des d'on
en generen els verbs. 

Les dades tenen el format: form, lemma postag. Per exemple:
	
 cantaria cantar VMIC1S00

El significat del _postag_ està documentat a: https://freeling-user-manual.readthedocs.io/en/latest/tagsets/tagset-ca/#part-of-speech-verb

Sempre assumim que hi ha una tripleta.

## Viccionari

Les definicions dels verbs provenen del bolcat del Viccionari en format XML. Les definicions dins del XML usen el format de Wikimedia,
com ara enllaços estil _[[:de:|Deutsch (alemany)]]_ que netegem per quedar-nos només el text de la descripció.


## Dades específiques del conjugador

Algunes dades específiques d'aquest com reflexius.txt o replace_diacritics_iec.txt
* El fitxer replace_diacritics_iec.txt que conté els diacrítics que es van eliminar en la reforma de 2017. Usem aquesta informació per complementar el diccionari i poder mostrar la forma amb i sense diacrític.
* El fitxer reflexius.txt que conté els verbs que són reflexius (informació que no conté el diccionari). S'usa per indicar les formes -se ('s) en l'infinitiu.

# Descripció general de la preparació de les dades

El resultat del proces de generació de dades són una col·leció d'uns 10.000 fitxers (un per infinitiu) en format JSON que contenten tota la informació del verb combinada de les diferents fonts. Aquests fitxers són els mateixos que retorna el servidor quan se li demana un verb, és a dir, els JSON amb la informació dels verbs està generada estàticament.

## Extract

L'aplicació extract.py té dos objectius:

 a) Extreu només els infinitius en fitxer de text
 b) Generar les formes verbals en format JSON

Els infinitius a) són necessaris després per poder importar les definicions des del bolcat de dades del Viccionari.

## Defintion

L'aplicació _definitions/extract-to-json.py_ té com a objectiu extreure les defincions del Viccionari en un JSON amb les definicions que després l'ordre extract.py usarà.

# Index

L'aplicació _indexer/index_creation.py_ s'encarrega de generar un índex amb el motor de cerca Whoosh que després usarem per oferir la cerca i l'autocomplete. 







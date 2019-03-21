import http
import json
import logging
import urllib.request
from collections import OrderedDict
from json import JSONDecodeError
from urllib.error import URLError, HTTPError
from applicatie.logic.controles import controle_met_schema
from config.configurations import REPO_PATH

_logger = logging.getLogger(__file__)

def ophalen_en_controleren_databestand(jsonbestand):
    """Haal JSON-bestand op. Voer controles uit.
    Geef JSON-bestand terug of een lijst met foutmeldingen.
    De volgende stappen worden doorlopen:
        - json data bestand inlezen
        - json schema ophalen van web
        - json data controleren aan json schema
        - json definitie bestand ophalen van web
        - TODO: json data controleren aan het definitie bestand
    """

    # json bestand inlezen
    data_bestand, fouten = laad_json_bestand(jsonbestand)
    if fouten:
        return data_bestand, fouten

    # json schema ophalen van web
    bestandsnaam = 'iv3_data_schema_v1_0.json'
    schema_bestand, fouten = ophalen_bestand_van_web(REPO_PATH, bestandsnaam, 'schemabestand')
    if fouten:
        return data_bestand, fouten

    # json data controleren aan json schema
    fouten = controle_met_schema(data_bestand, schema_bestand)
    if fouten:
        return data_bestand, fouten

    # json bestand voldoet aan het schema
    # echter balans_lasten, balans_baten en/of balans_standen kunnen ontbreken
    # in dit geval voegen we deze toe als lege dict
    if 'balans_lasten' not in data_bestand['data']:
        data_bestand['data'].update({'balans_lasten': []})
    if 'balans_baten' not in data_bestand['data']:
        data_bestand['data'].update({'balans_baten': []})
    if 'balans_standen' not in data_bestand['data']:
        data_bestand['data'].update({'balans_standen': []})

    # json definitie bestand ophalen van web
    meta = data_bestand['metadata']
    overheidslaag = meta['overheidslaag']
    boekjaar = meta['boekjaar']
    bestandsnaam = 'iv3_definities_' + overheidslaag + '_' + boekjaar + '.json'
    definitie_bestand, fouten = ophalen_bestand_van_web(REPO_PATH, bestandsnaam, 'definitiebetand')
    if fouten:
        return data_bestand, fouten

    # json data controleren aan het definitiebestand
    # TODO: nog niet klaar

    return data_bestand, fouten


def laad_json_bestand(bestand):
    """Laad een json bestand. Het bestand kan gecodeerd zijn als utf-8 of als cp1252."""
    newfile = bestand.read()
    data = None
    foutmeldingen = []

    # Vind een geschikte encoding
    encodings = ['utf8', 'cp1252']

    for encoding in encodings:
        try:
            data = json.loads(newfile.decode(encoding), object_pairs_hook=OrderedDict)
            _logger.info(f'verwerken als {encoding}')
            break
        except UnicodeDecodeError:
            continue  # Probeer de volgende
        except JSONDecodeError as e:
            foutmeldingen.append(f"{bestand} is geen json-bestand")
            break
    else:
        foutmeldingen.append('Het bestand kon niet gelezen worden. '
                             'Geef een geschikt json-bestand.')

    return data, foutmeldingen


def ophalen_bestand_van_web(url, bestandsnaam, bestandstype):
    """Haal JSON bestand van website op.

     Geef JSON-bestand terug of een lijst met foutmeldingen.
     """
    url = url + bestandsnaam
    foutmeldingen = []
    bestand = None
    errorcode = 0
    try:
        webUrl = urllib.request.urlopen(url)
    except HTTPError as e:
        errorcode = e.code
    except URLError as e:
        errorcode = e.code
    if errorcode == 0:
        if webUrl.getcode() == http.HTTPStatus.OK:
            bestand, foutmeldingen_json = laad_json_bestand(webUrl)
            foutmeldingen.extend(foutmeldingen_json)
            _logger.info("JSON bestand opgehaald van %s", url)
    else:
        errormessage = 'Fout bij ophalen {0}: {1} (foutcode #{2})'.format(bestandstype, bestandsnaam, errorcode)
        foutmeldingen.append(errormessage)
        _logger.info("Fout bij ophalen Iv3-definitiebestand")

    return bestand, foutmeldingen

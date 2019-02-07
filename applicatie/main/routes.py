from flask import render_template, request
from applicatie.logic.inlezen import laad_json_bestand, ophalen_sjabloon, indikken_data
from applicatie.logic.maak_matrix import maak_tabel, maak_lijst_koppen, pivot_table
from applicatie.logic.draaitabel import DraaiTabel
from applicatie.main import bp


@bp.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not request.files.get('file', None):
            return render_template("index.html")
        else:
            jsonfile = request.files['file']
            return matrix(bestand=jsonfile)
    elif request.method == 'GET':
        return render_template("index.html")


@bp.route("/matrix", methods=['GET', 'POST'])
def matrix(bestand):
    """Laad de pagina met een overzicht."""
    if bestand:
        complete_upload = laad_json_bestand(bestand)
        metadata = complete_upload['metadata']
        sjabloon = ophalen_sjabloon(metadata)

        sjabloon_meta = sjabloon['metadata']
        compacte_data = indikken_data(complete_upload['waarden'])
        print('stap 1')
        lasten_header = {'kolkop': maak_lijst_koppen(sjabloon, "LastenCategorien")}
        baten_header = {'kolkop': maak_lijst_koppen(sjabloon, "BatenCategorien")}
        balans_header = {'kolkop': maak_lijst_koppen(sjabloon, "BalansDatums")}
        rekening_rijen = {'rijkop': maak_lijst_koppen(sjabloon, 'Taakvelden')}
        balans_rijen = {'rijkop': maak_lijst_koppen(sjabloon, 'Balanscodes')}
        print('stap 2')
        lasten_tabel = maak_tabel(compacte_data, 'Lasten', lasten_header, rekening_rijen)
        baten_tabel = maak_tabel(compacte_data, 'Baten', baten_header, rekening_rijen)
        balans_lasten_tabel = maak_tabel(compacte_data, 'balans_lasten', lasten_header, balans_rijen)
        balans_baten_tabel = maak_tabel(compacte_data, 'balans_baten', baten_header, balans_rijen)
        balans_standen_tabel = maak_tabel(compacte_data, 'balans_standen', balans_header, balans_rijen)
        # data1 = data # dit is nep-data, niet ingelezen
        print('stap 3')

        lasten = DraaiTabel(complete_upload['waarden'])

        params = {
            'lasten': lasten,  # Is alles wat ik nodig heb
            'lasten_header': lasten_header,
            'baten_header': baten_header,
            'balans_header': balans_header,
            'lasten_tabel': lasten_tabel,
            'baten_tabel': baten_tabel,
            'balans_lasten_tabel': balans_lasten_tabel,
            'balans_baten_tabel': balans_baten_tabel,
            'balans_standen_tabel': balans_standen_tabel,
            'data': complete_upload,
            'meta': metadata,
            'sjabloon': sjabloon_meta,
        }

    return render_template("matrix.html", **params)

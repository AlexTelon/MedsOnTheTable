# -*- coding: utf-8 -*-
import sys

from flask import Flask, render_template, jsonify
import suds


reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
medArray = []


@app.route('/')
def index():
    return render_template("layout.html")


@app.route('/search')
def search():
    url = "http://sil40.test.silinfo.se/silapi40/SilDB?wsdl"
    sil = suds.client.Client(url)
    subs = sil.service.getDistributedDrugsByDrugId("20090916000021", False, -1)
    # print subs[0]

    #subs = sil.service.getSubstancesBySubstanceName ("Kodein%")
    #subs = sil.service.getDistributedDrugsByDistributedDrugTradeName ("Citodon", False, -1)
    #subs = sil.service.getDrugsByAtcCode ("N02AA59", False, -1)
    #subs = sil.service.getSILPregnancyLactationWarningsByNplIdList ("20090916000021")
    #subs = sil.service.getSuperDrugsByDistributedDrugTradeName("Aspirin", False, -1)
    #return subs[0]['text']
    print subs[0]['tradeName']
    return render_template("test.html", info=subs)


@app.route('/info/<id>')
def info(id):
    url = "http://sil40.test.silinfo.se/silapi40/SilDB?wsdl"
    sil = suds.client.Client(url)
    Fass = sil.service.getFassDocsByDrugId(str(id))
    return Fass[0]['XHtml']


# ATC is about what kind of medecine we are talking about, Different groups like blood and nervous system.

# How we get stuff from a ddrug ddrug[0]['nplId'].

# subs = sil.service.getDrugArticlesByDrugId ("20090916000021", False, -1) Gives information about different packages
# and their prices and so on


@app.route('/med/<brand>')
def brandInfo(brand):
    # Make sure we only put in unique ids
    if medArray.count(brand) == 0:
        medArray.append(brand)

    print "medArray: ", medArray
    return render_template('fassTest.html', ids=medArray, len=len(medArray))
    #return 'Medecinen: %s' % brand;


@app.route('/navbarInfo')
def navbarInfo():
    dict = {};
    url = "http://sil40.test.silinfo.se/silapi40/SilDB?wsdl"
    sil = suds.client.Client(url)
    for med in medArray:
        subs = sil.service.getDistributedDrugsByDrugId(med, False, -1)
        name = subs[0]['tradeName']
        dict[name] = med

    print dict
    return jsonify(dict)


@app.route('/navbar/nrOfIds')
def nrOfIds():
    temp = len(medArray)
    return str(temp)


@app.route('/clearNavbar')
def clearAllIds():
    while 0 != len(medArray):
        medArray.pop()
    return index()


@app.route('/card')
def card_view():
    # set up the connection
    url = "http://sil40.test.silinfo.se/silapi40/SilDB?wsdl"
    sil = suds.client.Client(url)

    #drug_list is a dictionary key=drugId aka nlpdID --> value= information about a object
    # [0] - DistributedDrugs Object
    # [1] - atcsCode Object
    drug_list = {}

    # add some test object to the list
    medArray.append('20090916000021')
    medArray.append('19590602000075')
    medArray.append('19670825000035')
    medArray.append('19581231000017')
    medArray.append('19970619000075')

    atc_dict = {'A': 'Matsmältningsorgan och ämnesomsättning',
                'B': 'Blod och blodbildande organ',
                'C': 'Hjärta och kretslopp',
                'D': 'Hudpreparat',
                'G': 'Urin- och könsorgan samt könshormoner',
                'H': 'Systemiska hormonpreparat, exkl. könshormoner och insuliner',
                'J': 'Antiinfektiva medel för systemiskt bruk',
                'L': 'Tumörer och rubbningar i immunsystemet',
                'M': 'Rörelseapparaten',
                'N': 'Nervsystemet',
                'P': 'Antiparasitära, insektsdödande och repellerande medel',
                'R': 'Andningsorgan',
                'S': 'Ögon och öron',
                'V': 'Övrigt'}

    buttons = {"H": "btn-danger",
               "M": "btn-warning",
               "L": "btn-success"}

    if not medArray:
        print "medArray is empty"
    else:
        for drugId in medArray:
            #bättre med anropet??
            #superDrug = sil.service.GetSuperDrugsByDrugIdList (drugId, False, -1)

            #parse diffrent objects from SIL
            distDrugs = sil.service.getDistributedDrugsByDrugId(drugId, False, -1)
            atcCode = sil.service.getAtcsByDrugId(drugId)
            distDrugsHistNames = sil.service.getDistributedDrugHistoricalNamesByNplId(drugId)
            drug = sil.service.getDrugByDrugId(drugId, False, -1)


            #print distDrugsHistNames
            

            # Add the Sil-object to the drug_list dictionary
            drug_list[drugId] = distDrugs
            drug_list[drugId].append(atcCode[0])
            drug_list[drugId].append(distDrugsHistNames)
            drug_list[drugId].append(drug)

            # Debug prints
            #print type(drug_list[drugId])
            print drug_list[drugId][1]['atcCode'][0]  # forsta bokstaven for atc
            #print drug_list[drugId][2] #lista over historiska namn
            #print drug_list[drugId][3]        # skriv ut hela drug objektet
            #print drug_list[drugId][3]['substanceGroupName'] # vilken substans

            #print drug

    #print drug_list

    print atc_dict[drug_list[drugId][1]['atcCode'][0]]

    #print drug_list[drugId]['salesstoppedFlag']
    #print atcCode[0]

    return render_template('card_view.html', ids=medArray, drug_list=drug_list, buttons=buttons, atc_dict=atc_dict)


@app.route('/grid')
def grid():
    return render_template('grid_system.html')


@app.route('/drug_info')
def drug_info():
    return render_template('drug_info.html')


if __name__ == '__main__':
    app.run(debug=True)

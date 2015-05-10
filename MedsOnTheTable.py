# -*- coding: utf-8 -*-
"""
    Läkemedelsplattan
    ~~~~~~~~~~~~~~
    Ska visa information om mediciner...


    :copyright: (c) 2015 by Johan Nordin, Alex Telon, Kristina Engström.
    :license: LICENSE_NAME, see LICENSE_FILE for more details.
"""

# Imports  ---------------------------------------------
import sys
from flask import Flask, render_template, jsonify
import suds

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)

# Constants ---------------------------------------------
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


# Variables  ---------------------------------------------
medArray = []
drug_list = {}
super_drug_list = {}


# Routes     ---------------------------------------------
@app.route('/')
def index():
    return render_template("layout.html")


#: For search
@app.route('/search')
def search():
    # set up the connection
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


#: Get information from fass
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


#: Our own information page
@app.route('/med_info/<drugId>')
def med_info(drugId):
    return render_template("drug_info.html", drugId=drugId, drug_list=drug_list, buttons=buttons, atc_dict=atc_dict)

#: Add medicine from NFC
@app.route('/med/<nplId>')
def add_drug(nplId):

    # # -----------------------------------------------------------------
    # Make sure we only put in unique ids
    if medArray.count(nplId) == 0:
        medArray.append(nplId)

    # # -----------------------------------------------------------------
    # # set up the connection to SIL
    url = "http://sil40.test.silinfo.se/silapi40/SilDB?wsdl"
    sil = suds.client.Client(url)

    # # -----------------------------------------------------------------
    # # Hämta data från SIL
    superDrug = sil.service.getSuperDrugsByDrugIdList(nplId, False, -1)
    #superDrugArticles = sil.service.getSuperDrugArticlesByNplPackIdList (medArray, False, -1, "NON_APPROVED")
    distDrugsHistNames = sil.service.getDistributedDrugHistoricalNamesByNplId(nplId)

    # # -----------------------------------------------------------------
    # # Sätt in läkemedlet i våran dictionary som skickas till sidan med information.
    # # key=nlpID --> value=lista med godtyckliga saker [SuperDrug, .. ,etc,]
    super_drug_list[nplId] = superDrug
    super_drug_list[nplId].append(distDrugsHistNames)

    # # -----------------------------------------------------------------
    # # Exempel på hur man kommer åt saker i dictionary
    #print super_drug_list
    #print super_drug_list[nplId]

    #Komma åt SuperDrug objeket
    print "------------------------"
    print super_drug_list[nplId][0]

    #Komma åt saker i SuperDrug objeket t.ex. atc-koder
    print "------------------------"
    print super_drug_list[nplId][0]['atcs'][0]['atcCode']

    #Komma åt saker i SuperDrug objeket t.ex. DistributedDrug --> tradeName
    print "------------------------"
    print super_drug_list[nplId][0]['distributedDrugs'][0]['tradeName']

    #Komma åt saker i SuperDrug objeket t.ex. Drug --> substanceGroupId
    print "------------------------"
    print super_drug_list[nplId][0]['drug']['substanceGroupId']

    #Komma åt andra saker med samma nlpdId utanför SuperDrug objektet t.ex. distDrugsHistNames
    print "------------------------"
    print super_drug_list[nplId][1]


    # # -----------------------------------------------------------------
    # # Exempel på olika förfrågningar till SIL-online utöver SuperDrug objeket som kan göras

    #substance = sil.service.getSubstancesByNplSubstanceIdList(medArray)
    substance = sil.service.getSubstancesByNplSubstanceIdList (["IDE4POEWUAJJEVERT1", "IDE4POEIUA926VERT1"])
    distDrugContent = sil.service.getDistributedDrugContentsByNplIdList(medArray)
    distDrugContentFilt = sil.service.getDistributedDrugContentsByNplIdListFiltered(medArray)
    allSubstanceGroup = sil.service.getSubstanceGroups ()
    substanceGroup = sil.service.getSubstanceGroupBySubstanceGroupId("70")
    superDrugArticles = sil.service.getSuperDrugArticlesByNplPackIdList (medArray, False, -1, "NON_APPROVED")

    # # -----------------------------------------------------------------
    # # Tillhörande printar

    #print superDrugArticles
    #print substanceGroup
    #print substance
    #print allSubstanceGroup
    #print distDrugContent
    #print distDrugContentFilt
    #print drug_list

    # få alla biverkningar
    biverkningar = sil.service.getSideEffectsByNplIdList (medArray, "", "")
    #print biverkningar


    # -----------------------------------------------------------------
    # Första sättet att sätta ihop en lista --> SKA TAS BORT
    #parse diffrent objects from SIL
    distDrugs = sil.service.getDistributedDrugsByDrugId(nplId, False, -1)
    atcCode = sil.service.getAtcsByDrugId(nplId)
    distDrugsHistNames = sil.service.getDistributedDrugHistoricalNamesByNplId(nplId)
    drug = sil.service.getDrugByDrugId(nplId, False, -1)

    # Add the Sil-object to the drug_list dictionary --> SKA TAS BORT
    drug_list[nplId] = distDrugs
    drug_list[nplId].append(atcCode[0])
    drug_list[nplId].append(distDrugsHistNames)
    drug_list[nplId].append(drug)

    # Debug prints --> SKA TAS BORT
    #print type(drug_list[drugId])
    #print drug_list[drugId][1]['atcCode'][0]  # forsta bokstaven for atc
    #print drug_list[drugId][2] #lista over historiska namn
    #print drug_list[drugId][3]        # skriv ut hela drug objektet
    #print drug_list[drugId][3]['substanceGroupName'] # vilken substans
    #print drug

    #print atc_dict[drug_list[drugId][1]['atcCode'][0]]
    #print drug_list[drugId]['salesstoppedFlag']
    #print atcCode[0]


    return render_template('med_info.html', nplId_list=medArray, len=len(medArray))

#: ???
@app.route('/navbarInfo')
def navbarInfo():
    dict = {};
    url = "http://sil40.test.silinfo.se/silapi40/SilDB?wsdl"
    sil = suds.client.Client(url)
    for med in medArray:
        subs = sil.service.getDistributedDrugsByDrugId(med, False, -1)
        name = subs[0]['tradeName']
        dict[name] = med

    #print dict
    return jsonify(dict)


#: ???
@app.route('/navbar/nrOfIds')
def nrOfIds():
    temp = len(medArray)
    return str(temp)


#: Remove all medicine from the list.
@app.route('/clearNavbar')
def clearAllIds():
    while 0 != len(medArray):
        medArray.pop()
    return index()

#: The horizontal view
@app.route('/card')
def card_view():


    return render_template('card_view.html', ids=medArray, drug_list=drug_list, buttons=buttons, atc_dict=atc_dict)


# Some test routes (can be removed) ---------------------------------------------

@app.route('/grid')
def grid():
    return render_template('grid_system.html')


@app.route('/drug_info')
def drug_info():
    return render_template('drug_info.html')

@app.route('/l2')
def index2():
    return render_template("layout2.html")

@app.route('/test')
def test():
    return render_template("child.html")

@app.route('/test2')
def test2():
    return render_template("test2.html")


def add_some_meds():

    # set up the connection
    url = "http://sil40.test.silinfo.se/silapi40/SilDB?wsdl"
    sil = suds.client.Client(url)

    #drug_list is a dictionary key=drugId aka nlpdID --> value= information about a object
    # [0] - DistributedDrugs Object
    # [1] - atcsCode Object

    # # add some test object to the list
    # medArray.append('20090916000021')
    # medArray.append('19590602000075')
    # medArray.append('19670825000035')
    # medArray.append('19581231000017')
    # medArray.append('19970619000075')

    if not medArray:
        print "medArray is empty"
    else:
        for drugId in medArray:
            #bättre med anropet??
            superDrug = sil.service.getSuperDrugsByDrugIdList(drugId, False, -1)

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
            #print drug_list[drugId][1]['atcCode'][0]  # forsta bokstaven for atc
            #print drug_list[drugId][2] #lista over historiska namn
            #print drug_list[drugId][3]        # skriv ut hela drug objektet
            #print drug_list[drugId][3]['substanceGroupName'] # vilken substans
            #print drug

            #print superDrug



if __name__ == '__main__':
    app.run(debug=True)

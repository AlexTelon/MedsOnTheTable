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
           "L": "btn-success",
           "Y": "btn-danger",
           "N": "btn-success"}

glyph_icon = {"H": "glyphicon-remove",
              "M": "glyphicon-question-sign",
              "L": "glyphicon-ok",
              "Y": "glyphicon-remove",
              "N": "glyphicon-ok"}

word_count = {"default": "word-count-default",
              "medium": "word-count-medium",
              "long": "word-count-long"}

# Variables  ---------------------------------------------
medArray = []
drug_list = {}  # Gamla sättet att göra förfrågningar till SIL --> ska tas bort
super_drug_list = {}  # Dictionaryn som all information samlar i och som skickas till olika sidor.

# substance_count = {}            # Räknar hur många du har av samma substans
substance_count = dict()


# Routes     ---------------------------------------------
@app.route('/')
def index():
    return render_template("layout.html")


# : For search
@app.route('/search')
def search():
    # set up the connection
    url = "http://sil40.test.silinfo.se/silapi40/SilDB?wsdl"
    sil = suds.client.Client(url)
    subs = sil.service.getDistributedDrugsByDrugId("20090916000021", False, -1)
    # print subs[0]

    #subs = sil.service.getSubstancesBySubstanceName ("Kodein%")
    #subs = sil.service.getDistributedDrugsByDistributedDrugTradeName ("Citodon", False, -1)

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
@app.route('/med_info/<nplId>')
def med_info(nplId):
    return render_template("drug_info.html", nplId=nplId, super_drug_list=super_drug_list, buttons=buttons,
                           atc_dict=atc_dict, glyph_icon=glyph_icon)


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
    distDrugsHistNames = sil.service.getDistributedDrugHistoricalNamesByNplId(nplId)

    # Utbytbara läkemedel efter substansgrupp
    # Var försiktig här --> kan vara ej utbytbar
    if superDrug[0]['drug']['interchangeableFlag'] == "Y":
        drugsBySubstance = sil.service.getDrugsBySubstanceGroupId(superDrug[0]['drug']['substanceGroupId'], False,
                                                                  -1)  # tar lång tid for vissa läkemedel
        substance_count[superDrug[0]['drug']['substanceGroupId']] = substance_count.get(
            superDrug[0]['drug']['substanceGroupId'], 0) + 1

    else:
        drugsBySubstance = 0

    # Lista med dug objekt. Liknande läkemedel efter ATC-kod
    drugsByAtcCode = sil.service.getDrugsByAtcCode(superDrug[0]['atcs'][0]['atcCode'], False, -1)

    # få alla biverkningar
    drugId_in_list = []
    drugId_in_list.append(str(superDrug[0]['drug']['drugId']))
    #drugId_in_list.append("19590602000075")

    biverkningar = sil.service.getSideEffectsByNplIdList(drugId_in_list, "", "")
    #biverkningar = sil.service.getSideEffectsByNplIdList(["19590602000075"], "", "")
    #print biverkningar


    drugArticles = sil.service.getDrugArticlesByNplId(nplId)
    #print '----'
    #print drugArticles
    #print '----'

    size_and_price = {}

    for drugArt in drugArticles:
        size_and_price[drugArt['packSizeText']] = drugArt['aup']
        print drugArt['nplId']
        print drugArt['aup']
        print drugArt['drugId']
        print drugArt['distributedTradeName']
        print '--'

    #print size_and_price
    substance = sil.service.getSubstancesBySubstanceName("Diklofenak%")
    #print substance



    # TODO: the logic is not correct
    # Check the length of the tradename
    print "??????"
    print len(superDrug[0]['drug']['tradeName'])
    print "???????"
    if len(superDrug[0]['drug']['tradeName']) > 25:
        trade_name_length = "long"
    elif len(superDrug[0]['drug']['tradeName']) > 15:
        trade_name_length = "medium"
    else:
        trade_name_length = "default"

    # # -----------------------------------------------------------------
    # # Konfigurering innan insättning

    # Lägg till de utbytbara medicinerna i en lista
    interchangeableDrugs = []  # Lista med utbytbara läkemedel --> baserat på samma substans och stryka

    if drugsBySubstance != 0:
        for drug in drugsBySubstance:
            #print drug['strengthGroupId']
            if drug['tradeName'] != superDrug[0]['drug']['tradeName']:
                if drug['strengthGroupId'] == superDrug[0]['drug'][
                    'strengthGroupId']:  # Kolla så de har samma stryke grupp.
                    if drug['interchangeableFlag'] == 'Y':  # Kolla så de är utbytbara
                        #if not drug['tradeName'] in interchangeableDrugs:                       # Kolla så inte samma namn läggs till två gång troligen reduntdant
                        #print drug['tradeName']
                        interchangeableDrugs.append(drug['tradeName'])
    else:
        interchangeableDrugs.append("Ej utbytbar")


    # Lägg till de liknande medicinerna i en lista
    similarDrugs = []  # Lista med liknande läkemedel --> baserat på ATC-kod
    similarSubstance = []  # Lista med liknande Substans --> baserat på ATC-kod

    for drug in drugsByAtcCode:
        #if drug['strengthGroupId'] == superDrug[0]['drug']['strengthGroupId']:           # Kolla så de har samma stryke grupp.
        #if drug['interchangeableFlag'] == 'Y':                                       # Kolla så de är utbytbara
        if not drug['tradeName'] in similarDrugs:  # Kolla så inte samma namn läggs till två gång troligen reduntdant
            #print drug['tradeName']
            similarDrugs.append(drug['tradeName'])
            if not drug['substanceGroupName'] in similarSubstance:
                if not drug['substanceGroupName'] == 'Ospecificerad':
                    similarSubstance.append(drug['substanceGroupName'])

    #print similarDrugs
    #print similarSubstance


    biverkningar_efter_klass = {}
    # kolla om den är tom
    if not biverkningar:
        biverkningar_efter_klass["0"] = "Läkemedlet har inga biverkningar"
    else:
        for symtom in biverkningar[0]['sideEffects']:
            if symtom['frequency'] in biverkningar_efter_klass:
                # append the new number to the existing array at this slot
                #years_dict[line[0]].append(line[1])
                biverkningar_efter_klass[symtom['frequency']].append(symtom['symptom'])
            else:
                # create a new array in this slot
                # years_dict[line[0]] = [line[1]]
                biverkningar_efter_klass[symtom['frequency']] = [symtom['symptom']]


    #print biverkningar[0]['sideEffects'] #lista med symtom
    #print biverkningar[0]['sideEffects']['frequency']
    #print biverkningar_efter_klass

    # historiska namn ---------------------------------------

    hist_names = []
    #print '***********'
    #print superDrug[0]['distributedDrugs'][0]['tradeName'][:-1]
    #print distDrugsHistNames
    drug_name = superDrug[0]['distributedDrugs'][0]['tradeName'][:-1]
    trade_name = superDrug[0]['distributedDrugs'][0]['tradeName']

    print '---------'
    print trade_name
    print trade_name[-1:]
    print '---------'

    if '®' in trade_name:
        print 'YES'

    for name in distDrugsHistNames:
        if name != drug_name and name != trade_name:
            hist_names.append(name)

    # Check if the list is empty
    if not hist_names:
        hist_names.append("Inga historiska namn")
        #print "List is empty"

    # # -----------------------------------------------------------------
    # # Sätt in läkemedlet i våran dictionary som skickas till sidan med information.
    # # key=nlpID --> value=lista med godtyckliga saker [SuperDrug, .. ,etc,]
    super_drug_list[nplId] = superDrug  # [0] - SuperDrug objekt --> innehåller ATC, distDrug och Drug object
    super_drug_list[nplId].append(hist_names)  # [1] - Lista med de historiska namnen
    super_drug_list[nplId].append(drugsBySubstance)  # [2] -
    super_drug_list[nplId].append(interchangeableDrugs)  # [3] - Lista med de utbytbara medicinerna
    super_drug_list[nplId].append(similarDrugs)  # [4] - Lista med de liknanade medicinerna
    super_drug_list[nplId].append(similarSubstance)  # [5] - Lista med de liknanade substanserna
    super_drug_list[nplId].append(
        biverkningar_efter_klass)  # [6] - Dict med biverkningar key=frekvens -> value=lista över symtom
    super_drug_list[nplId].append(size_and_price)  # [7] - Dict med pris. key=storlek -> value=pris
    super_drug_list[nplId].append(trade_name_length)  # [8] - String. length of the trade name (can be removed)

    return render_template('layout.html', nplId_list=medArray, len=len(medArray))


#: Returns the current medicines that are to be shown in the navbar. Called from javascript in info.html
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


#: simple return of number of medicines shown in the navbar
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
    # Some hardcoded medicines that are added to the card view. TODO - remove this?
    #add_drug(19581215000033)
    #add_drug(19851206000039)
    #add_drug(19581115000027)
    #add_drug(20070605000020)

    return render_template('card_view.html',
                           ids=medArray,
                           super_drug_list=super_drug_list,
                           buttons=buttons,
                           atc_dict=atc_dict,
                           glyph_icon=glyph_icon,
                           substance_count=substance_count,
                           word_count=word_count)


# Some test routes


@app.route('/drug_info')
def drug_info():
    return render_template('drug_info.html')


@app.route('/test')
def test():
    return render_template("test.html")


if __name__ == '__main__':
    app.run(debug=True)

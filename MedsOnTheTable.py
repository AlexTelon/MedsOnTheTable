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
import helpers


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

eleven77 = { '19851206000039' : {'Viktigt': 'Man ska inte använda medicinen om man tidigare har fått astma eller allergiska besvär av acetylsalicylsyra eller av andra cox-hämmare mot smärta och inflammation. Om man har eller har haft vissa sjukdomar ska man rådgöra med läkare innan man tar medicinen. Det gäller till exempel ökad risk för blödning, magsår, hjärtsvikt, inflammatorisk tarmsjukdom eller någon njur- eller leversjukdom. Man ska rådgöra med läkare om man har astma. Medicinen kan ge en kraftig överkänslighetsreaktion med nässelutslag, rinnsnuva eller andningsbesvär. Sådana reaktioner är vanligare bland personer som har astma. Man ska också rådgöra med läkare om man har hjärtproblem eller tidigare har haft stroke eller om man har en ökad risk för dessa tillstånd på grund av blodtryckssjukdom, diabetes eller livsstil (till exempel om man röker eller inte motionerar regelbundet). Det kan finnas en ökad risk för hjärtinfarkt eller stroke vid användning av medicinen. Risken är större om man använder höga doser av medicinen under lång tid. Man bör inte använda medicinen i samband med vattkoppor eftersom den då kan öka risken för ovanliga, men allvarliga, följdinfektioner. Gelen ska inte smörjas på öppna sår, infekterad hud, akne eller eksem. Man ska inte heller använda gelen under lufttäta bandage eftersom det kan göra att kroppen tar upp mer av läkemedlet och risken för biverkningar ökar. Medicinen kan tillfälligt minska kvinnors möjligheter att bli gravida.',
                                 'Biverkningar': 'En del personer som använder medicinen kan få magbesvär som till exempel illamående, ont i magen eller diarré. Medicinen kan också öka risken för magsår. Andra kan till exempel bli trötta, få ont i huvudet eller hudutslag. Äldre personer får lättare biverkningar av cox-hämmare. Detta gäller särskilt allvarliga symtom från magen som magblödningar. I sällsynta fall har allvarliga hudreaktioner inträffat efter användning av cox-hämmare. Om man får hudutslag eller skador på slemhinnorna ska man genast avbryta behandlingen och kontakta läkare.',
                                 'Graviditet': 'Under de första sex månaderna av graviditeten bör man inte använda medicinen utan att ha rådgjort med läkare. Det finns en risk för att fostret kan påverkas. Under graviditetens sista tre månader ska man inte använda medicinen alls.',
                                 'Amning': 'Man kan använda medicinen när man ammar trots att det verksamma ämnet passerar över i modersmjölken. Om man följer doseringsanvisningarna är det inte sannolikt att barnet påverkas.'},
             '19581115000027' : {'Viktigt': 'Man får inte mer smärtlindring genom att ta en större dos än vad som står på förpackningen eller vad läkaren ordinerat. Om man tar en större dos än rekommenderat finns risk för att man kan få en allvarlig leverskada. Därför ska man inte heller ta Alvedon tillsammans med andra läkemedel som innehåller paracetamol, eftersom den sammanlagda dosen paracetamol kan bli för hög. Man ska kontakta läkare direkt om man har tagit för hög dos eftersom leverskadan märks först efter ett par dagar. Om man missbrukar alkohol ökar risken för leverskada. Om man har alkoholproblem ska man inte använda läkemedel som innehåller paracetamol utan att först ha rådgjort med läkare. Berusningseffekten av alkohol ökar inte genom att man tar paracetamol samtidigt.',
                                 'Biverkningar': 'Vissa personer som använder stolpiller kan känna irritation i ändtarmen. Om man använder Alvedon på rätt sätt och i rätt doser är biverkningar annars ovanliga.',
                                 'Graviditet': 'Man kan använda läkemedlet när man är gravid.',
                                 'Amning': 'Man kan använda medicinen när man ammar trots att det verksamma ämnet passerar över i modersmjölken. Om man följer doseringsanvisningarna är det inte sannolikt att barnet påverkas.'},
             '19581215000033' : {'Viktigt': 'Man får inte mer smärtlindring genom att ta en större dos än vad som står på förpackningen eller vad läkaren ordinerat. Om man tar en större dos än rekommenderat finns risk för att man kan få en allvarlig leverskada. Därför ska man inte heller ta Panodil tillsammans med andra läkemedel som innehåller paracetamol, eftersom den sammanlagda dosen paracetamol kan bli för hög. Man ska kontakta läkare direkt om man har tagit för hög dos eftersom leverskadan märks först efter ett par dagar. Om man missbrukar alkohol ökar risken för leverskada. Om man har alkoholproblem ska man inte använda läkemedel som innehåller paracetamol utan att först ha rådgjort med läkare. Berusningseffekten av alkohol ökar inte genom att man tar paracetamol samtidigt.',
                                 'Biverkningar': 'Vissa personer som använder stolpiller kan känna irritation i ändtarmen. Om man använder Panodil på rätt sätt och i rätt doser är biverkningar annars ovanliga.',
                                 'Graviditet': 'Man kan använda läkemedlet när man är gravid.',
                                 'Amning': 'Man kan använda medicinen när man ammar trots att det verksamma ämnet passerar över i modersmjölken. Om man följer doseringsanvisningarna är det inte sannolikt att barnet påverkas.'},
             '20020208000323' : {'Viktigt': 'Man ska inte använda medicinen om man har en allvarlig njursjukdom. Det är ovanligt att medicinen påverkar förmågan att köra bil eller hantera maskiner. Enstaka personer kan bli dåsiga eller yra av medicinen och man måste själv känna efter hur man reagerar. Man är själv ansvarig för att bedöma om man kan köra bil eller annat motorfordon, eller sköta ett arbete som kräver full uppmärksamhet.',
                                 'Biverkningar': 'En del personer som använder medicinen kan till exempel bli dåsiga eller yra. Vissa kan få ont i huvudet.',
                                 'Graviditet': 'All erfarenhet visar att man kan använda medicinen när man är gravid.',
                                 'Amning': 'Man ska rådgöra med läkare om man behöver använda läkemedlet när man ammar.'},
             'null' :{           'Viktigt': 'Denna information har inte hämtats från 1177 for det här läkemedlet än',
                                 'Biverkningar': 'Denna information har inte hämtats från 1177 for det här läkemedlet än',
                                 'Graviditet': 'Denna information har inte hämtats från 1177 for det här läkemedlet än',
                                 'Amning': 'Denna information har inte hämtats från 1177 for det här läkemedlet än' }


             }

valid_drugs_for_demo = ['19581115000027', '19851206000039','19581215000033' ,'20020208000323']

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
medArray = {}
super_drug_list = {}              # Dictionaryn som all information samlar i och som skickas till olika sidor.
nlpId_list = []

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
    # # set up the connection to SIL
    url = "http://sil40.test.silinfo.se/silapi40/SilDB?wsdl"
    sil = suds.client.Client(url)

    if nlpId_list.count(nplId) == 0:
        nlpId_list.append(nplId)

    # # -----------------------------------------------------------------
    # Make sure we only put in unique ids
    if nplId not in medArray:
        subs = sil.service.getDistributedDrugsByDrugId(nplId, False, -1)
        name = subs[0]['tradeName']
        medArray[name] = nplId

    if not nplId in super_drug_list:
        # # -----------------------------------------------------------------
        # # Hämta data från SIL

        # SuperDrug objekt
        superDrug = sil.service.getSuperDrugsByDrugIdList(nplId, False, -1)

        # Historiska namn
        distDrugsHistNames = sil.service.getDistributedDrugHistoricalNamesByNplId(nplId)

        # Utbytbara läkemedel efter substansgrupp --> Var försiktig här --> kan vara ej utbytbar
        if superDrug[0]['drug']['interchangeableFlag'] == "Y":
            drugsBySubstance = sil.service.getDrugsBySubstanceGroupId(superDrug[0]['drug']['substanceGroupId'], False,
                                                                      -1)  # kan ta lång tid for vissa läkemedel
            substance_count[superDrug[0]['drug']['substanceGroupId']] = substance_count.get(
                superDrug[0]['drug']['substanceGroupId'], 0) + 1
        else:
            drugsBySubstance = 0

        # Liknande läkemedel efter ATC-kod Lista med drug objekt.
        drugsByAtcCode = sil.service.getDrugsByAtcCode(superDrug[0]['atcs'][0]['atcCode'], False, -1)

        # Biverkningar
        drugId_in_list = []
        drugId_in_list.append(str(superDrug[0]['drug']['drugId']))
        biverkningar = sil.service.getSideEffectsByNplIdList(drugId_in_list, "", "") # anropet måste ske med en lista

        # DrugArticles
        drugArticles = sil.service.getDrugArticlesByNplId(nplId)

        # This is not used for now
        substance = sil.service.getSubstancesBySubstanceName("Diklofenak%")
        #print substance

        # # -----------------------------------------------------------------
        # # Konfigurering innan insättning

        #: Lägg till de utbytbara medicinerna i en lista
        interchangeableDrugs = helpers.getUtbytbara(superDrug, drugsBySubstance)

        #: Lägg till de biverkningar efter klassificering i en dict
        biverkningar_efter_klass = helpers.getBiverkningar(biverkningar)

        #: Lägg till de historiska namnen i en lista
        hist_names = helpers.getHistoricNames(superDrug, distDrugsHistNames)

        #: Lägg till förpackning och pris i en dict
        size_and_price = helpers.getSizeAndPrize(drugArticles)

        # Lägg till de liknande medicinerna i en lista
        similarDrugs = []  # Lista med liknande läkemedel --> baserat på ATC-kod
        similarSubstance = []  # Lista med liknande Substans --> baserat på ATC-kod

        for drug in drugsByAtcCode:
            #if drug['strengthGroupId'] == superDrug[0]['drug']['strengthGroupId']:           # Kolla så de har samma stryke grupp.
            #if drug['interchangeableFlag'] == 'Y':                                           # Kolla så de är utbytbara
            if not drug['tradeName'] in similarDrugs:                                         # Kolla så inte samma namn läggs till två gång troligen reduntdant
                #print drug['tradeName']
                similarDrugs.append(drug['tradeName'])
                if not drug['substanceGroupName'] in similarSubstance:
                    if not drug['substanceGroupName'] == 'Ospecificerad':
                        similarSubstance.append(drug['substanceGroupName'])

        #print similarDrugs
        #print similarSubstance


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
        # # Sätt in läkemedlet i våran dictionary som skickas till sidan med information.
        # # key=nlpID --> value=lista med godtyckliga saker [SuperDrug, .. ,etc,]
        super_drug_list[nplId] = superDrug                          # [0] - SuperDrug objekt --> innehåller ATC, distDrug och Drug object
        super_drug_list[nplId].append(hist_names)                   # [1] - Lista med de historiska namnen
        super_drug_list[nplId].append(drugsBySubstance)             # [2] -
        super_drug_list[nplId].append(interchangeableDrugs)         # [3] - Lista med de utbytbara medicinerna
        super_drug_list[nplId].append(similarDrugs)                 # [4] - Lista med de liknanade medicinerna
        super_drug_list[nplId].append(similarSubstance)             # [5] - Lista med de liknanade substanserna
        super_drug_list[nplId].append(biverkningar_efter_klass)     # [6] - Dict med biverkningar key=frekvens -> value=lista över symtom
        super_drug_list[nplId].append(size_and_price)               # [7] - Dict med pris. key=storlek -> value=pris
        super_drug_list[nplId].append(trade_name_length)            # [8] - String. length of the trade name (can be removed)

        if nplId in valid_drugs_for_demo:
            super_drug_list[nplId].append(eleven77[str(nplId)])         # [9] - String. length of the trade name (can be removed)
        else:
            super_drug_list[nplId].append(eleven77['null'])         # [9] - String. length of the trade name (can be removed)


        print super_drug_list[nplId][9]['Viktigt']

    # "nplId_list" and "len" is not used by layout right now
    return render_template('layout.html', nplId_list=nlpId_list, len=len(medArray))


#: Returns the current medicines that are to be shown in the navbar. Called from javascript in info.html
@app.route('/navbarInfo')
def navbarInfo():
    return jsonify(medArray)


#: simple return of number of medicines shown in the navbar
@app.route('/navbar/nrOfIds')
def nrOfIds():
    temp = len(medArray)
    return str(temp)


#: Remove all medicine from the list.
@app.route('/clearNavbar')
def clearAllIds():
    medArray.clear()
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
                           nplId_list=nlpId_list,
                           super_drug_list=super_drug_list,
                           buttons=buttons,
                           atc_dict=atc_dict,
                           glyph_icon=glyph_icon,
                           substance_count=substance_count,
                           word_count=word_count)


# Some test routes

#: For only showing the drug_info
@app.route('/drug_info')
def drug_info():
    return render_template('drug_info.html')


@app.route('/test')
def test():
    return render_template("test.html")


if __name__ == '__main__':
    app.run(debug=True)

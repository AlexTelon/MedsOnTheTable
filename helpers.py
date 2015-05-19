# -*- coding: utf-8 -*-
__author__ = 'johanordin'


pris_databas = { '19851206000039': 56, #Ipren
                 '19581115000027': 34, #Alvedon
                 '19581215000033': 32, #Panodil
                 '20020208000323': 22,  #Cetirizin
                 'null': 'finns ingen prisuppgift än'}
valid_drugs_for_demo = ['19581115000027', '19851206000039','19581215000033' ,'20020208000323']


#: Lägg till de historiska namnen i en lista
def getHistoricNames(superDrug, distDrugsHistNames):
    hist_names = []
    #print '***********'
    #print superDrug[0]['distributedDrugs'][0]['tradeName'][:-1]
    #print distDrugsHistNames
    drug_name = superDrug[0]['distributedDrugs'][0]['tradeName'][:-1]
    trade_name = superDrug[0]['distributedDrugs'][0]['tradeName']

    for name in distDrugsHistNames:
        if name != drug_name and name != trade_name:
            hist_names.append(name)

    # Check if the list is empty
    if not hist_names:
        hist_names.append("Inga historiska namn")
        #print "List is empty"


    return hist_names


#: Lägg till
def getBiverkningar(biverkningar):

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

    return biverkningar_efter_klass


#: Lägg till de utbytbara medicinerna i en lista
def getUtbytbara(superDrug, drugsBySubstance):

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

    return interchangeableDrugs


def getSizeAndPrize(drugArticles):

    size_and_price = {}

    for drugArt in drugArticles:
        if not drugArt['aup'] == 0.0:
            size_and_price[drugArt['packSizeText']] = drugArt['aup']
        else:
            if str(drugArt['nplId']) in pris_databas:
                size_and_price[drugArt['packSizeText']] = pris_databas[str(drugArt['nplId'])]
            else:
                size_and_price[drugArt['packSizeText']] = 99

    if str(drugArt['nplId']) in valid_drugs_for_demo:
        size_and_price['demoPrice'] = pris_databas[str(drugArt['nplId'])]
    else:
        size_and_price['demoPrice'] = pris_databas['null']

    return size_and_price
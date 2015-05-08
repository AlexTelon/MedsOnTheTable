import sys
from mercurial.templatefilters import json
from flask import Flask, render_template, jsonify, url_for
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
    sil = suds.client.Client (url)
    subs = sil.service.getDistributedDrugsByDrugId ("20090916000021", False, -1)
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

#  subs = sil.service.getDrugArticlesByDrugId ("20090916000021", False, -1) Gives information about different packages
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
    sil = suds.client.Client (url)
    for med in medArray:
        subs = sil.service.getDistributedDrugsByDrugId (med, False, -1)
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
    return render_template('card_view.html', ids=medArray)

@app.route('/grid')
def grid():
    return render_template('grid_system.html')


@app.route('/drug_info')
def drug_info():
    return render_template('drug_info.html')




if __name__ == '__main__':
    app.run(debug=True)

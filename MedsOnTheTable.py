from flask import Flask, render_template
import suds
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


app = Flask(__name__)


def print_ddrug(ddrug):
    print "%s %s, %s, [nplId: %s, (%s), MAH: %s] %s" % \
          (ddrug['tradeName'], \
           ddrug['strengthText'], \
           ddrug['drugFormTextSv'], \
           ddrug['nplId'], \
           ddrug['marketedFlag'], \
           ddrug['marketingAuthHolder'], \
           ddrug['exportedFromCountryCode'])


@app.route('/')
def index():
    url = "http://sil40.test.silinfo.se/silapi40/SilDB?wsdl"
    sil = suds.client.Client (url)
    ddrugs = sil.service.getDistributedDrugsByDrugId ("199428000064", True, -1)

    print ddrugs
    return render_template("test.html", info=ddrugs)
    #return 'Hello World!'


@app.route('/search')
def search():
    url = "http://sil40.test.silinfo.se/silapi40/SilDB?wsdl"
    sil = suds.client.Client (url)
    #subs = sil.service.getSubstancesBySubstanceName ("Kodein%")
    #subs = sil.service.getDistributedDrugsByDistributedDrugTradeName ("Citodon", False, -1)
    #subs = sil.service.getDrugsByAtcCode ("N02AA59", False, -1)
    subs = sil.service.getDistributedDrugsByDrugId ("20090916000021", False, -1)
    subs = sil.service.getSILPregnancyLactationWarningsByNplIdList ("20090916000021")
    #subs = sil.service.getSuperDrugsByDistributedDrugTradeName("Aspirin", False, -1)
    #return subs[0]['text']
    print subs
    return render_template("test.html", info=subs)


@app.route('/info')
def info():
    url = "http://sil40.test.silinfo.se/silapi40/SilDB?wsdl"
    sil = suds.client.Client (url)
    ddrug = sil.service.getDistributedDrugsByDrugId("20090916000021", False, -1)
    drugId = ddrug[0]['tradeName']
    Fass = sil.service.getFassDocsByDrugId("20090916000021")
    return Fass[0]['XHtml']
    print "Drug ID is:", ddrug
    #print Fass
    return render_template("test.html", info=ddrug)

#ATC is about what kind of medecine we are talking about, Different groups like blood and nervous system.
# How we get stuff from a ddrug ddrug[0]['nplId'].


@app.route('/med/<brand>')
def brandInfo(brand):
    url = "http://sil40.test.silinfo.se/silapi40/SilDB?wsdl"
    sil = suds.client.Client (url)
    ddrug = sil.service.getDistributedDrugsByDrugId("20090916000021", False, -1)
    drugId = ddrug[0]['tradeName']
    Fass = sil.service.getFassDocsByDrugId("20090916000021")
    return Fass[0]['XHtml']

    #return render_template('medPage.html', brand=brand)
    #return 'Medecinen: %s' % brand;


if __name__ == '__main__':
    app.run(debug=True)

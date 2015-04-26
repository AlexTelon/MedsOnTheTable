from flask import Flask, render_template
import suds
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


app = Flask(__name__)

@app.route('/')
def index():
    url = "http://sil40.test.silinfo.se/silapi40/SilDB?wsdl"
    sil = suds.client.Client (url)
    ddrugs = sil.service.getDistributedDrugsByDistributedDrugTradeName ("Aspirin", True, -1)

    print ddrugs
    return render_template("test.html", info=ddrugs)
    #return 'Hello World!'

@app.route('/s')
def search():
    url = "http://sil40.test.silinfo.se/silapi40/SilDB?wsdl"
    sil = suds.client.Client (url)
    subs = sil.service.getSubstancesBySubstanceName ("ace%")
    print subs
    return render_template("test.html", info=subs)
    #return 'Hello World!'




@app.route('/med/<brand>')
def brandInfo(brand):
    return render_template('medPage.html', brand=brand)
    #return 'Medecinen: %s' % brand;


if __name__ == '__main__':
    app.run(debug=True)

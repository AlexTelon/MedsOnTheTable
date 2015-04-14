from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("layout.html")
    #return 'Hello World!'

@app.route('/med/<brand>')
def brandInfo(brand):
    return 'Medecinen: %s' % brand;


if __name__ == '__main__':
    app.run(debug=True)

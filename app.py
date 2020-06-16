from flask import Flask,request,make_response,render_template
app = Flask(__name__)

@app.route('/')
def hello():
    return render_template("index.html")
if __name__ == '__main__':
    # app.run(host='127.0.0.1',port=80)
    # app.run(debug=True, use_reloader=True,port=8080)
    app.run()

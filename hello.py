from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"
@app.route("/smartapp/index.html")
def GET():
        f = open('index.html', 'r')
        data = f.read()
        f.close()
        return data
if __name__ == "__main__":
    app.run("localhost",8000)

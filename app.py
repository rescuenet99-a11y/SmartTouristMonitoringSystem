from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def tracking():
    return render_template("tracking.html")

if __name__ == "__main__":
    app.run(debug=True)
from flask import *
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

app.secret_key = '1234'

def dateNow():
    now = datetime.now()
    today = now.strftime("%d/%m/%Y %H:%M:%S")
    return today

def load_users():
    df = pd.read_csv('data.csv')
    df = df.astype(str)
    return dict(zip(df.username, df.password))

def get_data():
    df = pd.read_csv('main.csv')
    df = df.astype(str)
    df = df.fillna('-')
    return df.to_dict('records')

users = load_users()

@app.route('/')
def root():
    return render_template("auth.html")

@app.route('/auth/', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
    if username in users and users[username] == password:
        session['username'] = username
        return redirect(url_for("home"))
    else:
        return render_template("auth.html", data={"type": "error"})

@app.route('/home')
def home():
    return render_template("index.html", data=get_data())

@app.route('/save', methods=['GET', 'POST'])
def save():
    data = {
        "name": request.form.get('name'),
        "lastname": request.form.get('lastname'),
        "phone": str(request.form.get('phone'))
    }
    df_new = pd.DataFrame([data])
    if os.path.exists("./main.csv"):
        df_existing = pd.read_csv("./main.csv")
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.drop_duplicates(inplace=True)
    else:
        df_combined = df_new
    df_combined.to_csv("./main.csv", index=False)
    return redirect(url_for("home"))

@app.route('/delete/<name>', methods=['GET'])
def delete(name: str):
    df_existing = pd.read_csv("./main.csv")
    df = df_existing[df_existing['name'] != name]
    df.to_csv("./main.csv", index=False)
    return redirect(url_for("home"))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('root'))


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    df_existing = pd.read_csv("./main.csv")
    updated_data = request.form.to_dict()

    df_existing['phone'] = df_existing['phone'].astype(str)
    updated_data['old_phone'] = str(updated_data['old_phone'])
    updated_data['phone'] = str(updated_data['phone'])

    df_existing.loc[df_existing['name'] == updated_data['old_name'], 'name'] = updated_data['name']
    df_existing.loc[df_existing['lastname'] == updated_data['old_lastname'], 'lastname'] = updated_data['lastname']
    df_existing.loc[df_existing['phone'] == updated_data['old_phone'], 'phone'] = updated_data['phone']

    df_existing.to_csv("./main.csv", index=False)
    
    return redirect(url_for("home"))

@app.route("/print", methods=['GET'])
def print():
    df = pd.read_csv("./main.csv")
    table_html = df.to_html(classes='table table-striped table-sm table-hover', index=False)
    today = dateNow()
    scripting = """
        <script>
            function printAndClose() {
                let closeWindow = setTimeout(function() {
                    window.close()
                }, 500)
                window.print()
                window.onafterprint = function() {
                    clearTimeout(closeWindow)
                }
            }
        </script>
    """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>User Data</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    {scripting}
    <body onload="printAndClose()">
        <div class="container">
            <h1 class="mt-5">ข้อมูลรายชื่อ</h1>
            <hr>
            {table_html}
            <div align="right">
                <p>วันที่พิมพ์: {today}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html)
    
if __name__ =="__main__":
    app.run(host="0.0.0.0", port=99, debug=True)
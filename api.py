from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse
from pydantic import BaseModel
import sqlite3, uuid, csv, atexit

atexit.register(lambda: conn.close())


app = FastAPI()


conn = sqlite3.connect('autoinsurance.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS queue (
id TEXT,
first_name TEXT,
last_name TEXT,
street_address TEXT,
city TEXT,
zip TEXT,
phone TEXT,
email TEXT
); """
)
conn.commit()


class AutoInsurance(BaseModel):
    first_name: str
    last_name: str
    street_address: str
    city: str 
    zipp: str
    phone: str
    email: str


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Logs</title>
    </head>
    <body>
        <div>
        <a href='/download' style='float:right'>Download csv</a>
        </div>
        <h3>Id, First Name, Last Name, Street Address, Zip, Phone, Email, Status</h2>
        <div id="log-body"></div>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('log-body')
                var content = document.createTextNode(event.data)
                messages.innerHTML = content.textContent
            };
             setInterval(() => ws.send('sefesfae'), 100)
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
      data = await websocket.receive_text()
      cmd = cur.execute("SELECT * FROM log")
      data = cmd.fetchall()
      new_data = "<br/>".join([", ".join(x) for x in data])
      await websocket.send_text(new_data)


@app.get('/queued')
def queued():
    cmd = cur.execute("SELECT * FROM queue")
    data = cmd.fetchall()
    return data


@app.post('/add-to-queue')
async def automate(auto_insurance: AutoInsurance):
  idd = str(uuid.uuid4())
  cur.execute(f"""INSERT INTO queue (
    id, 
    first_name, 
    last_name, 
    street_address, 
    city, 
    zip, 
    phone, 
    email
    ) 
    VALUES ({"?, "*7}?)""", (
        idd, 
        auto_insurance.first_name, 
        auto_insurance.last_name,  
        auto_insurance.street_address, 
        auto_insurance.city, 
        auto_insurance.zipp, 
        auto_insurance.phone, 
        auto_insurance.email))
        
  conn.commit()
  return auto_insurance

@app.get('/download')
def download_as_csv():
    cmd = cur.execute("SELECT * FROM log")
    
    with open('logs.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Id", 
                "First Name", 
                "Last Name", 
                "Street Address", 
                "zip", 
                "Phone", 
                "email", 
                "Year", 
                "Make", 
                "Model", 
                "Insured From", 
                "DOB", 
                "Gender", 
                "Device", 
                "Education", 
                "Rating", 
                "Status"
            ]
        )
        writer.writerows(cmd)
    return FileResponse('logs.csv', media_type='text/csv', filename='logs.csv')
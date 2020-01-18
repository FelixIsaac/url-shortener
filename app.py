import config
import mysql.connector
import flask
import random
import string
import json
import re

# initialize SQL connection
sql = mysql.connector.connect(
  host= config.mysql['host'],
  user= config.mysql['user'],
  passwd= config.mysql['passwd'],
  auth_plugin='mysql_native_password',
  database="links"
)

cursor = sql.cursor(buffered=True)

# check if necessary table is there
def checkLinksTable():
  cursor.execute("SHOW TABLES LIKE 'links'")
  if (cursor.fetchone() == None):
    cursor.execute("CREATE TABLE links (id INT AUTO_INCREMENT PRIMARY KEY, original VARCHAR(2048), shortened VARCHAR(4))")

# generate shortened link 
def shorten(length = 4):
  letters = string.ascii_letters + string.digits
  return ''.join(random.choice(letters) for i in range(length))

# initialize flask
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# landing page
@app.route('/', methods=['GET', 'POST'])
def home():
  if (flask.request.method == 'GET'):
    return flask.render_template('index.html')
  else:
    original = json.loads(flask.request.data)['original']
    
    # check if the original link is already shortened
    cursor.execute("SELECT shortened FROM links WHERE original = %(o)s", {
      'o': original
    })
    
    result = cursor.fetchone()
    
    if (result):
      return json.dumps({
        'error': False,
        'message': "/" + result[0]
      })
    else:
      # check if URL is valid
      if re.match('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', original):
        shorted = shorten()
        
        cursor.execute("INSERT INTO links (original, shortened) VALUES (%(o)s, %(s)s)", {
          'o': original,
          's': shorted
        })
        
        sql.commit()
        
        return flask.Response(response= json.dumps({
          'error': False,
          'message': "/" + shorted
        }), status=200, mimetype='application/json')
      else:
        return flask.Response(response= son.dumps({
          'error': True,
          'message': 'Invalid URL'
        }), status=400, mimetype='application/json')

# Get long link from shortened
@app.route('/<shorten>', methods=['GET'])
def short(shorten):
  cursor.execute("SELECT original FROM links WHERE shortened = %(s)s", {
    's': shorten
  })
  
  result = cursor.fetchone();
  print(result)
  
  if (result):  
    return flask.redirect(result[0]);
  else: return flask.redirect('/')

app.run()
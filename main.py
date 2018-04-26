
from microWebSrv import MicroWebSrv
import rtthread
import json
import dht12
from machine import Pin, I2C

# ----------------------------------------------------------------------------

@MicroWebSrv.route('/test')
def _httpHandlerTestGet(httpClient, httpResponse) :
    content = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>TEST GET</title>
        </head>
        <body>
            <h1>TEST GET</h1>
            Client IP address = %s
            <br />
            <form action="/test" method="post" accept-charset="ISO-8859-1">
                First name: <input type="text" name="firstname"><br />
                Last name: <input type="text" name="lastname"><br />
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """ % httpClient.GetIPAddr()
    httpResponse.WriteResponseOk( headers        = None,
                                  contentType    = "text/html",
                                  contentCharset = "UTF-8",
                                  content        = content )


@MicroWebSrv.route('/test', 'POST')
def _httpHandlerTestPost(httpClient, httpResponse) :
    formData  = httpClient.ReadRequestPostedFormData()
    firstname = formData["firstname"]
    lastname  = formData["lastname"]
    content   = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>TEST POST</title>
        </head>
        <body>
            <h1>TEST POST</h1>
            Firstname = %s<br />
            Lastname = %s<br />
        </body>
    </html>
    """ % ( MicroWebSrv.HTMLEscape(firstname),
            MicroWebSrv.HTMLEscape(lastname) )
    httpResponse.WriteResponseOk( headers        = None,
                                  contentType    = "text/html",
                                  contentCharset = "UTF-8",
                                  content        = content )

@MicroWebSrv.route('/sysdata')
def _httpHandlerTestGet(httpClient, httpResponse) :
    sensor.measure()
    
    temperature = sensor.temperature()
    humidity    = sensor.humidity()
    #key_v       = key.value()
    
    content ={
        'status'      : 200,
        'body'        :{
        'status'      : 1,
        'result'      :{
            "versions":"3.0.3",
            "getTime":"1497594033",
            "cpuUtilization":"0.35",
            "presentUtilization":"0.35",
            "ipAddress":"192.168.0.1",
            "key":1,
            "sensors":"temperature:{temperature},humidity:{humidity},".format(temperature = temperature,humidity = humidity)}
        }
        }

    json_content = json.dumps(content)
    httpResponse.WriteResponseOk( headers        = None,
                                  contentType    = "text/json",
                                  contentCharset = "UTF-8",
                                  content        = json_content)

@MicroWebSrv.route('/edit/<index>')             # <IP>/edit/123           ->   args['index']=123
@MicroWebSrv.route('/edit/<index>/abc/<foo>')   # <IP>/edit/123/abc/bar   ->   args['index']=123  args['foo']='bar'
@MicroWebSrv.route('/edit')                     # <IP>/edit               ->   args={}
def _httpHandlerEditWithArgs(httpClient, httpResponse, args={}) :
    content = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>TEST EDIT</title>
        </head>
        <body>
    """
    content += "<h1>EDIT item with {} variable arguments</h1>"\
        .format(len(args))
    
    if 'index' in args :
        content += "<p>index = {}</p>".format(args['index'])
    
    if 'foo' in args :
        content += "<p>foo = {}</p>".format(args['foo'])
    
    content += """
        </body>
    </html>
    """
    httpResponse.WriteResponseOk( headers        = None,
                                  contentType    = "text/html",
                                  contentCharset = "UTF-8",
                                  content        = content )

# ----------------------------------------------------------------------------

def _acceptWebSocketCallback(webSocket, httpClient) :
    print("WS ACCEPT")
    webSocket.RecvTextCallback   = _recvTextCallback
    webSocket.RecvBinaryCallback = _recvBinaryCallback
    webSocket.ClosedCallback     = _closedCallback

def _recvTextCallback(webSocket, msg) :
    print("WS RECV TEXT : %s" % msg)
    webSocket.SendText("Reply for %s" % msg)

def _recvBinaryCallback(webSocket, data) :
    print("WS RECV DATA : %s" % data)

def _closedCallback(webSocket) :
    print("WS CLOSED")

# ----------------------------------------------------------------------------

#routeHandlers = [
#   ( "/test",  "GET",  _httpHandlerTestGet ),
#   ( "/test",  "POST", _httpHandlerTestPost )
#]

i2c = I2C(1)
sensor = dht12.DHT12(i2c)
# led = Pin(("LED1", 52), Pin.OUT_PP)
# key = Pin(("KEY", 125), Pin.IN, Pin.PULL_UP) 

srv = MicroWebSrv(webPath='www/')
srv.MaxWebSocketRecvLen     = 256
srv.WebSocketThreaded       = False
srv.AcceptWebSocketCallback = _acceptWebSocketCallback
srv.Start(threaded=False)

# ----------------------------------------------------------------------------

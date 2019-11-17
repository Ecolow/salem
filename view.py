#!/usr/bin/env python3

import asyncio
import aiohttp.web

header = '''
<!DOCTYPE html>
<body>
<img src="/static/header_logo.png" alt="Icon" height="70" width="180">
'''

search_bar = '''
    <form action="javascript:WebSocketTest()">
      <input id="searchBar.query" type="text" placeholder="What...">
      <input id="searchBar.location" type="text" placeholder="Where..." value="London">
      <button type="submit">Submit</button>
    </form>
'''

footer = "</body></html>"

script = '''<script type = "text/javascript">
function WebSocketTest() {
    var resultDiv = document.getElementById("results");
    
    // cleaning up the previous results
    while (resultDiv.firstChild) {
        resultDiv.removeChild(resultDiv.firstChild);
    }
    var Socket = new WebSocket("ws://localhost:8080/socket");
    
    Socket.onopen = function() {
        var query = document.getElementById("searchBar.query").value;
        var location = document.getElementById("searchBar.location").value;

        var responseObject = {"query" : query, "location" : location};
        var responseJson = JSON.stringify(responseObject)

        Socket.send(responseJson);

    }

    Socket.onmessage = function (event) {
        var received = event.data;
        var offer = document.createElement('offer');

        offer.innerHTML = '<p>' + received + '</p>';
        resultDiv.appendChild(offer);
    }
}
</script>
'''

offer_div = '''<br>
<h3> {title} </h3>
<p> Company: {company} <br> Salary: {salary} <br> {skills} <br>
'''

body = '''   
<body>
    <div id = "results">
    </div>  
</body> 
'''
class WebView:
    def __init__(self, control_interface):
        self.control_interface = control_interface

    def run(self):
        app = aiohttp.web.Application()
        app.add_routes([aiohttp.web.get('/socket', self.socket),
                        aiohttp.web.get('/', self.index)])
        app.router.add_static('/static/', path='./views/static/')
        aiohttp.web.run_app(app)

    async def socket(self, request):
        ws = aiohttp.web.WebSocketResponse()
        await ws.prepare(request)
        print("Websocket ready !")
        data = None
        async for msg in ws :
            data = msg.json()
            break
        print(data['query'])
        async for offer in self.control_interface(data['query']):
            res_div = offer_div.format(title=offer.title, company=offer.company, 
                                    salary=offer.salary, skills=offer.skills)
            await ws.send_str(res_div)

        # close the websocket once done 
        await ws.close()
        print("Websocket closed.")

    async def index(self, request):
        resp = header + search_bar + script + body + footer
        return aiohttp.web.Response(text=resp, content_type='text/html')


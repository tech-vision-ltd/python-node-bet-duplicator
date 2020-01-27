const http = require('http');
const betAgent = require('./betAgent');

const hostname = '127.0.0.1';
const port = 3000;

const server = http.createServer(function (request, response) {
    if (request.method === 'POST') {
        console.log('POST');
        let body = '';
        request.on('data', function (data) {
            body += data;
            console.log('Partial body: ' + body);
        });
        request.on('end', async function () {
            console.log('Body: ' + body);
            let betData = JSON.parse(body);
            let betId = betData.betId;
            let sportId = betData.sportId;
            let eventId = betData.eventId;
            let stake = betData.stake;
            let teamType = betData.teamType;
            console.log(betId, sportId, eventId, stake, teamType);
            try {
                let bRepeat = true;
                while (bRepeat) {
                    let betInfoResponse = await betAgent.getMotherBetInfo();
                    if (betInfoResponse.isSuccess) {
                        bRepeat = false;
                        let betInfoArray = betInfoResponse.data;
                        for (let betInfoItem of betInfoArray) {
                            if (betInfoItem.id === betId.toString()) {
                                let betType = betInfoItem.betType.slice(0, betInfoItem.betType.lastIndexOf(" "));
                                let placeBetResponse = await betAgent.duplicateBets(betId, sportId, betType, eventId, teamType, stake);
                                console.log(placeBetResponse);
                            }
                        }
                        console.log(betInfoArray);
                    }
                }
            } catch (e) {

            }
            response.writeHead(200, {'Content-Type': 'application/json'});
            let data = {data: 'post received'};
            response.end(JSON.stringify(data));
        })
    } else {
        console.log('GET');
        response.writeHead(200, {'Content-Type': 'text/html'});
        response.end('server is running ...')
    }
});

server.listen(port, hostname);
console.log(`Listening at http://${hostname}:${port}`);

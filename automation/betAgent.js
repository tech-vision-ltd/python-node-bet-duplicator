const nightmare = require('nightmare');
const sqlite3 = require('sqlite3').verbose();
let nmAgent = nightmare({show: true, waitTimeOut: 60000, height: 900, width: 1600, openDevTools: {mode: 'detach'}});
const siteUrl = "https://www.ps3838.com";


let motherName = "";
let motherPass = "";
let sonsArray = [];
let database = new sqlite3.Database('../database.db');


getMotherBetInfo = async () => {
    return new Promise(async (resolve, reject) => {
        let nmAgent = nightmare({
            show: true,
            waitTimeOut: 60000,
            height: 900,
            width: 1600,
            openDevTools: {mode: 'detach'}
        });
        nmAgent.goto(siteUrl)
            .wait('#login-panel input[name="loginId"]')
            .type('#login-panel input[name="loginId"]', motherName)
            .wait('#login-panel input[name="password"]')
            .type('#login-panel input[name="password"]', motherPass)
            .click('#login')
            .wait(10000)
            // .wait('#my-bets-content .my-bets .bet')
            .evaluate(() => {
                let retArray = [];
                let betElements = document.querySelectorAll('#my-bets-content .my-bets .bet');
                for (let betElement of betElements) {
                    let retItem = {};
                    let idElement = betElement.querySelector('.wager-id');
                    if (idElement) {
                        retItem.id = idElement.innerText;
                    }
                    let leagueElement = betElement.querySelector('span.league');
                    if (leagueElement) {
                        retItem.league = leagueElement.innerText;
                    }
                    let betTypeElement = betElement.querySelector('span.bet-type');
                    if (betTypeElement) {
                        retItem.betType = betTypeElement.innerText;
                    }

                    retArray.push(retItem);
                }
                return retArray;
            })
            .end()
            .then(result => {
                resolve({
                    isSuccess: true,
                    data: result
                })
            })
            .catch(e => {
                console.log(e.message);
                resolve({
                    isSuccess: false,
                })
            });
    })
};

duplicateBets = async (betId, sportId = "12", betType = "Map 1", eventId = "1087842378", teamType = "0", stake = "5.00") => {
    return new Promise(async resolve => {
        try {
            for (let user of sonsArray) {
                let userName = user.name;
                let userPass = user.pass;

                let bRepeat = true;
                while (bRepeat) {
                    let placeBetResponse = await placeBet(userName, userPass, sportId, betType, eventId, teamType, stake);
                    if (placeBetResponse.isSuccess)
                        bRepeat = false;
                }
            }
            let ret = await markAsPlaced(betId);
            console.log('mark as placed ', betId, ': ', ret);
        } catch (e) {
            console.log(e.message)
        }
        resolve(true);
    });
};

placeBet = async (userName, userPass, sportId = "12", betType = "Map 1", eventId = "1087842378", teamType = "0", stake = "5.00") => {
    return new Promise(async (resolve, reject) => {
            // start placing bet
            let menuTitle = betType;
            if (sportId.toString() === "29" && betType ===  "Match") {
                menuTitle = "Live";
            }
            let nmAgent = nightmare({
                show: true,
                waitTimeOut: 60000,
                height: 900,
                width: 1600,
                openDevTools: {mode: 'detach'}
            });
            nmAgent.goto(siteUrl)
                .wait('#login-panel input[name="loginId"]')
                .type('#login-panel input[name="loginId"]', userName)
                .wait('#login-panel input[name="password"]')
                .type('#login-panel input[name="password"]', userPass)
                .click('#login')
                .wait(10000)
                .goto(siteUrl + "/en/sports")
                .wait(`#sports-menu ul.sp-list li[data-id="${sportId}"]`) // for E sport, sportId = 12
                .click(`#sports-menu ul.sp-list li[data-id="${sportId}"]`)
                .wait(`#sports-menu ul.sp-list li[data-id="${sportId}"] ul.mk-type li[title="${menuTitle}"]`) // betType = Map 1
                .click(`#sports-menu ul.sp-list li[data-id="${sportId}"] ul.mk-type li[title="${menuTitle}"]`)
                .wait(`table#e${eventId} tr.mkline a.odds[data-team-type="${teamType}"]`) // team1 -> 0, team2 -> 1
                .click(`table#e${eventId} tr.mkline a.odds[data-team-type="${teamType}"]`)
                .wait('#betslip-content div.bet-stake input[name="stake"]')
                .type('#betslip-content div.bet-stake input[name="stake"]', stake)
                .click('#betslip-content div.betslip-options input[name="acceptBetterOdds"]')
                .wait(1000)
                .click('#betslip-content div.betslip-buttons input[type="submit"]')
                .wait(3000)
                .wait('#alert')
                .click('div.ui-dialog-buttonset button.pbtn') // for ok, button.pbtn ; cancel button.cancelBtn
                .end()
                .then(() => {
                    resolve({
                        isSuccess: true,
                    })
                })
                .catch(e => {
                    console.log(e.message);
                    resolve({
                        isSuccess: false,
                    })
                })
        }
    )
};

markAsPlaced = async (betId) => {
    return new Promise(resolve => {
        try {
            const stmt = database.prepare("UPDATE placed_bet SET is_duplicated = ? WHERE bet_id = ?");
            const updates = stmt.run(1, betId);
        } catch (e) {
            console.log("Failed to update bet data");
        } finally {
            resolve(true);
        }
    });
};

readUserData = async () => {
    return new Promise(resolve => {
        try {
            database.all("SELECT * FROM user", (err, rows) => {
                if (err) {
                    console.log(err);
                    return;
                }
                rows.forEach(row => {
                    console.log(`${(new Date()).toLocaleTimeString()}, signal_id = ${row.name}, ai_id = ${row.pass}`);
                    if (row.is_mother === 1) {
                        motherName = row.name;
                        motherPass = row.pass;
                    } else {
                        sonsArray.push({
                            name: row.name,
                            pass: row.pass
                        })
                    }
                });
                resolve(true);
            });
        } catch (e) {
            console.log('Failed to read last status data');
        }
    });
};

test = async () => {
    try {

        for (let son of sonsArray) {
            let ret = await placeBet(son.name, son.pass);
        }
        console.log('finished');

    } catch (e) {
        console.log(e.message)
    }
};

(async () => {
    let ret = await readUserData();
    // test();
})();

module.exports.getMotherBetInfo = getMotherBetInfo;
module.exports.placeBet = placeBet;
module.exports.duplicateBets = duplicateBets;

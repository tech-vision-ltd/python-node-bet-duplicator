import base64
import requests
from enum import Enum
from datetime import timedelta, datetime
import threading
import time
from settings import AppData
import uuid
import json

"""
Script to connect to ps3838 API
URL to check API User Guide:
https://www.tender88.com/static/index.php/es-es/help/api-user-guide-es-es
In order to access PS3838 API you must have a funded account.
"""


class BetAccount:
    def __init__(self, name: str = "", password: str = ""):
        self.user_name = name
        self.user_pass = password
        self.API_ENDPOINT = 'http://api.ps3838.com'

    # Available Request Methods
    class HttpMethod(Enum):
        GET = 'GET'
        POST = 'POST'

    def get_headers(self, request_method: HttpMethod) -> dict:
        headers = {}
        headers.update({'Accept': 'application/json'})
        headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0'})

        if request_method is self.HttpMethod.POST:
            headers.update({'Content-Type': 'application/json'})

        headers.update({'Authorization': 'Basic {}'.format(
            base64.b64encode((bytes("{}:{}".format(self.user_name, self.user_pass), 'utf-8'))).decode())
        })

        return headers

    def get_operation_endpoint(self, operation: str) -> str:
        return '{}{}'.format(self.API_ENDPOINT, operation)

    # def get_sports():
    #     operation = '/v1/sports'
    #     req = requests.get(
    #         get_operation_endpoint(operation),
    #         headers=get_headers(HttpMethod.GET)
    #     )
    #     return req.json()
    #
    #
    # def get_leagues(sport_id=1):
    #     operation = '/v1/leagues?sportId={}'.format(sport_id)
    #     req = requests.get(
    #         get_operation_endpoint(operation),
    #         headers=get_headers(HttpMethod.GET)
    #     )
    #     return req.json()
    #
    #
    # def get_fixtures():
    #     operation = '/v1/fixtures?sportid=29'
    #     res = requests.get(
    #         get_operation_endpoint(operation),
    #         headers=get_headers(HttpMethod.GET)
    #     )
    #     return res  # .json()

    def get_bets(self, days: float = 0, hours: float = 0, minutes: float = 0):
        # valid date example: 2015-12-29T23:59:59Z

        from_date = datetime.strftime(datetime.utcnow() - timedelta(days=days, hours=hours, minutes=minutes),
                                      "%Y-%m-%dT%H:%M:%SZ")
        to_date = datetime.strftime(datetime.utcnow(), "%Y-%m-%dT%H:%M:%SZ")
        operation = '/v3/bets?betlist=RUNNING&fromDate={}&toDate={}'.format(from_date, to_date)
        headers = self.get_headers(self.HttpMethod.GET)
        url = self.get_operation_endpoint(operation)
        res = requests.get(
            url=url,
            headers=headers
        )
        return res.json()

    def place_bets(self, new_bet):
        operation = '/v2/bets/place'
        headers = self.get_headers(self.HttpMethod.POST)

        res = requests.post(
            self.get_operation_endpoint(operation),
            data=new_bet,
            headers=self.get_headers(self.HttpMethod.POST)
        )
        print(res.json())

    def get_line(self, sport_id, league_id, event_id, period_number, bet_type, handicap, team="", side=""):
        operation = '/v2/line?sportId={}&leagueId={}&eventId={}&periodNumber={}&betType={}&handicap={}'.format(
            sport_id, league_id, event_id, period_number, bet_type, handicap
        )
        res = requests.get(
            self.get_operation_endpoint(operation),
            headers=self.get_headers(self.HttpMethod.GET)
        )
        return res.json()


class BetManager:
    def __init__(self):
        # API ENDPOINT
        self.app_data = AppData()
        self.app_data.read_data()
        self.current_bets = []
        self.mother = BetAccount(self.app_data.account_mother_name, self.app_data.account_mother_pass)
        self.sons = []
        for son_data in self.app_data.accounts_son:
            son = BetAccount(son_data['name'], son_data['pass'])
            self.sons.append(son)
        # self.monitor_process = multiprocessing.Process(target=self.monitor)
        self.monitor_thread = None

    class OddsFormat(Enum):
        AMERICAN = 'AMERICAN'
        DECIMAL = 'DECIMAL'
        HONGKONG = 'HONGKONG'
        INDONESIAN = 'INDONESIAN'
        MALAY = 'MALAY'

    class BOOLEAN(Enum):
        FALSE = 'FALSE'
        TRUE = 'TRUE'

    class WinRiskType(Enum):
        RISK = 'RISK'
        WIN = 'WIN'

    class BetType(Enum):
        MONEYLINE = 'MONEYLINE'
        TEAM_TOTAL_POINTS = 'TEAM_TOTAL_POINTS'
        SPREAD = 'SPREAD'
        TOTAL_POINTS = 'TOTAL_POINTS'
        SPECIAL = 'SPECIAL'

    class BetStatus(Enum):
        ACCEPTED = 'ACCEPTED'
        CANCELLED = 'CANCELLED'
        LOSE = 'LOSE'
        PENDING_ACCEPTANCE = 'PENDING_ACCEPTANCE'
        REFUNDED = 'REFUNDED'
        REJECTED = 'REJECTED'
        WON = 'WON'

    def get_mother_bets(self):
        return self.mother.get_bets(days=29)

    def monitor(self):
        while True:
            if self.app_data.status_is_running == 0:
                print(datetime.now(), " -> ", "monitor thread stopped")
                return

            bets_response = self.get_mother_bets()
            print(datetime.now(), " -> ", bets_response)
            self.current_bets = bets_response['straightBets']
            for bet_response in bets_response['straightBets']:
                print(bet_response)
                # TODO: check bet status
                if bet_response['betStatus'] != self.BetStatus.ACCEPTED.value:
                    continue

                if self.app_data.check_if_exists_or_duplicated(bet_id=bet_response['betId']):
                    continue

                self.app_data.add_bet(bet_id=bet_response['betId'])

                bet_uuid = '{}'.format(uuid.uuid1())
                win_risk_stake = self.WinRiskType.RISK.value
                stake = bet_response['risk'] * self.app_data.status_percentage / 100
                if stake < 5.00:
                    stake = 5.00
                bet_team = "0"
                if bet_response['teamName'] == bet_response['team1']:
                    bet_team = '0'
                if bet_response['teamName'] == bet_response['team2']:
                    bet_team = '1'

                # line = self.mother.get_line(
                #     sport_id=bet_response['sportId'],
                #     league_id=bet_response['leagueId'],
                #     event_id=bet_response['eventId'],
                #     period_number=bet_response['periodNumber'],
                #     bet_type=bet_response['betType'],
                #     handicap=bet_response['handicap'],
                #     team=bet_response['teamName']
                # )
                # print(line)
                # line['lineId']
                bet_line_id = 1

                bet_request = {}
                # bet_request.update({
                #     'uniqueRequestId': bet_uuid,
                #     'acceptBetterLine': self.BOOLEAN.TRUE.value,
                #     'oddsFormat': bet_response['oddsFormat'],
                #     'betId': bet_response['betId'],
                #     'stake': stake,
                #     'winRiskStake': win_risk_stake,
                #     'sportId': bet_response['sportId'],
                #     'eventId': bet_response['eventId'],
                #     'periodNumber': bet_response['periodNumber'],
                #     'betType': bet_response['betType'],
                #     'lineId': bet_line_id,
                #     'team': 'TEAM1',
                # })

                bet_request.update({
                    'betId': bet_response['betId'],
                    'stake': stake,
                    'sportId': bet_response['sportId'],
                    'eventId': bet_response['eventId'],
                    'betType': bet_response['betType'],
                    'teamType': bet_team
                })
                res = self.duplicate_bets(json.dumps(bet_request))
                print(res)
            time.sleep(self.app_data.status_delay_in_seconds)

    def start(self):
        self.app_data.status_is_running = 1
        self.monitor_thread = threading.Thread(target=self.monitor)
        self.monitor_thread.start()

    def stop(self):
        self.app_data.status_is_running = 0
        # self.monitor_process.terminate()
        # self.app_data.write_data()

    def duplicate_bets(self, bet_request: dict):
        headers = {}
        headers.update({'Accept': 'application/json'})
        headers.update({'Content-Type': 'application/json'})

        res = requests.post(
            url="http://127.0.0.1:3000",
            data=bet_request,
            headers=headers
        )
        print(res.json())
        return res.json()
        # for son in self.sons:
        #     son.place_bets(new_bet=bet_request)
        # return True


# bet_manager = BetManager()
# print(bet_manager.mother.get_bets(days=2))

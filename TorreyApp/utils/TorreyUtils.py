import logging
import time
from datetime import datetime, timedelta
import typing
import json
import smtplib
import ssl
import requests
import json

PAGE_URL = "https://foreupsoftware.com/index.php/booking/index/19347#/"
LOGIN_URL = "https://foreupsoftware.com/index.php/api/booking/users/login"
API_URL = "https://foreupsoftware.com/index.php/api/booking/"
LOGIN_FORM = {
    "username": "",
    "password": "",
    "booking_class_id": "",
    "api_key": "no_limits",
    "course_id": 19347,
}
COURSE_IDS = [
    {"name":"torrey_north", "id": 1468},
    {"name":"torrey_south", "id": 1487}
]
LOGIN_HEADERS = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}

logger = logging.getLogger(__name__)


class TorreyUtils:
    PORTAL_USER = ""
    PORTAL_PWD = ""
    EMAIL_USER = ""
    EMAIL_PWD = ""
    
    def __init__(self):
        with open('../utils_secrets.json') as f:
            contents = json.loads(f.read())
            self.PORTAL_USER = contents.get("PORTAL_USER")
            self.PORTAL_PWD = contents.get("PORTAL_PWD")
            self.EMAIL_USER = contents.get("EMAIL_USER")
            self.EMAIL_PWD = contents.get("EMAIL_PWD")
    
    def get_next_weekends(self) -> typing.Tuple[str]:
        today = datetime.today()
        deltaSat = timedelta((12 - today.weekday()) % 7)
        deltaSun = deltaSat + timedelta(days=1)
        nextSat = (today + deltaSat).strftime("%m-%d-%y")
        nextSun = (today + deltaSun).strftime("%m-%d-%y")
        return (nextSat, nextSun)


    def get_times(self) -> typing.Dict:
        dates = self.get_next_weekends()
        with requests.Session() as sesh:
            init_page = sesh.get(PAGE_URL)
            cookies = init_page.cookies
            login_form = LOGIN_FORM.copy()
            login_form["username"] = self.PORTAL_USER
            login_form["password"] = self.PORTAL_PWD
            logger.error("Attempting to login.")
            logger.error(cookies)
            login = sesh.post(LOGIN_URL, login_form, headers=LOGIN_HEADERS, cookies=cookies)
            logger.error(str(login.content))
            if login.status_code != 200:
                logger.error(f"Login failed. Error: {login.status_code}")
                return None
            results = {}
            for course in COURSE_IDS:
                results[course["name"]] = {}
                for date in dates:
                    # Hardcoded to get times from 6am to 12:00pm
                    times_url = (
                        API_URL + f"times?time=all&date={date}&holes=18"
                        "&booking_class=888&startTime=0600&endTime=1200&schedule_id=1487&schedule_ids%5B%5D=0&schedule_ids%5B%5D=1468"
                        f"&schedule_ids%5B%5D={course['id']}&specials_only=0&api_key=no_limits"
                    )
                    logger.error(f"Getting tee times for {course['name']} on {date}")
                    tee_times = sesh.get(times_url, cookies=login.cookies)
                    logger.error(str(tee_times.content))
                    if tee_times.status_code != 200:
                        logger.error(f"Failed to get tee times. Error: {tee_times.status_code}")
                    try:
                        results[course["name"]][date] = (json.loads(tee_times.content))
                    except json.JSONDecodeError as err:
                        logger.error(f"Unable to decode tee times content: {err}")
            return results
                

    def send_notification(self, message_body: str, recipient: str):
        message = """Subject: Tee Times Found


    """
        message += message_body
        port = 465
        username = self.EMAIL_USER
        password = self.EMAIL_PWD
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            logger.error(f"Sending email {message}")
            server.login(username, password)
            server.sendmail(username, recipient, message)
    

    def filter_times(self, data: typing.Dict, filters: typing.Dict) -> str:
        # allowed filters: num_players, list of courses
        result = ""
        # Data format: courseName->date->available_spots
        if not data:
            logger.error("No data to parse!")
            return result
        for course in data:
            if course in filters.get("courses"):
                msg = ""
                for date in data[course]:
                    for entry in data[course][date]:
                        if entry["available_spots"] >= filters.get("num_players",4):
                            if not msg:
                                msg = f"Times for {course}\n"
                            msg += f"\t{entry.get('players')} players at {entry.get('time')}\n"
                if msg:
                    result += msg
        return result

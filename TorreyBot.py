import logging
import argparse
import time
import getpass
import typing
import requests
import json
import smtplib
import ssl

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
LOGIN_HEADERS = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
emails = ["maxlutt55@gmail.com"]

def get_times(username: str, password: str, date: str, players: int) -> typing.Optional[typing.Dict]:
    with requests.Session() as sesh:
        init_page = sesh.get(PAGE_URL)
        cookies = init_page.cookies
        login_form = LOGIN_FORM.copy()
        login_form["username"] = username
        login_form["password"] = password
        logging.info("Attempting to login.")
        login = sesh.post(LOGIN_URL, login_form, headers=LOGIN_HEADERS, cookies=cookies)
        logging.debug(str(login.content))
        if login.status_code != 200:
            logging.error(f"Login failed. Error: {login.status_code}")
            return None
        times_url = (
            API_URL + 
            f"times?time=all&date={date}&holes=18&players={players}"
            "&booking_class=888&schedule_id=1487&schedule_ids%5B%5D=0&schedule_ids%5B%5D=1468"
            "&schedule_ids%5B%5D=1487&specials_only=0&api_key=no_limits"
        )
        logging.info(f"Getting tee times for {date}")
        tee_times = sesh.get(times_url, cookies=login.cookies)
        logging.debug(str(tee_times.content))
        if tee_times.status_code != 200:
            logging.error(f"Failed to get tee times. Error: {tee_times.status_code}")
            return None
        return str(tee_times.content)
        


def send_notification(times_data):
    message = """Subject: Tee Times Found

    
    """
    for entry in times_data:
        players = entry.get("available_spots")
        tee_time = entry.get("time")
        message += f"Found time for {players} players at {tee_time}\n"
    port = 465
    username = input("Enter username: ")
    password = getpass.getpass(prompt="Password: ", stream=None)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        logging.info(f"Sending email {message}")
        server.login(username, password)
        server.sendmail(username, emails, message)


def main():
    date = time.strftime("%m-%d-%y-%H.%M.%S", time.gmtime())

    parser = argparse.ArgumentParser(description="Check Torrey tee times.")
    parser.add_argument("username", nargs=1, help="Username duh.")
    parser.add_argument("-v", action="store_true")
    args = parser.parse_args()
    user_password = getpass.getpass(prompt="Password: ", stream=None)

    log_level = logging.DEBUG if args.v else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("TorreyBot-{}.txt".format(date)),
            logging.StreamHandler(),
        ],
    )

    query_date = "02-14-2021"
    players = 2
    
    times = get_times(args.username, user_password, query_date, players)
    if not times:
        logging.error("Failed to get tee times.")
        return 1
    
    
    
    # send_notification(times)


if __name__ == "__main__":
    main()

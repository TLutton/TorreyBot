import logging
import argparse
import time
import getpass
import requests

login_url = "https://foreupsoftware.com/index.php/api/booking/users/login"
login_form = {
    "username": "",
    "password": "",
    "booking_class_id": "",
    "api_key": "no_limits",
    "course_id": 19347,
}
login_headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}


def login(username, password):
    login_form["username"] = username
    login_form["password"] = password
    logging.debug("Attempting to login.")
    response = requests.post(login_url, login_form, headers=login_headers)
    if response.status_code == requests.codes.ok:
        logging.debug("Log in successful.")
        logging.debug(response.content)
        return True
    else:
        logging.debug("Log in failed. Error code: {}".format(response.status_code))
        logging.debug(response.content)
        return False


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

    login(args.username, user_password)


if __name__ == "__main__":
    main()

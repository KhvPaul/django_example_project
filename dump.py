#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import datetime
import requests
from bs4 import BeautifulSoup
from termcolor import colored

SITE = "http://translatedby.com/"
TAG = "GURPS"
BASE_DIR_NAME = datetime.datetime.now().strftime("%Y-%m-%d")
TRANSLATIONS = []


if __name__ == "__main__":
    print("Start")
    r = requests.get(SITE)
    # fmt: off
    if r.status_code != requests.codes.ok:  # Check site is online
        print("{site} status - {status_code}".format(**{"site": SITE, "status_code": colored(r.status_code, "red")}))
    else:
        print("{site} status - {status_code}".format(**{"site": SITE, "status_code": colored(r.status_code, "green")}))
    # fmt: on
        if os.path.isdir(BASE_DIR_NAME):
            print("Dump exists. Aborting.")
        else:
            print("Create dump directory.")
            os.mkdir(os.path.join(BASE_DIR_NAME))

            URL = "{site}you/tags/{tag}/".format(**{"site": SITE, "tag": TAG})
            r = requests.get(URL)
            soup = BeautifulSoup(r.text, "html.parser")
            pages = int(soup.find("div", {"class": "spager"}).find_all("a")[-1].string)  # Get last page number
            for i in range(1, pages + 1):
                TAG_URL = "{url}?page={i}".format(**{"url": URL, "i": i})
                r = requests.get(TAG_URL)
                # fmt: off
                if r.status_code != requests.codes.ok:  # Check the list page is available
                    print("{site} status - {status_code}".format(**{"site": TAG_URL, "status_code": colored(r.status_code, "red")}))
                    continue
                else:
                    print("{site} status - {status_code}".format(**{"site": TAG_URL, "status_code": colored(r.status_code, "green")}))
                    # fmt: on
                    soup = BeautifulSoup(r.text, "html.parser")
                    for dt in soup.find("dl", {"class": "translations-list"}).find_all("dt"):
                        TRANSLATIONS.append(
                            {
                                "name": dt.a.string.replace("\n", " "),
                                "url": re.sub("/trans/$", "/", dt.a.get("href"))[1:],
                            }
                        )
            for book in TRANSLATIONS:
                URL = "{site}{url}".format(**{"site": SITE, "url": book["url"]})
                r = requests.get(URL + "stats/")
                # fmt: off
                if r.status_code != requests.codes.ok:  # Check the list page is available
                    print("{site} status - {status_code}".format(**{"site": URL, "status_code": colored(r.status_code, "red")}))
                    continue
                else:
                    print("{site} status - {status_code}".format(**{"site": URL, "status_code": colored(r.status_code, "green")}))
                    # fmt: on
                    print("Dumping \"{name}\"".format(name=book["name"]))
                    DIR = os.path.join(BASE_DIR_NAME, book["name"])
                    os.mkdir(DIR)
                    soup = BeautifulSoup(r.text, "html.parser")
                    about = soup.find(id="about-translation").blockquote
                    about = about.string.strip() if about else ""
                    with open(os.path.join(DIR, "about.txt"), "wt", encoding="utf-8") as f:
                        f.write("URL - {url}\n".format(url=URL))
                        f.write(about)
                    with open(os.path.join(DIR, "result.txt"), "wb") as f:
                        r = requests.get(URL + ".txt")
                        f.write(r.content)
                    print("Dumped.")
    print("Finished")

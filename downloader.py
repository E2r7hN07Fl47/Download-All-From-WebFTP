import requests
import sys
from bs4 import BeautifulSoup
import urllib.parse
import os


HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:101.00) Gecko/20100101 Firefox/101.00'
      }


def downloader(url, session):
    path_arr = urllib.parse.unquote(url).split("/")[2:]
    file_name = path_arr.pop(-1)
    path = "/".join(path_arr) + '/'
    os.makedirs(path, exist_ok=True)
    full_path = path + file_name

    print(f"Downloading {file_name} on path {path}")

    r = session.get(url, stream=True)
    with open(full_path, "wb") as file:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)

    print(f"{file_name} successfully downloaded\n")


def parser(url, session=None):
    dirs = []
    if session is None:
        session = requests.Session()
        session.headers = HEADERS
    r = session.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find("table").findAll("tr")
    for row in rows:
        row_data = row.findAll("td")
        if len(row_data) == 0:
            continue
        type = (row_data[0].find("img").get("alt"))
        if type == "[PARENTDIR]":
            continue

        href = url + row_data[1].find("a").get("href")
        if type == "[DIR]":
            dirs.append(href)
        else:
            downloader(href, session)

    for one_dir in dirs:
        parser(one_dir, session)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Not enough arguments. Provide url.")
        raise SystemExit

    site_url = sys.argv[1]
    if not site_url.endswith("/"):
        site_url += "/"
    parser(site_url)
    print("Site has been successfully downloaded")

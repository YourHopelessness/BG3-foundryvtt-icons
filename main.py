import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse, unquote

def safe_filename(url):
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path) 
    filename = unquote(filename)

    if filename.startswith("380px-"):
        filename = filename[6:]

    if filename.endswith(".webp.png"):
        filename = filename.replace(".webp.png", ".webp")
    elif filename.endswith(".png") and ".webp" in filename:
        filename = filename.split(".webp")[0] + ".webp"

    return filename

BASE_URL = "https://bg3.wiki"
CATEGORIES_URLS = {
    "bg3_weapons_icons": f"{BASE_URL}/wiki/Category:Weapon_action_tooltip_images",
    "bg3_action_icons": f"{BASE_URL}/wiki/Category:Action_tooltip_images",
    "bg3_generic_icons": f"{BASE_URL}/wiki/Category:Generic_tooltip_images",
    "bg3_passive_icons": f"{BASE_URL}/wiki/Category:Passive_feature_tooltip_images",
    "bg3_skill_icons": f"{BASE_URL}/wiki/Category:Skill_tooltip_images",
    "bg3_spell_icons": f"{BASE_URL}/wiki/Category:Spell_tooltip_images",
}

def get_all_image_links(category_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    image_links = []
    next_url = category_url

    while next_url:
        print(f"Обработка страницы: {next_url}")
        response = requests.get(next_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        for li in soup.select("div.mw-content-ltr ul li"):
            link = li.find("a")
            if link and link.get("href"):
                file_page_url = urljoin(BASE_URL, link["href"])
                file_response = requests.get(file_page_url, headers=headers)
                file_soup = BeautifulSoup(file_response.text, "html.parser")
                
                img = file_soup.find("img", src=lambda s: s and "/w/images/" in s)
                if img:
                    image_url = urljoin(BASE_URL, img["src"])
                    image_links.append(image_url)

        # Поиск ссылки на следующую страницу
        next_link = soup.find("a", string="next page")
        if next_link:
            next_url = urljoin(BASE_URL, next_link["href"])
        else:
            next_url = None  # Конец

    return image_links

def download_images(path, image_urls):
    for url in image_urls:
        filename = safe_filename(url)
        filepath = os.path.join(path, filename)
        if not os.path.exists(filepath):
            img_data = requests.get(url).content
            with open(filepath, "wb") as f:
                f.write(img_data)

if __name__ == "__main__":
    all_image_links = 0
    for path, url in CATEGORIES_URLS.items():
        os.makedirs(path, exist_ok=True)
        
        image_links = get_all_image_links(url)
        print("Найдено изображений:", len(image_links))
        all_image_links += len(image_links)
        download_images(path, image_links)
    print(f"Загрузка завершена. Загружено {all_image_links}")

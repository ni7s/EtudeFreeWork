import requests
from bs4 import BeautifulSoup
import json
import time
import csv
import logging
from datetime import datetime
# Configuration du logging
logging.basicConfig(filename='scraping.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_soup(url):
    """Récupère le contenu d'une URL et retourne un objet BeautifulSoup."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lève une exception pour les réponses non réussies
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        logging.error(f"Erreur lors de la récupération de l'URL {url}: {e}")
        return None

def parse_annonce(annonce):
    """Extrait les informations d'une annonce et retourne un dictionnaire."""
    try:
        titre = annonce.find('h3').text.strip().replace("Mission freelance", "").strip()
        entreprise = annonce.find('div', class_='text-base font-medium truncate w-full').text.strip()
        date = annonce.find('time').text.strip()
        description = annonce.find('div', class_='line-clamp-3 mb-4').text.strip()
    except AttributeError as e:
        logging.warning(f"Problème lors de l'analyse d'une annonce: {e}")
        return None

    return {
        'Titre': titre,
        'Entreprise': entreprise,
        'Date': date,
        'Description': description
    }

def scrape_page(url):
    """Récupère les annonces d'une page donnée."""
    soup = get_soup(url)
    print("Scraping : "+url)
    if soup is not None:
        annonce_divs = soup.find_all('div', class_='mb-4 relative rounded-lg max-full bg-white flex flex-col cursor-pointer shadow hover:shadow-md')
        return [parse_annonce(annonce) for annonce in annonce_divs if parse_annonce(annonce) is not None]
    else:
        return []

def save_to_json(filename, data):
    """Enregistre les données au format JSON."""
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def save_to_csv(filename, data):
    """Enregistre les données au format CSV."""
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def main():
    base_url = 'https://www.free-work.com/fr/tech-it/jobs?query=cloud&contracts=contractor&page='
    pages_to_scrape = 20
    page_to_start_by = 20
    base_url = base_url+str(page_to_start_by)
    delay = 0.2
    d = datetime.now()
    all_annonces = []
    f = d.strftime('%Y-%m-%d-%Hh%Mm%Ss')
    for page in range(1, pages_to_scrape + 1):
        logging.info(f"Traitement de la page {page}")
        url = f"{base_url}&page={page}"
        all_annonces.extend(scrape_page(url))
        time.sleep(delay)

    save_to_json('jobs/annonces-'+f+'-'+str(pages_to_scrape)+'pages'+'.json', all_annonces)
    save_to_csv('jobs/annonces.csv', all_annonces)

    logging.info("Scraping terminé")

if __name__ == '__main__':
    main()
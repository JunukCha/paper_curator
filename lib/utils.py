import os, os.path as osp

import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.request import urlretrieve
import zipfile
import streamlit as st

def extract_link(container, link_text, attribute='href'):
    link_element = container.find('a', string=lambda text: text and link_text in text.lower())
    if link_element:
        return link_element[attribute] if attribute != 'text' else link_element.get_text(strip=True)
    return 'Not available'

def scrape_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    papers = []
    for entry in soup.find_all('dt', class_='ptitle'):
        title = entry.text.strip()
        authors_dirty = entry.find_next_sibling('dd').text.strip()
        authors = ' '.join(author.strip() for author in authors_dirty.split('\n') if author.strip())
        links_container = entry.find_next_sibling('dd').find_next_sibling('dd')
        pdf_link = extract_link(links_container, 'pdf')
        supp_link = extract_link(links_container, 'supp')
        bibtex_info = links_container.find('div', class_='bibref').text if links_container.find('div', class_='bibref') else 'No BibTeX available'
        papers.append({
            'title': title,
            'authors': authors,
            'pdf_link': "https://openaccess.thecvf.com" + pdf_link,
            'supp_link': "https://openaccess.thecvf.com" + supp_link,
            'bibtex': bibtex_info
        })
    return papers

def show_data(papers):
    for paper_idx, paper in enumerate(papers):
        st.markdown(f'### {paper_idx+1}. {paper["title"]}')
        st.markdown(paper["authors"])
        st.markdown(f"[PDF Link]({paper['pdf_link']})")
        st.markdown(f"[Supplemental Link]({paper['supp_link']})")
        st.markdown("##### BibTeX")
        st.markdown(f"```\n{paper['bibtex']}\n```")
import os, os.path as osp
import pandas as pd
import io
import streamlit as st
from lib.utils import scrape_data, show_data

# Initialize session state to track layout
if 'layout' not in st.session_state:
    st.session_state.layout = 'Layout 1'

if 'running' not in st.session_state:
    st.session_state.running = False

st.set_page_config(page_title="Curate Paper", page_icon="😊")

# Layout 1
if st.session_state.layout == 'Layout 1':
    if 'run_scrape_button' in st.session_state \
        and st.session_state.run_scrape_button == True:
        st.session_state.running = True
    else:
        st.session_state.running = False
    
    if 'query' not in st.session_state:
        st.session_state.query = ''

    st.title("Conference Paper Scraper")

    conference = st.selectbox("Conference", ["CVPR", "ICCV", "WACV"], disabled=st.session_state.running)
    if conference == "WACV":
        years = list(range(2024, 2019, -1))
    elif conference == "ICCV":
        years = list(range(2023, 2012, -2))  # ICCV is held every two years
    else:  # CVPR and other conferences
        years = list(range(2024, 2012, -1))
    year = st.selectbox("Year", years, disabled=st.session_state.running)
    query = st.text_input("Search Query", disabled=st.session_state.running)

    scrape_button = st.sidebar.button("Scrape Data", disabled=st.session_state.running, key='run_scrape_button')
    
    if scrape_button:
        if query.strip():  # Check if query is not empty
            prev_papers = None
            base_url = f"https://openaccess.thecvf.com/{conference}{year}"
            words = [word for word in query.replace('_', ' ').replace('-', ' ').split()]
            for word in words:
                full_url = f"{base_url}?query={word}"
                papers = scrape_data(full_url)
                if prev_papers is None:
                    prev_papers = papers
                else:
                    prev_papers_set = {tuple(paper.items()) for paper in prev_papers}
                    current_papers_set = {tuple(paper.items()) for paper in papers}
                    common_papers_set = prev_papers_set & current_papers_set
                    prev_papers = [dict(paper) for paper in common_papers_set]
            filtered_papers = prev_papers if prev_papers is not None else []
            st.session_state['papers'] = filtered_papers
            st.rerun()  # Refresh the app to apply the enabled state
        else:
            st.session_state['none_query'] = True
            st.rerun()

    if 'none_query' in st.session_state:
        st.write("Query cannot be empty!")
        del st.session_state["none_query"]
    
    if 'papers' in st.session_state:
        base_path = osp.join('material', conference, str(year), query)
        
        papers = st.session_state['papers']
        st.write(f"Data scraped successfully! Number of papers: {len(papers)}")

        show_data(papers)

        df = pd.DataFrame(papers)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)

        st.sidebar.download_button(
            label="Download as Excel", 
            data=output.getvalue(), 
            file_name="papers.xlsx", 
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
            disabled=st.session_state.running, 
        )
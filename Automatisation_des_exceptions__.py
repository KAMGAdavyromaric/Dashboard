# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import streamlit as st
import os
from io import BytesIO

# Configuration de la page
st.set_page_config(page_title="Exception", page_icon="📊", layout="wide")

# CSS pour améliorer l'esthétique
style = """
<style>
body {
    font-family: 'Helestica', sans-serif;
    font-size: 12px;
    background-color: #f4f4f9;
}
h1, h2, h3, h4, h5, h6 {
    color: #FF6347;
}
.main-header {
    text-align: center;
    font-size: 36px;
    color: #FF6347;
    margin-top: 20px;
}
.metric-box {
    background-color: #e6f7ff;
    padding: 10px;
    border-radius: 10px;
    margin: 10px 0;
}
.sample-table {
    border: 1px solid #d3d3d3;
    border-radius: 10px;
    margin-top: 10px;
}
.download-button {
    display: flex;
    justify-content: center;
    margin-top: 20px;
}
.centered {
    text-align: center;
}
.big-font {
    font-size: 30px !important;
    font-weight: bold;
}
</style>
"""

st.markdown(style, unsafe_allow_html=True)

# Titre principal


# Chemin du répertoire contenant les fichiers de données sur GitHub
chemin_github = "https://raw.githubusercontent.com/votre_utilisateur/votre_depot/main/data"

# Chargement des données
MTN_url = os.path.join(chemin_github, "CDR_MTN_not_in_CDR_OCM___MTN_vers_ORANGE_02032023.csv")
OCM_url = os.path.join(chemin_github, "CDR_OCM_not_in_CDR_MTN___MTN_vers_ORANGE_02032023.csv")

@st.cache_data
def load_data():
    
    MTN = pd.read_csv(MTN_url, sep=";", encoding='latin1')
    
    OCM = pd.read_csv(OCM_url, sep=";", encoding='latin1')
    
    return MTN, OCM


MTN, OCM = load_data()

# Chemin des fichiers
chemin = r"C:\Users\DELL\Desktop\OrangeCameroun\TransferNow"
os.chdir(chemin)

# Chargement des données
#MTN = pd.read_csv("CDR_MTN_not_in_CDR_OCM___MTN_vers_ORANGE_02032023.csv", sep=";", encoding='latin1')
#OCM = pd.read_csv("CDR_OCM_not_in_CDR_MTN___MTN_vers_ORANGE_02032023.csv", sep=";", encoding='latin1')


#MTN = pd.read_csv(MTN_url, sep=";", encoding='latin1')
#OCM = pd.read_csv(OCM_url, sep=";", encoding='latin1')

# Sidebar pour la navigation
st.sidebar.title(':mag_right: Sommaire')
pages = ["Visualisation des données 📈", "Téléchargement de la base des exceptions 💾"]
page = st.sidebar.radio("Aller vers la page :", pages)

# Fonctions de traitement des données
@st.cache_data
def top(data, colonne, colonne1):
    pivot_table = data.pivot_table(index=colonne, aggfunc='size').reset_index(name="Nombre d'appels")
    somme_colonne1 = data.groupby(colonne)[colonne1].sum().reset_index(name='Volume de trafics')
    resultat = pd.merge(pivot_table, somme_colonne1, on=colonne)
    resultat.set_index(colonne, inplace=True)
    resultat_trie = resultat.sort_values(by="Nombre d'appels", ascending=False).head(15)
    return resultat_trie

@st.cache_data
def exception(MTN, OCM):
    OCM = OCM.drop_duplicates().reset_index(drop=True)
    MTN = MTN.drop_duplicates().reset_index(drop=True)
    unique_ocm = OCM[~OCM['a_number'].isin(MTN['A_NUMBER'])]
    unique_mtn = MTN[~MTN['A_NUMBER'].isin(OCM['a_number'])]
    return unique_ocm, unique_mtn

unique_ocm, unique_mtn = exception(MTN, OCM)

@st.cache_resource
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    writer.save()
    processed_data = output.getvalue()
    return processed_data

if page == pages[0]:
    st.markdown("<h3 class='centered' style='color: orange;'>📊 Statistiques OCM et MTN</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns((2, 2))
    
    with col1:
        st.markdown("<h4 class='centered'>Statistiques côté OCM 📞 </h4>", unsafe_allow_html=True)
        st.write("**Échantillon de la base OCM**")
        st.dataframe(OCM.sample(5), use_container_width=True)
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric(label="Nombre d'appels de la journée", value=f"{OCM.shape[0]:,}")
        st.metric(label="Volume de trafic (en secondes)", value=f"{OCM['duration'].sum():,}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("**Numéros ayant le plus appelés provenant de la base OCM**")
        OCM_top = top(OCM, 'a_number', 'duration')
        st.dataframe(OCM_top)
    
    with col2:
        st.markdown("<h4 class='centered'>Statistiques côté MTN 📞</h4>", unsafe_allow_html=True)
        st.write("**Échantillon de la base MTN**")
        st.dataframe(MTN.sample(5), use_container_width=True)
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric(label="Nombre d'appels de la journée", value=f"{MTN.shape[0]:,}")
        st.metric(label="Volume de trafic (en secondes)", value=f"{MTN['CALL_DURATION'].sum():,}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("**Numéros ayant le plus appelés provenant de la base MTN**")
        MTN_top = top(MTN, 'A_NUMBER', 'CALL_DURATION')
        st.dataframe(MTN_top)

if page == pages[1]:
    
    st.markdown("<h1 class='main-header'> Traitement des exceptions</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns((2, 2))
    
    with col1:
        st.markdown("<h4 class='centered'>Statistiques des exceptions côté OCM 📉</h4>", unsafe_allow_html=True)
        st.write("**Échantillon de la base des exceptions OCM**")
        st.dataframe(unique_ocm.sample(5), use_container_width=True)
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric(label="Volume de trafic des exceptions (en secondes)", value=f"{unique_ocm['duration'].sum():,}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("**Numéros ayant le plus appelés provenant des exceptions OCM**")
        OCM_top = top(unique_ocm, 'a_number', 'duration')
        st.dataframe(OCM_top, use_container_width=True)
        st.download_button(
            label="📂 Télécharger le fichier des exceptions OCM en Excel 📥",
            data=to_excel(unique_ocm),
            file_name="exceptions_OCM.xlsx",
            mime="application/vnd.ms-excel",
            key='download-ocm'
        )

    with col2:
        st.markdown("<h4 class='centered'>Statistiques des exceptions côté MTN 📉</h4>", unsafe_allow_html=True)
        st.write("**Échantillon de la base des exceptions MTN**")
        st.dataframe(unique_mtn.sample(5), use_container_width=True)
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric(label="Volume de trafic des exceptions (en secondes)", value=f"{unique_mtn['CALL_DURATION'].sum():,}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("**Numéros ayant le plus appelés provenant des exceptions MTN**")
        MTN_top = top(unique_mtn, 'A_NUMBER', 'CALL_DURATION')
        st.dataframe(MTN_top, use_container_width=True)
        st.download_button(
            label=" 📂 Télécharger le fichier des exceptions MTN en Excel 📥",
            data=to_excel(unique_mtn),
            file_name="exceptions_MTN.xlsx",
            mime="application/vnd.ms-excel",
            key='download-mtn'
        )

    ecart_mtn_ocm = unique_mtn['CALL_DURATION'].sum() - unique_ocm['duration'].sum()
    if ecart_mtn_ocm > 0:
        st.markdown(f"<div class='big-font centered'> L'écart des exceptions entre MTN et OCM est de {ecart_mtn_ocm:,} secondes.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='big-font centered'> L'écart des exceptions entre OCM et MTN est de {abs(ecart_mtn_ocm):,} secondes.</div>", unsafe_allow_html=True)


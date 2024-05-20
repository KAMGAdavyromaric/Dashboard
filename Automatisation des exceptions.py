# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import numpy as np
import streamlit as st
import os
from io import BytesIO

# Configuration de la page
st.set_page_config(page_title="Exception", page_icon=":bar_chart:", layout="wide")

# Titre principal
st.title(":bar_chart: Traitement des exceptions")

# Chemin des fichiers
chemin = r"C:\Users\kyxb5593\Desktop\ORANGE CAMEROUN\MTN_vers_ORANGE\10_02_2023"
os.chdir(chemin)

# Lecture des fichiers CSV
MTN = pd.read_csv("CDR_MTN_not_in_CDR_OCM___MTN_vers_ORANGE_10022023.csv", sep=";", encoding='latin1')
OCM = pd.read_csv("CDR_OCM_not_in_CDR_MTN___MTN_vers_ORANGE_10022023.csv", sep=";", encoding='latin1')




st.sidebar.title(':mag_right: Sommaire') 
pages = ["Visualisation des données", "Téléchargement de la base des exceptions"]
page = st.sidebar.radio("Aller vers la page : ", pages)

# Fonctions de traitement des données
@st.cache_data
def top(data, colonne):
    pivot_table = data.pivot_table(index=colonne, aggfunc='size')
    top = pivot_table.sort_values(ascending=False).head(15)
    top_df = top.to_frame(name="nombre d'appels")
    top_df.reset_index(inplace=True)
    top_df.rename(columns={'index': colonne}, inplace=True)
    return top_df

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

style = """
<style>
.big-font {
    font-size:30px !important;
    font-weight: bold;
}
.centered {
    text-align: center;
}
.metric-box {
    background-color: #f0f2f6;
    padding: 10px;
    border-radius: 10px;
    margin: 10px 0;
}
</style>
"""

st.markdown(style, unsafe_allow_html=True)


if page == pages[0]:
    
    st.markdown("<h3 style='text-align: center; color: orange;'>  Statistiques OCM et MTN</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns((2, 2))
    
    with col1:
        
        st.markdown("""
    <div style="text-align: center; font-size: 24px;">
        <strong>Statistiques côté OCM </strong>
    </div>
    """, unsafe_allow_html=True)

        st.write("**Échantillon de la base OCM**")
        st.dataframe(OCM.sample(5))
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric(label="Nombre d'appels de la journée", value=f"{OCM.shape[0]:,}")
        st.metric(label="Volume de trafic (en secondes)", value=f"{OCM['duration'].sum():,}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("**Numéros ayant le plus appelés provenant de la base OCM**")
        OCM_top = top(OCM, 'a_number')
        st.dataframe(OCM_top)
    
    with col2:
        st.markdown("""
    <div style="text-align: center; font-size: 24px;">
        <strong>Statistiques côté MTN</strong>
    </div>
    """, unsafe_allow_html=True)

    
        st.write("**Échantillon de la base MTN**")
        st.dataframe(MTN.sample(5))
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric(label="Nombre d'appels de la journée", value=f"{MTN.shape[0]:,}")
        st.metric(label="Volume de trafic (en secondes)", value=f"{MTN['CALL_DURATION'].sum():,}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("**Numéros ayant le plus appelés provenant de la base MTN**")
        MTN_top = top(MTN, 'A_NUMBER')
        st.dataframe(MTN_top)

if page == pages[1]:
    col1, col2 = st.columns((2, 2))
    
    with col1:
        
        
        st.markdown("""
    <div style="text-align: center; font-size: 24px;">
        <strong> Statistiques des exceptions côté OCM </strong>
    </div>
    """, unsafe_allow_html=True)

        st.write("**Échantillon de la base des exceptions OCM**")
        st.dataframe(unique_ocm.sample(5))
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric(label="Volume de trafic des exceptions (en secondes)", value=f"{unique_ocm['duration'].sum():,}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("**Numéros ayant le plus appelés provenant des exceptions OCM**")
        OCM_top = top(unique_ocm, 'a_number')
        st.dataframe(OCM_top)
        st.download_button(
            label="Télécharger le fichier des exceptions OCM en Excel",
            data=to_excel(unique_ocm),
            file_name="exceptions_OCM.xlsx",
            mime="application/vnd.ms-excel"
        )

    with col2:
        st.markdown("""
    <div style="text-align: center; font-size: 24px;">
        <strong> Statistiques des exceptions côté MTN </strong>
    </div>
    """, unsafe_allow_html=True)
        st.write("**Échantillon de la base des exceptions MTN**")
        st.dataframe(unique_mtn.sample(5))
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric(label="Volume de trafic des exceptions (en secondes)", value=f"{unique_mtn['CALL_DURATION'].sum():,}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("**Numéros ayant le plus appelés provenant des exceptions MTN**")
        MTN_top = top(unique_mtn, 'A_NUMBER')
        st.dataframe(MTN_top)
        st.download_button(
            label="Télécharger le fichier des exceptions MTN en Excel",
            data=to_excel(unique_mtn),
            file_name="exceptions_MTN.xlsx",
            mime="application/vnd.ms-excel"
        )

    ecart_mtn_ocm = unique_mtn['CALL_DURATION'].sum() - unique_ocm['duration'].sum()
    if ecart_mtn_ocm > 0:
        st.markdown(f"<div class='big-font centered'>L'écart des exceptions entre MTN et OCM est de {ecart_mtn_ocm:,} secondes.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='big-font centered'>L'écart des exceptions entre OCM et MTN est de {abs(ecart_mtn_ocm):,} secondes.</div>", unsafe_allow_html=True)





















# -*- coding: utf-8 -*-
# Importation des bibliothèques nécessaires
import pandas as pd
import streamlit as st
from io import BytesIO

# Configuration de la page Streamlit
st.set_page_config(page_title="Traitement des exceptions", page_icon=":bar_chart:", layout="wide")

# Titre principal de la page
st.title(":bar_chart: Traitement des exceptions")

# Création de deux colonnes pour les téléversements de fichiers
col1, col2 = st.columns((2, 2))

# Variables pour stocker les données des fichiers
OCM = None
MTN = None

# Colonne pour le fichier d'OCM
with col1:
    f1 = st.file_uploader("Ouvrir le fichier d'OCM", type=["csv", "txt", "xlsx", "xls"])
    if f1 is not None:
        try:
            # Détermination de l'encodage du fichier
            encoding = 'latin-1' if f1.type == 'txt' else 'utf-8'
            # Lecture du fichier en fonction de son type
            OCM = pd.read_csv(f1, encoding=encoding) if f1.type in ["csv", "txt"] else pd.read_excel(f1)
            # Affichage d'un échantillon du dataframe
            st.dataframe(OCM.sample(5))
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier OCM: {e}")

# Colonne pour le fichier de MTN
with col2:
    f2 = st.file_uploader("Ouvrir le fichier de MTN", type=["csv", "txt", "xlsx", "xls"])
    if f2 is not None:
        try:
            # Détermination de l'encodage du fichier
            encoding = 'latin-1' if f2.type == 'txt' else 'utf-8'
            # Lecture du fichier en fonction de son type
            MTN = pd.read_csv(f2, encoding=encoding) if f2.type in ["csv", "txt"] else pd.read_excel(f2)
            # Affichage d'un échantillon du dataframe
            st.dataframe(MTN.sample(5))
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier MTN: {e}")

# Affichage du sommaire dans la sidebar
st.sidebar.title(':mag_right: Sommaire')
pages = ["Visualisation des données", "Téléchargement de la base des exceptions"]
page = st.sidebar.radio("Aller vers la page :", pages)

# Fonction pour obtenir les 15 principaux appels par numéro
@st.cache_data
def top(data, colonne):
    pivot_table = data.pivot_table(index=colonne, aggfunc='size')
    top = pivot_table.sort_values(ascending=False).head(15)
    top_df = top.to_frame(name="nombre d'appels")
    top_df.reset_index(inplace=True)
    top_df.rename(columns={'index': colonne}, inplace=True)
    return top_df

# Fonction pour trouver les exceptions entre les fichiers OCM et MTN
@st.cache_data 
def exception(MTN, OCM):
    OCM = OCM.drop_duplicates().reset_index(drop=True)
    MTN = MTN.drop_duplicates().reset_index(drop=True)
    unique_ocm = OCM[~OCM['a_number'].isin(MTN['A_NUMBER'])]
    unique_mtn = MTN[~MTN['A_NUMBER'].isin(OCM['a_number'])]
    return unique_ocm, unique_mtn

# Vérification si les fichiers sont chargés avant de procéder
if OCM is not None and MTN is not None:
    unique_ocm, unique_mtn = exception(MTN, OCM)

# Fonction pour convertir un DataFrame en fichier Excel
@st.cache_resource  
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    writer.save()
    processed_data = output.getvalue()
    return processed_data

# Affichage des données en fonction de la page sélectionnée
if OCM is not None and MTN is not None:
    if page == "Visualisation des données":
        st.markdown("""
            <div style="text-align: center; font-size: 24px;">
                <strong>### Statistiques des données OCM et MTN</strong>
            </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns((2, 2))
        
        with col1:
            st.markdown("""
                <div style="text-align: center; font-size: 24px;">
                    <strong>Statistiques côté OCM</strong>
                </div>
            """, unsafe_allow_html=True)
            st.write("**Échantillon de la base OCM**")
            st.dataframe(OCM.sample(5))
            st.metric(label="Nombre d'appels de la journée", value=f"{OCM.shape[0]:,}")
            st.metric(label="Volume de trafic (en secondes)", value=f"{OCM['duration'].sum():,}")
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
            st.metric(label="Nombre d'appels de la journée", value=f"{MTN.shape[0]:,}")
            st.metric(label="Volume de trafic (en secondes)", value=f"{MTN['CALL_DURATION'].sum():,}")
            st.write("**Numéros ayant le plus appelés provenant de la base MTN**")
            MTN_top = top(MTN, 'A_NUMBER')
            st.dataframe(MTN_top)

    if page == "Téléchargement de la base des exceptions":
        col1, col2 = st.columns((2, 2))
        
        with col1:
            st.markdown("""
                <div style="text-align: center; font-size: 24px;">
                    <strong>Statistiques des exceptions côté OCM</strong>
                </div>
            """, unsafe_allow_html=True)
            st.write("**Échantillon de la base des exceptions OCM**")
            st.dataframe(unique_ocm.sample(5))
            st.metric(label="Volume de trafic des exceptions (en secondes)", value=f"{unique_ocm['duration'].sum():,}")
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
                    <strong>Statistiques des exceptions côté MTN</strong>
                </div>
            """, unsafe_allow_html=True)
            st.write("**Échantillon de la base des exceptions MTN**")
            st.dataframe(unique_mtn.sample(5))
            st.metric(label="Volume de trafic des exceptions (en secondes)", value=f"{unique_mtn['CALL_DURATION'].sum():,}")
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

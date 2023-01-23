import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import requests
import datetime
import pandas as pd

def checkDouble(data : pd.DataFrame , nom_new_player):
    for i in data["Nom"]:
        if i == nom_new_player:
            return False
    return True


credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
project_id = 'bddrecrutement'

client = bigquery.Client(credentials= credentials,project=project_id)

data = client.query("""
   SELECT  *
   FROM `bddrecrutement.Joueur.Joueur`
    """).result().to_dataframe()

'''
Joueurs en attente d'être évalué.
'''
st.table(data)



"""
Ajouter un joueur a la liste de recrutement
"""
with st.form("Add a Player"):
    nom = st.text_input("Nom")
    motivation = st.text_input("motivation du joueur")

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        if nom and checkDouble(data , nom):
            nom=nom.lower()
            #requete a l'API de WoW pour collecter de la data sur le joueur
            xp = requests.get(f'''https://eu.api.blizzard.com/profile/wow/character/hyjal/{nom}/mythic-keystone-profile?namespace=profile-eu&locale=fr_FR&access_token={st.secrets["API"]}''').json()["current_mythic_rating"]["rating"]
            classe = requests.get(f'''https://eu.api.blizzard.com/profile/wow/character/hyjal/{nom}?namespace=profile-eu&locale=fr_FR&access_token={st.secrets["API"]}''').json()
            xp_raid = requests.get(f'https://eu.api.blizzard.com/profile/wow/character/hyjal/{nom}/encounters/raids?namespace=profile-eu&locale=fr_FR&access_token={st.secrets["API"]}').json()
            xp_raid = xp_raid["expansions"][-1]["instances"][-1]["modes"]
            classe = [classe["character_class"]["name"],classe["active_spec"]["name"]]
            str_xp_raid = ""
            #Recuperation de l'XP raid
            for mode in xp_raid:
                str_xp_raid += f'{mode["difficulty"]["type"]} : {mode["progress"]["completed_count"]}/{mode["progress"]["total_count"]}  '
            date=str(datetime.date.today())
            query = f'''INSERT INTO `bddrecrutement.Joueur.Joueur`
                    VALUES ('{nom}', '{classe[0]} : {classe[1]}','Cote mythique : {xp} , XP Raid : {str_xp_raid}','{motivation}','{date}',"None")'''
            client.query(query)
        else:
            st.write("❗Veuillez renseigner le nom du joueur ou le joueur rentré est un doublon❗")
"""
Modifier la section Commentaire ou supprimer un joueur
"""
with st.form("Changement sur le joueur"):
    nom = st.selectbox(
    "Selectionner le joueur",
    (data["Nom"]))
    motivation = st.text_input("avis sur le joueur")
    boutton_supprimer = st.checkbox("désirez vous supprimer le joueur du processus de recrutement / le supprimer de la base de donné après le recrutement")
        # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        if nom:
            if boutton_supprimer:
                client.query(f"""DELETE FROM `bddrecrutement.Joueur.Joueur` WHERE Nom='{nom}'""")
            elif motivation:
                client.query(f"""UPDATE bddrecrutement.Joueur.Joueur
                                SET Commentaire = '{motivation}'
                                WHERE Nom = '{nom}'""")
            else:
                st.write("❗Veuillez mettre a jour les motivations❗")
        else:
            st.write("Veuillez renseigner un nom")

import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
project_id = 'bddrecrutement'

client = bigquery.Client(credentials= credentials,project=project_id)


'''
Joueurs en attente d'être évalué.
'''
st.table(client.query("""
   SELECT  *
   FROM `bddrecrutement.Joueur.Joueur`
   LIMIT 5""").result().to_dataframe())



"""
Ajouter un joueur a la liste de recrutement
"""
with st.form("Add a Player"):
    nom = st.text_input("Nom")
    classe = st.text_input("Classe")
    xp = st.text_input("xp raid et / ou mm+")
    motivation = st.text_input("motivation du joueur")

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        print(nom)
        if nom:
            client.query(f"""INSERT INTO `bddrecrutement.Joueur.Joueur`
                      VALUES ('{nom}','{classe}','{xp}','{motivation}')""")
            pass
        else:
            st.write("Veuillez renseigner un nom")

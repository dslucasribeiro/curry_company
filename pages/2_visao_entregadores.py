#Libreries
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.offline as pyo
from haversine import haversine
import folium
from streamlit_folium import folium_static
import streamlit as st
from PIL import Image

st.set_page_config( page_title = 'Visão Entregadores', page_icon='🛵', layout = 'wide')


# Importacao e Cópia
df = pd.read_csv('Dados/train.csv')

# Limpeza
def clean_code(df1):
    """ Funcao responsavel pela limpeza do dataframe
    
    Tipos de limpeza:
    1. Remocao dos dados contendo NaN.
    2. Conversao de tipos.
    3. Remocao de espacos das colunas.
    4. Formatacao da coluna de tempo.  
    
    """
    
    # Eliminando Valores ausentes (NaN) da coluna Delivery_person_Age.
    linhas_trash = df1.loc[:, 'Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_trash, :]

    # Eliminando Valores ausentes (NaN) da coluna Road_traffic_density.
    linhas_trash2 = df1.loc[:, 'Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_trash2, :]

    # Eliminando Valores ausentes (NaN) da coluna City.
    df1 = df1.loc[df1.loc[:, 'City'] != 'NaN ', :]

    # Convertendo a coluna multiple_deliveries de texto para Numero.
    lines_trash = df1.loc[:, 'multiple_deliveries'] != 'NaN '
    df1 = df1.loc[lines_trash, :].copy()

    # Eliminando Valores ausentes (NaN) da coluna City.
    df1 = df1.loc[df1.loc[:, 'Weatherconditions'] != 'conditions NaN ', :]

    # Convertendo a coluna Age de texto para Numero.
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    # Convertendo a coluna Delivery_person_Ratings.
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # Convertendo a coluna Order_Date para data.
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # Object to Int
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # Remover espacos em branco dos valores
    df1 = df1.reset_index( drop=True )

    for i in range( len(df1) ):
       df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()

    # Remover espacos em branco dos valores de uma coluna sem loop for
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()
    df1.loc[:,'Delivery_person_ID'] = df1.loc[:,'Delivery_person_ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()

    # Limpando a coluna de Time_Taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    return df1

df1 = clean_code(df)
#================== Functions =======================#

# Funcao criada para verificar avaliacoes medias por transito ou condicoes climaticas.
def avg_condition(df1, col):
    cols = ['Delivery_person_Ratings', col]
    df_avg = (df1.loc[:, cols].groupby(col)['Delivery_person_Ratings']
        .agg(['mean', 'std']).reset_index())
    st.dataframe(df_avg)

# Funcao criada para mostrar os 10 entregadores mais rapidos ou mais lentos.
def top_deliveries(df1, top_asc):
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby( ['City', 'Delivery_person_ID'] )
                      .mean().sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index())

    df_aux01 = df2.loc[df2['City'] == 'Metropolitan', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index(drop=True)
    st.dataframe(df3)


# ====================================
# Barra Lateral do streamlit
# ====================================
st.header('Marketplace - Visão Entregadores')
image_path = 'dashboard.png'
image = Image.open( image_path )
st.sidebar.image(image, width=120)

st.sidebar.markdown ('# Cury Company')
st.sidebar.markdown ('## Fastest Delivery in Town')
st.sidebar.markdown ("""---""")

st.sidebar.markdown( '## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Áté qual valor?',
    value=pd.datetime( 2022, 4, 13 ),
    min_value=pd.datetime( 2022, 2, 11 ),
    max_value=pd.datetime( 2022, 4, 6 ),
    format='DD-MM-YYYY')

st.sidebar.markdown ("""---""")

traffic_options = st.sidebar.multiselect (
    'Quais as condicoes do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown ("""---""")

#Filtro de data
lines = df1.loc[:, 'Order_Date'] < date_slider
df1 = df1.loc[lines, :]

#Filtro de transito
lines_traffic_options = df1.loc[:, 'Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[lines_traffic_options, :]

# ====================================
# Layout no Streamlit
# ====================================

tab1, tab2, tab3 = st.tabs ( ['Visão Gerencial', ' ', ' '] )

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric("Maior idade", maior_idade)
            
        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
            
        with col3:
            melhor = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condicao', melhor)
            
        with col4:
            pior = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric("Pior condicao", pior)
            
        st.markdown ("""---""")
        
    with st.container():
        st.title('Avaliacoes')
        col1, col2 = st.columns (2)
        with col1:
            st.markdown('##### Avaliacoes media por Entregador')
            cols = ['Delivery_person_Ratings', 'Delivery_person_ID']
            df_avg_ratings = df1.loc[:, cols].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(df_avg_ratings)
            
        with col2:
            st.markdown('##### Avaliacoes media por transito')
            avg_condition(df1, 'Road_traffic_density')
            
            st.markdown('##### Avaliacoes media por condicoes climaticas')
            avg_condition(df1, 'Weatherconditions')
            
        st.markdown ("""---""")        
            
    with st.container():
        st.title('Velocidade de Entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top entregadores mais rapidos')
            top_deliveries(df1, top_asc=True)
            
            
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            top_deliveries(df1, top_asc=False)
            
            
    
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
import streamlit as st

st.set_page_config( page_title = 'Visão Empresa', page_icon='📊', layout = 'wide')

# Importacao e Cópia
df = pd.read_csv('Dados/train.csv')
#df1 = df.copy()


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
def order_by_day(df1):
    cols = ['ID', 'Order_Date']
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()

    # Grafico de barras com plotly
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    st.plotly_chart(fig, use_container_width=True)

    
def traffic_order_share(df1):
    cols = ['ID', 'Road_traffic_density']
    df_aux = df1.loc[:,cols].groupby('Road_traffic_density').count().reset_index()

    # Cria porcentagens
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

    # Criar grafico de pizza com plotly
    fig = px.pie( df_aux, values='entregas_perc', names='Road_traffic_density' )
    st.plotly_chart(fig, use_container_width=True)
    
def traffic_order_city(df1):
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()

    # Grafico de bolhas com plotly
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size = 'ID', color='City'  )
    st.plotly_chart(fig, use_container_width=True)


def order_by_week(df1):
    # Cria coluna Semana e conta pedidos por semana.
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    cols = ['ID', 'week_of_year']
    df_aux = df1.loc[:, cols].groupby('week_of_year').count().reset_index()

    # Cria grafico de linha com plotly
    fig = px.line (df_aux, x=df_aux['week_of_year'], y='ID')
    st.plotly_chart(fig, use_container_width=True)
    
def order_share_by_week(df1):
    # Quantidade de pedidos por semana / Numero unico de entregadores por semana
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()


    # Juntar os dois dataframes criados
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')

    # Realizar a divisao
    df_aux['order_by_deliver'] = round(df_aux['ID'] / df_aux['Delivery_person_ID'], 1)

    # Criar Grafico de linhas com plotly
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    st.plotly_chart(fig, use_container_width=True)
    

def country_maps(df1):
    # Cria dataframe com latitude e longitude (localizacao) central de cada cidade por tipo de trafego
    cols = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).median().reset_index()

    #cria mapa com folium
    map = folium.Map(location = [
            df_aux['Delivery_location_latitude'].mean(),
            df_aux['Delivery_location_longitude'].mean()],
        zoom_start=10,
        control_scale=True)

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']],
                        popup= location_info[['City', 'Road_traffic_density']]
                        ).add_to(map)

    folium_static (map, width = 1024, height=600 )

# ====================================
# Barra Lateral do streamlit
# ====================================
st.header('Marketplace - Visão Cliente')
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

tab1, tab2, tab3 = st.tabs ( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    with st.container():
        st.markdown('## Pedidos por dia.')
        order_by_day(df1)

    with st.container():
        
        col1, col2 = st.columns(2)
        with col1:
            st.header('Pedidos por tráfego.')
            traffic_order_share(df1)
            
        with col2:
            st.header('Pedidos por cidade e tráfego.')
            traffic_order_city(df1)          
        
    
with tab2:
    with st.container():
        st.header('Order by Week')
        order_by_week(df1)
        
        
    with st.container():
        st.header('Order Share by Week')
        order_share_by_week(df1)
        
    
    
with tab3:
        st.markdown('# Country Maps')
        country_maps(df1)
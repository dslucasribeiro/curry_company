#Libreries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.offline as pyo
import plotly.graph_objects as go
from haversine import haversine
import folium
from streamlit_folium import folium_static
import streamlit as st
from PIL import Image

st.set_page_config( page_title = 'Visão Restaurantes', page_icon="🍝", layout = 'wide')


# Importacao e Cópia
df = pd.read_csv('Dados/train.csv')
df1 = df.copy()

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

def distance(df1):
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df1['distance'] = df1.loc[:, cols].apply( lambda x: 
                        haversine( 
                            (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1 )
    df_aux = round(df1['distance'].mean(),2)
    col2.metric('Distância média', str(df_aux))
    
    

def avg_std(df1, graph):
    if graph == True:
        df_aux = (df1.loc[:, ['Time_taken(min)', 'City' ]].groupby('City')['Time_taken(min)']
                        .agg(['mean', 'std']).reset_index())
        fig = go.Figure()
        fig.add_trace(go.Bar( name='Control', x=df_aux['City'], y=df_aux['mean'], error_y=dict(type='data', array=df_aux['std'])))
        fig.update_layout(barmode='group')
        st.plotly_chart(fig)
    else:
        df_aux = (df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']]
                      .groupby(['City', 'Type_of_order'])['Time_taken(min)']
                      .agg(['mean', 'std']).reset_index())
        st.dataframe(df_aux)



def avg_in_festival(df1):            
    df1['distance'] = df1.loc[:, ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude' ]].apply( lambda x:
            haversine (
            (x['Restaurant_latitude'], x['Restaurant_longitude']),
            (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )
    avg_distance = df1.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index( )
    fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
    st.plotly_chart( fig )
    
    
def avg_df_city_traffic(df1):
    df_aux = (df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']]
            .groupby(['City', 'Road_traffic_density'])['Time_taken(min)'].agg(['mean', 'std']).reset_index())
    fig = (px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='mean',
                    color='std', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std']) ))
    st.plotly_chart(fig)    

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
        st.markdown('### Overall Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            df_aux = df1.loc[:, 'Delivery_person_ID'].nunique()
            col1.metric('Qtd. Entregadores', str(df_aux))
            
        with col2:
            distance(df1)
            
        with col3:
            df_aux = round(df1.loc[df1.loc[:, 'Festival'] == 'Yes', 'Time_taken(min)'].mean(),2)
            col3.metric('T.M com Festival', df_aux)

        with col4:
            df_aux = round(df1.loc[df1.loc[:, 'Festival'] == 'Yes', 'Time_taken(min)'].std(),2)
            col4.metric('DP com Festival', df_aux)

        with col5:
            df_aux = round(df1.loc[df1.loc[:, 'Festival'] == 'No', 'Time_taken(min)'].mean(),2)
            col5.metric('T.M Sem Festival', df_aux)
        with col6:
            df_aux = round(df1.loc[df1.loc[:, 'Festival'] == 'No', 'Time_taken(min)'].std(),2)
            col6.metric('DP Sem Festival', df_aux)
        st.markdown("""---""")
    
    with st.container():
        col1, col2, col3 = st.columns(3 , gap='large')
        with col1:
            st.markdown('##### Tempo médio e desvio padrão de entrega por cidade.')
            avg_std(df1, graph=True)

        with col2:
            st.markdown("")
            
        with col3:
            st.markdown('##### Tempo médio e desvio padrão de entrega por cidade e tipo de pedido.')
            avg_std(df1, graph=False)      
            
        st.markdown("""---""")
        
    
    with st.container():
        col1, col2 = st.columns(2 , gap='large')
        with col1:  
            st.markdown('##### Tempo médio de entrega durantes os Festivais.')
            avg_in_festival(df1)
      
        with col2:
            st.markdown('##### Tempo médio e desvio padrão de entrega por cidade e tipo de tráfego.')
            avg_df_city_traffic(df1)
            

            
        
        
        
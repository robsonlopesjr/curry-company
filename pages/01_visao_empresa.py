import folium
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')


def clean_database(dataframe):
    '''Esta função tem a responsabilidade de limpar o dataframe
        Tipos de limpeza:
        1 - Remoção dos dados NaN
        2 - Mudança do tipo da coluna de dados
        3 - Remoção dos espaços das variáveis de texto
        4 - Formatação da coluna de datas
        5 - Limpeza da coluna de tempo (remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe
    '''
    # Removendo linhas com NaN da base de dados
    linhas_selecionadas = dataframe['Delivery_person_Age'] != 'NaN '
    dataframe = dataframe.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = dataframe['multiple_deliveries'] != 'NaN '
    dataframe = dataframe.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = dataframe['Road_traffic_density'] != 'NaN '
    dataframe = dataframe.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = dataframe['City'] != 'NaN '
    dataframe = dataframe.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = dataframe['Festival'] != 'NaN '
    dataframe = dataframe.loc[linhas_selecionadas, :].copy()

    # Remover o texto de numeros --> '(min) 24'
    dataframe['Time_taken(min)'] = dataframe['Time_taken(min)'].apply(
        lambda x: x.split('(min) ')[1])

    # Converter os tipos das colunas
    dataframe['Delivery_person_Age'] = dataframe['Delivery_person_Age'].astype(
        int)

    dataframe['multiple_deliveries'] = dataframe['multiple_deliveries'].astype(
        int)

    dataframe['Delivery_person_Ratings'] = dataframe['Delivery_person_Ratings'].astype(
        float)

    dataframe['Time_taken(min)'] = dataframe['Time_taken(min)'].astype(int)

    # Precisa usar a biblioteca pandas quando se trata de converter em data
    dataframe['Order_Date'] = pd.to_datetime(
        dataframe['Order_Date'], format='%d-%m-%Y')

    # Resetar o index
    dataframe = dataframe.reset_index(drop=True)

    # Remover os espaços em branco dentro das strings de ID
    dataframe.loc[:, 'ID'] = dataframe.loc[:, 'ID'].str.strip()
    dataframe.loc[:, 'Road_traffic_density'] = dataframe.loc[:,
                                                             'Road_traffic_density'].str.strip()
    dataframe.loc[:, 'Type_of_order'] = dataframe.loc[:,
                                                      'Type_of_order'].str.strip()
    dataframe.loc[:, 'Type_of_vehicle'] = dataframe.loc[:,
                                                        'Type_of_vehicle'].str.strip()
    dataframe.loc[:, 'City'] = dataframe.loc[:, 'City'].str.strip()
    dataframe.loc[:, 'Festival'] = dataframe.loc[:, 'Festival'].str.strip()

    return dataframe


def order_metric(df):
    cols = ['ID', 'Order_Date']
    # Selecao de linhas
    df_aux = df.loc[:, cols].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y='ID')

    return fig


def trafic_order_share(df):
    df_aux = df.loc[:, ['ID',  'Road_traffic_density']].groupby(
        'Road_traffic_density').count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN", :]
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')

    return fig


def trafic_order_city(df):
    df_aux = df.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(
        ['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density',
                     size='ID', color='City')

    return fig


def order_by_week(df):
    # Criar a coluna dia da semana
    df['week_of_day'] = df['Order_Date'].dt.strftime('%U')
    df_aux = df.loc[:, ['week_of_day', 'ID']].groupby(
        'week_of_day').count().reset_index()
    fig = px.line(df_aux, x='week_of_day', y='ID')
    return fig


def order_share_by_week(df):
    df_aux1 = df.loc[:, ['ID', 'week_of_day']].groupby(
        'week_of_day').count().reset_index()
    df_aux2 = df.loc[:, ['Delivery_person_ID', 'week_of_day']
                     ].groupby('week_of_day').nunique().reset_index()
    df_aux = pd.merge(df_aux1, df_aux2, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_day', y='order_by_deliver')
    return fig


def contry_maps(df):
    df_aux = df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude',
                        'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']],
                      popup=location_info[['City', 'Road_traffic_density']]).add_to(map)

    folium_static(map, width=1024, height=600)


# Import dataset
df = pd.read_csv('./dataset/train.csv')

# Limpando os dados
df1 = clean_database(df)


# ===============================================================================
# Barra lateral - Streamlit
# ===============================================================================

st.header('Marketplace - Visão Empresa')

image_path = './image/logo.jpg'
image = Image.open(image_path)
st.sidebar.image(image, width=200)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')


st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY'
)

st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Robson ❤️')

# =========================
# Filtros
# =========================
# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de tânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# ===============================================================================
# layout - Streamlit
# ===============================================================================


tab1, tab2, tab3 = st.tabs(
    ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric
        fig = order_metric(df1)
        st.header('Orders by Day')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():

        col1, col2 = st.columns(2)
        with col1:
            fig = trafic_order_share(df1)
            st.header('Traffic Order Share')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = trafic_order_city(df1)
            st.header('Traffic Order City')
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        fig = order_by_week(df1)
        st.header('Order by Week')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        fig = order_share_by_week(df1)
        st.header('Order Share by Week')
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header('Country Maps')
    contry_maps(df1)

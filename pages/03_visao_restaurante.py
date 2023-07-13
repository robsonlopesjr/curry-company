from datetime import datetime
from haversine import haversine
from PIL import Image
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title='Visão Restaurante',
                   page_icon='🍽️', layout='wide')

# =======================================================================
# Funções
# =======================================================================


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


def top_delivers(df, top_asc):
    df = df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(
        ['City', 'Delivery_person_ID']).max().sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index()

    df_aux1 = df.loc[df['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df.loc[df['City'] == 'Urban', :].head(10)
    df_aux3 = df.loc[df['City'] == 'Semi-Urban', :].head(10)

    df = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index()

    return df


def distance(df, fig):
    if not fig:
        cols = ['Restaurant_latitude', 'Restaurant_longitude',
                'Delivery_location_latitude', 'Delivery_location_longitude']

        df['distance_km'] = df.loc[:, cols].apply(lambda x: haversine(
            (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

        avg_distance = np.round(df['distance_km'].mean(), 2)

        return avg_distance

    else:
        cols = ['Restaurant_latitude', 'Restaurant_longitude',
                'Delivery_location_latitude', 'Delivery_location_longitude']

        df['distance'] = df.loc[:, cols].apply(lambda x: haversine(
            (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

        avg_distance = df.loc[:, ['City', 'distance']
                              ].groupby('City').mean().reset_index()

        # Avg_distance
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'],
                        values=avg_distance['distance'], pull=[0, 0.1, 0])])
        return fig


def avd_std_delivery(df, festival, op):
    """ Está função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Prâmentros:
            Input:
                - df: DataFrame com os dados necesários para o calculo
                - op: Tipo de operação que precisa ser calculado
                 'avg_time': Calcula o tempo médio
                 'std_time': Calcula o desvio padrão do tempo
            Output:
                - df: DaraFrame com 2 colunas e 1 linha
                """
    df_aux = df.loc[:, ['Festival', 'Time_taken(min)']].groupby(
        ['Festival']).agg({'Time_taken(min)': ['mean', 'std']})

    df_aux.columns = ['avg_time', 'std_time']

    df_aux = df_aux.reset_index()
    df_aux = np.round(
        df_aux.loc[df_aux['Festival'] == festival, 'avg_time'], 2)

    return df_aux


def avg_std_time_graph(df):
    df_aux = df.loc[:, ['City', 'Time_taken(min)']].groupby(
        'City').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                         x=df_aux['City'],
                         y=df_aux['avg_time'],
                         error_y=dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')

    return fig


def avg_std_time_on_traffic(df):
    df_aux = df.loc[:, ['City', 'Road_traffic_density', 'Time_taken(min)']].groupby(
        ['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})

    df_aux.columns = ['avg_time', 'std_time']

    df_aux = df_aux.reset_index()
    df_aux.head()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                      color='std_time', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

# ============================================================================
# Import datasett
# ===============================================================================


# Import dataset
df = pd.read_csv('./dataset/train.csv')

# Limpando os dados
df1 = clean_database(df)

# ===============================================================================
# Barra lateral - Streamlit
# ===============================================================================

st.header('Marketplace - Visão Restaurante')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overal Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = df1.loc[:, ['Delivery_person_ID', 'ID']].groupby(
                'Delivery_person_ID').nunique().count()
            st.metric('Entregadores únicos', delivery_unique)

        with col2:
            avg_distance = distance(df1, fig=False)
            st.metric('A distancia média', avg_distance)

        with col3:
            df_aux = avd_std_delivery(df1, 'Yes', 'avg_time')
            col3.metric('Tempo médio', df_aux)

        with col4:
            df_aux = avd_std_delivery(df1, 'Yes', 'std_time')
            col4.metric('STD entrega', df_aux)

        with col5:
            df_aux = avd_std_delivery(df1, 'No', 'avg_time')
            col5.metric('Tempo médio', df_aux)

        with col6:
            df_aux = avd_std_delivery(df1, 'No', 'std_time')
            col6.metric('STD entrega', df_aux)

    with st.container():
        st.markdown('''---''')

        col1, col2 = st.columns(2)

        with col1:
            st.title('Tempo médio de entrega por cidade')
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.title('Distribuição da distância')
            df_aux = df1.loc[:, ['City', 'Type_of_order', 'Time_taken(min)']].groupby(
                ['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})

            df_aux.columns = ['avg_time', 'std_time']

            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)

    with st.container():
        st.title('Distribuição do tempo')

        col1, col2 = st.columns(2)

        with col1:
            fig = distance(df1, fig=True)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)

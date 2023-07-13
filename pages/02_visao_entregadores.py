from datetime import datetime
from PIL import Image
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='Visão Entregadores',
                   page_icon='🚚', layout='wide')


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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')

        with col1:
            # st.subheader('Maior idade')
            # Maior idade dos entregadores
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric(' Maior Idade', maior_idade)

        with col2:
            # st.subheader('Menor idade')
            # Menor idade dos entregadores
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric(' Menor idade', menor_idade)

        with col3:
            # st.subheader('Melhor condição de veículos')
            # condições dos veiculos
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição de veículo', melhor_condicao)

        with col4:
            # st.subheader('Pior condição de veículos')
            # condições dos veiculos
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição de veículo', pior_condicao)

    with st.container():
        st.markdown('''---''')
        st.title('Avaliações')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Avalicao medias por Entregador')
            df_avg_ratings_per_deliver = (df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                          .groupby('Delivery_person_ID')
                                          .mean()
                                          .reset_index())
            st.dataframe(df_avg_ratings_per_deliver)

        with col2:
            st.markdown(' ##### Avalisção média por transito')
            df_avg_std_rating_by_traffic = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby(
                'Road_traffic_density').agg({'Delivery_person_Ratings': ['mean', 'std']}))

            df_avg_std_rating_by_traffic.columns = [
                'delirery_mean', 'delirery_std']

            df_avg_std_rating_by_traffic.reset_index()
            st.dataframe(df_avg_std_rating_by_traffic)

            st.markdown(' ##### Avalisção média por clima')
            df_avg_std_rating_by_wather = df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby(
                'Weatherconditions').agg({'Delivery_person_Ratings': ['mean', 'std']})

            df_avg_std_rating_by_wather.columns = [
                'delirery_mean', 'delirery_std']

            df_avg_std_rating_by_wather.reset_index()
            st.dataframe(df_avg_std_rating_by_wather)

    with st.container():
        st.markdown('''---''')
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Top entregadores mais rápidos')
            df2 = top_delivers(df1, top_asc=True)
            st.dataframe(df2)

        with col2:
            st.subheader('Top entregadores mais lentos')
            df2 = top_delivers(df1, top_asc=False)
            st.dataframe(df2)

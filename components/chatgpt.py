from menu_styles import *
from functions import *
from app import *

from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd


import openai
from dotenv import load_dotenv
import os

load_dotenv()

#definicao da chave da API
openai.api_key = os.getenv("OPENAI_API_KEY")


try:
    df_historico = pd.read_csv('historical_msgs.csv', index_col=0)

except:
    df_historico = pd.DataFrame(columns=['user', 'chatGPT'])
    
df_historico.to_csv('historical_msgs.csv')

df_data = pd.read_csv('book_data.csv')
df_data.drop('exchange', axis=1, inplace=True)
df_data['date'] = df_data['date'].str.replace('T00:00:00', '')

def generate_card_gpt(pesquisa):
    cardNovo =  dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Row([
                                    dbc.Col([
                                        html.H5([html.I(className='fa fa-desktop', style={"fontSize": '85%'}), " ChatGPT: "], className='textoQuartenario'),
                                        html.H5(str(pesquisa), className='textoQuartenarioBranco')
                                    ], md=12, style={'text-align' : 'left'}),                              
                                ]),
                            ], md=11, xs=6, style={'text-align' : 'left'}),
                        ])
                    ])
                ], className='card_chatgpt')
            ])
        ], className='g-2 my-auto')

    return cardNovo
def generate_card_user(pesquisa):
    cardNovo =  dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Row([
                                    dbc.Col([
                                        html.H5([html.I(className='fa fa-user-circle', style={"fontSize": '85%'}), " User: "], className='textoQuartenario'),
                                        html.H5(str(pesquisa), className='textoQuartenarioBranco')
                                    ], md=12, style={'text-align' : 'left'}),                              
                                ]),
                            ], md=11, xs=6, style={'text-align' : 'left'}),
                        ])
                    ])
                ], className='card_chatgpt')
            ])
        ], className='g-2 my-auto')

    return cardNovo

def generateCardsList(card_pergunta, card_resposta):

    cardAgrupado = dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    card_pergunta
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    card_resposta
                ])
            ]),
        ])
    ]),

    return cardAgrupado


def gerar_resposta(messages):
    try:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        #model="gpt-3.5-turbo-0301", ## ate 1 junho 2023
        messages=messages,
        max_tokens=1024,
        temperature=1,
        # stream=True
        )
        retorno = response.choices[0].message.content
    except:
        retorno = 'Não foi possível pesquisar. ChatGPT fora do ar'
    return retorno

def clusterCards(df_msgs_store):

    df_historical_msgs = pd.DataFrame(df_msgs_store)
    cardsList = []
    
    for line in df_historical_msgs.iterrows():
        card_pergunta = generate_card_user(line[1]['user'])
        card_resposta = generate_card_gpt(line[1]['chatGPT'])

        cardsList.append(card_pergunta)
        cardsList.append(card_resposta)


    return cardsList

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    "AsimoChat"
                ], className='textoPrincipal', style={'margin-top' : '10px'})
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Input(id="msg_user", type="text", placeholder="Insira uma mensagem")
                ], md=10),
                dbc.Col([
                    dbc.Col([dbc.Button("Pesquisa", id="botao_search")])
                ], md=2)
            ])
        ]),
        dbc.Col([

        ],md=12, id='cards_respostas', style={"height": "100%", "maxHeight": "25rem", "overflow-y": "auto"}),
    ], className='g-2 my-auto')
],fluid=True),



@app.callback(
    # Output('historical_msgs_store', 'data'),
    Output('cards_respostas', 'children'),
    Input('botao_search', 'n_clicks'),
    # Input('historical_msgs_store', 'data'),
    State('msg_user', 'value'),
    # prevent_initial_call=True
)

def add_msg(n, msg_user):

    df_historical_msgs = pd.read_csv('historical_msgs.csv', index_col=0)
    # print(df_historical)

    if msg_user == None:
        lista_cards = clusterCards(df_historical_msgs)
        return lista_cards


    mensagem = f'{df_data}, considerando somente os dados existentes dentro do dataframe, qual é a resposta exata para a pergunta: ' + msg_user

    mensagens = []
    mensagens.append({"role": "user", "content": str(mensagem)})

    pergunta_user = mensagens[0]['content']
    resposta_chatgpt = gerar_resposta(mensagens)

    # print(type(pergunta_user))

    if pergunta_user == 'None' or  pergunta_user == '':
        lista_cards = clusterCards(df_historical_msgs)
        return lista_cards

    new_line = pd.DataFrame([[pergunta_user, resposta_chatgpt]], columns=['user', 'chatGPT'])
    # print('TA AQUI *************************************************************')
    # print(new_line)
    # print(type(new_line))
    new_line['user'] = new_line['user'].str.split(':')
    new_line['user'] = new_line['user'][0][-1]
    df_historical_msgs = pd.concat([new_line, df_historical_msgs], ignore_index = True)

    # import pdb; pdb.set_trace()   

    df_historical_msgs.to_csv('historical_msgs.csv')
    
    lista_cards = clusterCards(df_historical_msgs)



    return lista_cards

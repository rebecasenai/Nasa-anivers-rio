from flask import Flask, render_template, request
import requests
from datetime import datetime
import os
from deep_translator import GoogleTranslator
import hashlib
import json

app = Flask(__name__)

NASA_API_KEY = "DEMO_KEY"
tradutor = GoogleTranslator(source='en', target='pt')

cache_traducao = {}

def traduzir_texto(texto):
    """Função auxiliar para traduzir com cache"""
    if not texto or len(texto.strip()) == 0:
        return texto
    
    # Cria uma chave única para o texto
    chave = hashlib.md5(texto.encode()).hexdigest()
    
    # Verifica se já traduziu este texto antes
    if chave in cache_traducao:
        return cache_traducao[chave]
    
    try:
        # Traduz e armazena no cache
        traducao = tradutor.translate(texto)
        cache_traducao[chave] = traducao
        return traducao
    except Exception as e:
        print(f"Erro na tradução: {e}")
        return texto

@app.route('/')
def introducao():
    return render_template('index.html')

@app.route('/buscar', methods=['POST'])
def buscar_foto():
    data_nascimento = request.form.get('data_nascimento')
    
    if not data_nascimento:
        return render_template('resultado.html', 
                             erro="Por favor, selecione uma data.")
    
    try:
        data_obj = datetime.strptime(data_nascimento, '%Y-%m-%d')
        data_inicio = datetime(1995, 6, 16)
        
        if data_obj < data_inicio:
            return render_template('resultado.html',
                                 erro="O APOD da NASA começou em 16 de Junho de 1995. Por favor, escolha uma data posterior.")
        
        if data_obj > datetime.now():
            return render_template('resultado.html',
                                 erro="Não é possível buscar fotos do futuro!")
        
        data_formatada = data_obj.strftime('%d/%m/%Y')
        
        url = f"https://api.nasa.gov/planetary/apod"
        params = {
            'api_key': NASA_API_KEY,
            'date': data_nascimento,
            'thumbs': True
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            
            # Usando a função de tradução com cache
            foto_data = {
                'titulo': traduzir_texto(dados.get('title', 'Sem título')),
                'titulo_original': dados.get('title', 'Sem título'),
                'data': data_formatada,
                'explicacao': traduzir_texto(dados.get('explanation', 'Sem descrição disponível.')),
                'explicacao_original': dados.get('explanation', 'Sem descrição disponível.'),
                'url': dados.get('url', ''),
                'tipo': dados.get('media_type', 'image'),
                'copyright': dados.get('copyright', 'NASA'),
                'thumbnail': dados.get('thumbnail_url', '')
            }
            
            return render_template('resultado.html', foto=foto_data)
            
        elif response.status_code == 429:
            return render_template('resultado.html',
                                 erro="Limite de requisições excedido. Por favor, tente novamente mais tarde.")
        else:
            return render_template('resultado.html',
                                 erro=f"Não foi possível encontrar uma foto para esta data. Código: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        return render_template('resultado.html',
                             erro=f"Erro de conexão: {str(e)}")
    except ValueError as e:
        return render_template('resultado.html',
                             erro=f"Data inválida: {str(e)}")
    except Exception as e:
        return render_template('resultado.html',
                             erro=f"Erro inesperado: {str(e)}")

@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('error404.html'), 404

@app.errorhandler(500)
def erro_servidor(e):
    return render_template('error500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
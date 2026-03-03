from flask import Flask, render_template, request
import requests
from datetime import datetime
import os
import sys

# Configuração para Vercel
app = Flask(__name__)

# Sua chave da NASA (pegando de variável de ambiente por segurança)
NASA_API_KEY = os.environ.get('NASA_API_KEY', 'LgiIulhdGC0XWgMh4YGxB0dhusSP5we882B2DmKd')

@app.route('/')
def introducao():
    """Página inicial de introdução da NASA"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Erro ao carregar página: {str(e)}", 500

@app.route('/buscar', methods=['POST'])
def buscar_foto():
    """Busca a foto do APOD para a data selecionada"""
    
    try:
        data_nascimento = request.form.get('data_nascimento')
        
        if not data_nascimento:
            return render_template('resultado.html', 
                                 erro="Por favor, selecione uma data.")
        
        # Valida a data
        data_obj = datetime.strptime(data_nascimento, '%Y-%m-%d')
        data_inicio = datetime(1995, 6, 16)
        
        if data_obj < data_inicio:
            return render_template('resultado.html',
                                 erro="O APOD da NASA começou em 16 de Junho de 1995. Por favor, escolha uma data posterior.")
        
        if data_obj > datetime.now():
            return render_template('resultado.html',
                                 erro="Não é possível buscar fotos do futuro!")
        
        # Formata a data para exibição
        data_formatada = data_obj.strftime('%d/%m/%Y')
        
        # Faz a requisição à API da NASA
        url = "https://api.nasa.gov/planetary/apod"
        params = {
            'api_key': NASA_API_KEY,
            'date': data_nascimento,
            'thumbs': True
        }
        
        print(f"Buscando foto para data: {data_nascimento}", file=sys.stderr)
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            
            foto_data = {
                'titulo': dados.get('title', 'Sem título'),
                'data': data_formatada,
                'explicacao': dados.get('explanation', 'Sem descrição disponível.'),
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
        print(f"Erro de conexão: {str(e)}", file=sys.stderr)
        return render_template('resultado.html',
                             erro=f"Erro de conexão: {str(e)}")
    except ValueError as e:
        print(f"Data inválida: {str(e)}", file=sys.stderr)
        return render_template('resultado.html',
                             erro=f"Data inválida: {str(e)}")
    except Exception as e:
        print(f"Erro inesperado: {str(e)}", file=sys.stderr)
        return render_template('resultado.html',
                             erro=f"Erro inesperado: {str(e)}")

@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('index.html', erro="Página não encontrada"), 404

@app.errorhandler(500)
def erro_servidor(e):
    return render_template('index.html', erro="Erro interno do servidor"), 500

# Para desenvolvimento local
if __name__ == '__main__':
    app.run(debug=True)

# Para Vercel - EXPORTE o app (NÃO use app.run)
# Esta linha é CRUCIAL para a Vercel
application = app
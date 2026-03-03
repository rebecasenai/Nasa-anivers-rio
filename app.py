from flask import Flask, render_template, request
import requests
from datetime import datetime
import os

app = Flask(__name__)

# Sua API Key https://api.nasa.gov/
NASA_API_KEY = "DEMO_KEY"  

@app.route('/')
def introducao():
    """Página inicial de introdução da NASA"""
    return render_template('index.html')

@app.route('/buscar', methods=['POST'])
def buscar_foto():
    """Busca a foto do APOD para a data selecionada"""
    
    data_nascimento = request.form.get('data_nascimento')
    
    if not data_nascimento:
        return render_template('resultado.html', 
                             erro="Por favor, selecione uma data.")
    
    try:
        data_obj = datetime.strptime(data_nascimento, '%Y-%m-%d')
        data_inicio = datetime(1995, 6, 16)  # Início do APOD
        
        if data_obj < data_inicio:
            return render_template('resultado.html',
                                 erro="O APOD da NASA começou em 16 de Junho de 1995. Por favor, escolha uma data posterior.")
        
        if data_obj > datetime.now():
            return render_template('resultado.html',
                                 erro="Não é possível buscar fotos do futuro!")
        
        # formata a data para exibição
        data_formatada = data_obj.strftime('%d/%m/%Y')
        
        # faz a requisicao de daods da nasa
        url = f"https://api.nasa.gov/planetary/apod"
        params = {
            'api_key': NASA_API_KEY,
            'date': data_nascimento,
            'thumbs': True  # Para vídeos
        }
        
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
    # renderiza página de erro dedicada
    return render_template('error404.html'), 404

@app.errorhandler(500)
def erro_servidor(e):
    # utiliza template específico para erro interno
    return render_template('error500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
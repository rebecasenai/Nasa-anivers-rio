from flask import Flask, render_template, request
import requests
from datetime import datetime
import os

app = Flask(__name__)


NASA_API_KEY = "LgiIulhdGC0XWgMh4YGxB0dhusSP5we882B2DmKd"

@app.route('/')
def introducao():
    """Página inicial"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Erro: {str(e)}"

@app.route('/buscar', methods=['POST'])
def buscar_foto():
    """Busca a foto"""
    try:
        data_nascimento = request.form.get('data_nascimento')
        
        if not data_nascimento:
            return render_template('resultado.html', erro="Selecione uma data.")
        
        # Validação da data
        data_obj = datetime.strptime(data_nascimento, '%Y-%m-%d')
        data_inicio = datetime(1995, 6, 16)
        
        if data_obj < data_inicio:
            return render_template('resultado.html',
                                 erro="Disponível apenas a partir de 16/06/1995")
        
        # Requisição à API
        url = "https://api.nasa.gov/planetary/apod"
        params = {
            'api_key': NASA_API_KEY,
            'date': data_nascimento,
            'thumbs': True
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            
            foto_data = {
                'titulo': dados.get('title', 'Sem título'),
                'data': data_obj.strftime('%d/%m/%Y'),
                'explicacao': dados.get('explanation', 'Sem descrição'),
                'url': dados.get('url', ''),
                'tipo': dados.get('media_type', 'image'),
                'copyright': dados.get('copyright', 'NASA')
            }
            
            return render_template('resultado.html', foto=foto_data)
        else:
            return render_template('resultado.html',
                                 erro=f"Erro na API: {response.status_code}")
    
    except Exception as e:
        return render_template('resultado.html', erro=str(e))

# LINHA CRUCIAL PARA A VERCEL - NÃO REMOVA!
application = app


if __name__ == '__main__':
    app.run(debug=True)
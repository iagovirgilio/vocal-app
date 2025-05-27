# Imagem base oficial do Python
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . /app

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta padrão do Streamlit
EXPOSE 8080

# Comando para rodar o Streamlit
CMD ["sh", "-c", "streamlit run vocal_app.py --server.port=$PORT --server.address=0.0.0.0"]

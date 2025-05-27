# 🎵 Calculadora de Extensão Vocal

Uma aplicação web desenvolvida em Python que ajuda cantores a encontrar a tonalidade ideal para suas músicas, baseada em sua extensão vocal.

## 📋 Funcionalidades

- **Análise de Extensão Vocal**: Calcula e visualiza a extensão vocal do cantor
- **Análise de Músicas**: Identifica a extensão de notas de uma música
- **Transposição Automática**: Sugere a melhor tonalidade para cantar a música
- **Margens de Conforto**: Considera margens de segurança para cantar confortavelmente
- **Interface Intuitiva**: Interface web amigável e responsiva usando Streamlit

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/vocal.git
cd vocal
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 💻 Uso

1. Inicie a aplicação:
```bash
streamlit run vocal_app.py
```

2. Acesse a aplicação no navegador:
```
http://localhost:8080
```

3. Siga os passos na interface:
   - Defina sua extensão vocal (notas mais grave e aguda)
   - Configure a música (notas e tonalidade)
   - Ajuste a margem de conforto
   - Analise os resultados

## 🎯 Como Funciona

1. **Extensão Vocal**:
   - O cantor define suas notas mais grave e aguda
   - O sistema calcula a extensão total em semitons

2. **Análise da Música**:
   - Define as notas mais grave e aguda da música
   - Identifica a tonalidade original
   - Calcula a extensão total

3. **Transposição**:
   - Calcula o centro da extensão vocal
   - Calcula o centro da extensão da música
   - Sugere a melhor transposição para alinhar os centros
   - Considera margens de conforto nas extremidades

4. **Resultados**:
   - Mostra a nova tonalidade sugerida
   - Exibe as notas transpostas
   - Indica as margens de conforto
   - Avalia a compatibilidade

## 🛠️ Tecnologias Utilizadas

- Python 3.8+
- Streamlit
- TypeScript
- HTML/CSS

## 📝 Requisitos

- Python 3.8 ou superior
- Streamlit
- Navegador web moderno

## 🤝 Contribuindo

1. Faça um Fork do projeto
2. Crie uma Branch para sua Feature (`git checkout -b feature/AmazingFeature`)
3. Faça o Commit das suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Faça o Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ✨ Recursos Adicionais

- Suporte a tonalidades maiores e menores
- Conversão automática entre notações (bemóis/sustenidos)
- Interface em português
- Design responsivo e moderno
- Feedback visual imediato

## 📞 Suporte

Para suporte, envie um email para iagovirgilio@gmail.com.com ou abra uma issue no GitHub.

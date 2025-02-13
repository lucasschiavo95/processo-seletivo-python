# Flask API - Relatórios

Esta API desenvolvida com Flask gera relatórios baseados em dados de plataformas de anúncios.

## 📌 Pré-requisitos

Antes de iniciar, certifique-se de ter instalado:

* Python 3.8+
* Pip
* Virtualenv (opcional, mas recomendado)

## 🚀 Instalação e Execução

### Clone o repositório

```bash
git clone https://github.com/seu-repositorio/processo-seletivo-python.git
cd processo-seletivo-python
```

### Crie e ative um ambiente virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar no Windows
venv\Scripts\activate

# Ativar no Linux/Mac
source venv/bin/activate
```

### Instale as dependências

```bash
pip install -r requirements.txt
```

### Configure as variáveis de ambiente

```bash
# Linux/Mac
export FLASK_APP=app.py
export FLASK_ENV=development

# Windows (PowerShell)
$env:FLASK_APP="app.py"
$env:FLASK_ENV="development"
```

### Execute o servidor

```bash
flask run
```

A API estará disponível em http://127.0.0.1:5000/

## 📡 Endpoints Disponíveis

* **GET /** - Informações do desenvolvedor
* **GET /api** - Endpoints disponíveis
* **GET /api/platforms** - Lista todas as plataformas
* **GET /resumo** - Gera um relatório resumido para uma plataforma específica

## 📄 Licença

Este projeto está sob a licença MIT. Sinta-se à vontade para usá-lo e modificá-lo.

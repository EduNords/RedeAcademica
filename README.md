# Rede Academica - Django Project

Bem-vindo ao projeto Rede Academica! Este é um guia completo para configurar e executar o projeto em sua máquina local.

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git

## 🚀 Como rodar o projeto

### 1. Clonar o repositório

Primeiro, clone o repositório do projeto para sua máquina local:

```bash
git clone https://github.com/EduNords/RedeAcademica.git
cd RedeAcademica
```

### 2. Criar e ativar o ambiente virtual (venv)

É uma boa prática usar um ambiente virtual para isolar as dependências do projeto.

**No Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**No Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Você saberá que o ambiente virtual está ativo quando ver `(venv)` no início da linha de comando.

### 3. Instalar as dependências

Com o ambiente virtual ativado, instale o Django e outras dependências:

```bash
pip install -r requirements.txt
```

Se o arquivo `requirements.txt` não existir, instale o Django manualmente:

```bash
pip install django
```

### 4. Configurar o banco de dados

Antes de rodar o projeto, é necessário criar as tabelas do banco de dados. Execute as migrações:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Criar um superusuário (opcional)

Para acessar o painel administrativo do Django, crie um superusuário:

```bash
python manage.py createsuperuser
```

Siga as instruções no terminal para definir username, email e senha.

username: admin
email: admin@gmail.com
senha: admin ( no seu terminal ao digitar não vai aparecer as letras, isso é uma configuração de segurança... digite mesmo assim e confirme )
confirmar senha: admin  ( no seu terminal ao digitar não vai aparecer as letras, isso é uma configuração de segurança... digite mesmo assim e confirme )

### 6. Rodar o servidor de desenvolvimento

Agora você está pronto para iniciar o servidor:

```bash
python manage.py runserver
```

O servidor estará disponível em: `http://127.0.0.1:8000/`

Para acessar o painel administrativo: `http://127.0.0.1:8000/admin/`

## 📁 Estrutura do projeto

```
projeto/
│
├── app/                # settings, urls
├── core/               # views, templates, forms, models, admin
├── .gitignore          # Arquivos ignorados pelo Git
├── manage.py           # Script de gerenciamento do Django
└── requirements.txt    # Dependências do projeto
```

## 🛠️ Comandos úteis

### Criar um novo app Django
```bash
python manage.py startapp nome_do_app
```

### Coletar arquivos estáticos
```bash
python manage.py collectstatic
```

### Criar novas migrações após alterações nos models
```bash
python manage.py makemigrations
python manage.py migrate
```

### Desativar o ambiente virtual
```bash
deactivate
```

## 📝 Notas importantes

- Sempre ative o ambiente virtual antes de trabalhar no projeto
- Não commite o diretório `venv/` para o repositório (ele já está no .gitignore)
- Mantenha o arquivo `requirements.txt` atualizado com as dependências do projeto
- Para atualizar o `requirements.txt`:
  ```bash
  pip freeze > requirements.txt
  ```

## 🤝 Como Contribuir com o Projeto

### 1. Inicializar o Git no seu projeto local

Se você já tem o código do projeto na sua máquina, comece inicializando o Git:
```bash
# Navegue até a pasta do projeto
cd seu-repositorio

# Inicialize o repositório Git
git init
```

### 2. Conectar ao repositório remoto

Conecte seu repositório local ao repositório no GitHub:
```bash
# Adicione o repositório remoto (substitua a URL pela do repositório)
git remote add origin https://github.com/EduNords/seu-repositorio.git

# Verifique se foi configurado corretamente
git remote -v
```

### 3. Baixar o código mais recente

Antes de fazer alterações, sincronize com a versão mais recente do projeto:
```bash
# Baixe as alterações do repositório remoto
git pull origin main
```

### 4. Fazer suas alterações no código

Agora você pode modificar, adicionar ou remover arquivos no projeto conforme necessário.

### 5. Verificar as alterações

Após modificar o código, veja o que foi alterado:
```bash
# Ver os arquivos modificados
git status

# Ver as alterações detalhadas
git diff
```

### 6. Adicionar as alterações

Adicione os arquivos modificados ao staging:
```bash
# Adicionar arquivos específicos
git add caminho/do/arquivo.py

# Ou adicionar todas as alterações de uma vez
git add .
```

### 7. Fazer o commit

Salve suas alterações com uma mensagem descritiva:
```bash
# Commit com mensagem curta
git commit -m "Adiciona funcionalidade de login"

# Commit com mensagem detalhada
git commit -m "Adiciona funcionalidade de login" -m "- Implementa autenticação de usuário
- Adiciona validação de formulário
- Atualiza página de login"
```

**Dicas para boas mensagens de commit:**
- Use verbos no imperativo: "Adiciona", "Corrige", "Remove"
- Seja claro e específico sobre o que foi feito
- Mantenha a primeira linha com até 50 caracteres

### 8. Enviar para o GitHub

Envie suas alterações para o repositório remoto:
```bash
# Enviar para a branch main
git push origin main

# Se for a primeira vez, use:
git push -u origin main
```

### 9. Criar um Pull Request

Depois de fazer o push, acesse o repositório no GitHub e:

1. Vá até a página do repositório
2. Clique em **"Pull requests"**
3. Clique em **"New pull request"**
4. Selecione sua branch (se aplicável)
5. Preencha o título e a descrição explicando suas alterações
6. Clique em **"Create pull request"**

**Exemplo de descrição:**
```
## O que foi alterado
- Implementei a funcionalidade de cadastro de usuários
- Corrigi bug no formulário de contato
- Atualizei a documentação

## Por que essa mudança é necessária
Para permitir que novos usuários se registrem no sistema

## Como testar
1. Acesse a página de cadastro
2. Preencha o formulário
3. Verifique se o usuário foi criado
```

### Comandos Git Úteis
```bash
# Ver histórico de commits
git log --oneline

# Desfazer alterações não commitadas em um arquivo
git checkout -- arquivo.py

# Ver status resumido
git status -s

# Atualizar repositório local
git pull origin main

# Ver configurações do repositório
git config --list
```

### Configuração Inicial do Git (primeira vez)

Se é sua primeira vez usando Git, configure seu nome e email:
```bash
# Configurar nome
git config --global user.name "Seu Nome"

# Configurar email
git config --global user.email "seu.email@example.com"

# Verificar configurações
git config --global --list
```

## 📄 Licença

Este projeto está sob a licença MIT.

## 👤 Autor

**Equipe Rede Academica**
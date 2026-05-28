# Deploy em Nuvem

Este projeto Flask pode ser publicado em provedores de nuvem que suportem Docker ou aplicativos Python.

## Opção 1: Usar Docker

1. Construir a imagem:
   ```bash
   docker build -t webcosmeticos .
   ```
2. Executar localmente para testes:
   ```bash
   docker run -e FLASK_DEBUG=false -p 5000:5000 webcosmeticos
   ```
3. Acesse em:
   ```
   http://localhost:5000
   ```

## Opção 2: Hospedar em um provedor de nuvem

### Render
- Crie um novo serviço Web no Render.
- Use o repositório Git como fonte.
- Escolha deployment via Docker.
- A porta padrão é `5000`.

### Railway
- Crie um novo projeto Railway.
- Adicione um serviço Web.
- Use Dockerfile ou Python com `Procfile`.
- Defina a variável `PORT` se necessário.

### Heroku
- Faça login e crie um app.
- Faça deploy pelo Git.
- O `Procfile` já está incluído.

## Variáveis de ambiente

- `PORT`: porta do servidor (padrão `5000`)
- `FLASK_DEBUG`: `true` ou `false` (recomendado `false` em produção)

## Observações

- O Flask em `app.py` já foi preparado para rodar em `0.0.0.0`.
- Em produção, use `gunicorn` em vez do servidor de desenvolvimento integrado.
- Se for usar `WeasyPrint`, o container já instala as dependências de sistema mínimo necessárias.

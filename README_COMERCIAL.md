# JARVIS Mega-Sena — Commercial Launch Kit

Este pacote contém o app JARVIS 3.0 e materiais para transformar o projeto em produto digital.

## Estrutura
- `app.py` — aplicativo JARVIS 3.0
- `requirements.txt` — dependências
- `site/index.html` — página de vendas inicial
- `copy/` — textos para cadastro, página de vendas e FAQ
- `legal/` — aviso de responsabilidade
- `integracoes/webhook.md` — arquitetura de integração por webhook

## Publicação
1. Publique `app.py` e `requirements.txt` no repositório do app.
2. Hospede a página `site/index.html` em um serviço de páginas estáticas ou no seu domínio.
3. Crie o produto/assinatura na plataforma de checkout escolhida.
4. Substitua os placeholders `[LINK...]` pelos links reais.
5. Configure webhook e backend de controle de acesso antes de vender acesso privado ao app.

## Importante
O app atual é a camada de análise. Para um SaaS comercial com login e controle automático de acesso, ainda é necessário um backend com banco de dados, autenticação e processamento dos webhooks do checkout.

# LifeOS

venv\Scripts\activate

Sistema pessoal de organização de vida — desenvolvido como projeto de longo prazo para reunir
estudos, tarefas, calendário e (futuramente) financeiro e esportes em um único lugar.

> Projeto pessoal em desenvolvimento contínuo, iniciado a partir da tentativa de reaproveitar
> hardware antigo (uma TV Box) e evoluído para um sistema web completo em Django.

## Funcionalidades

- **Autenticação** — login individual protegendo todo o sistema.
- **Dashboard** — visão consolidada de tarefas da semana, próximas provas/trabalhos, próximos
  eventos e calendário de sequência de estudos.
- **Tarefas** — criação, edição, conclusão e exclusão, com filtro por status e prioridade.
- **Estudos**:
  - Matérias, provas, trabalhos.
  - Sistema de notas por tipo (prova, trabalho, atividade, caderno), com totais por bimestre e
    total anual.
  - Conteúdos estudados, com status (falta estudar / estudado / revisado) e controle de revisão
    via Anki.
  - Timer Pomodoro integrado, com registro automático (ou parcial) do tempo estudado.
  - Calendário visual de sequência de estudos ("streak"), com possibilidade de marcar dias com
    justificativa.
- **Calendário** — visualização mensal unificando eventos, provas e trabalhos, com suporte a
  eventos recorrentes (RRULE) e sincronização com Google Agenda.

## Tecnologias

- Python + Django
- SQLite (desenvolvimento) → PostgreSQL (produção, planejado)
- Bootstrap 5
- Google Calendar API (OAuth 2.0)
- python-dateutil (cálculo de recorrência)

## Como rodar o projeto localmente

```bash
git clone <url-do-repositorio>
cd lifeos

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt

# Copie .env.example para .env e preencha os valores
copy .env.example .env         # Windows
# cp .env.example .env         # Linux/Mac

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse `http://127.0.0.1:8000`.

Para a integração com Google Agenda, é necessário configurar credenciais OAuth no Google Cloud
Console e posicionar o arquivo `google_credentials.json` na raiz do projeto (não versionado, por
segurança). Veja o documento de arquitetura para o passo a passo completo.

## Documentação do projeto

- [Documento de Visão](./LifeOS_Documento_de_Visao.md)
- [Documento de Requisitos](./LifeOS_Documento_de_Requisitos.md)
- [Documento de Arquitetura](./LifeOS_Documento_de_Arquitetura.md)

## Roadmap

- [x] v0.1 — Login, dashboard, tarefas
- [x] v0.2 — Estudos (matérias, notas, conteúdos, Pomodoro, sequência de estudos)
- [x] v0.3 — Calendário (eventos, recorrência, sincronização com Google Agenda)
- [ ] v1.0 — Consolidação e estabilização
- [ ] Pós v1.0 — Financeiro, Esporte, sincronização de tarefas com Microsoft To Do

## Autor

Projeto pessoal desenvolvido por Davi, com uso contínuo planejado ao longo dos próximos anos.
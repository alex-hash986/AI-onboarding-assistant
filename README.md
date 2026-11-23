# AI-onboarding-assistant

ИИ-ассистент помогает новым сотрудникам вымышленной IT-компании «НейроСтек» пройти первые шаги адаптации и найти нужную информацию.

## Бизнес-задачи

- Снизить число повторных вопросов к HR и IT-поддержке.
- Дать новичкам единые инструкции по оформлению и получению доступов.
- Направлять вопросы об оплате, документах и рабочих процессах ответственным отделам.

## Структура проекта

| Файл | Назначение |
| --- | --- |
| [README.md](README.md) | Обзор проекта и быстрый старт |
| [STATUS.md](STATUS.md) | Состояние проекта и история итераций |
| [docs/company_profile.md](docs/company_profile.md) | Паспорт вымышленной компании |
| [docs/admin_guide.md](docs/admin_guide.md) | Руководство для администратора и HR по обновлению базы знаний и регрессионной проверке |
| [docs/dialog_examples.md](docs/dialog_examples.md) | Шесть примеров ответов, включая эскалации и случаи, когда в базе нет ответа |
| [prompts/system_prompt.md](prompts/system_prompt.md) | Системные инструкции ассистента |
| [knowledge_base/departments_and_contacts.csv](knowledge_base/departments_and_contacts.csv) | Отделы, контакты, маршруты обращений и сроки первого ответа |
| [knowledge_base/processes_and_faq.csv](knowledge_base/processes_and_faq.csv) | Рабочие процессы и ответы на частые вопросы |
| [knowledge_base/tools_setup_guides.csv](knowledge_base/tools_setup_guides.csv) | Инструкции по настройке корпоративных инструментов |
| [knowledge_base/onboarding_checklists.csv](knowledge_base/onboarding_checklists.csv) | Чек-листы адаптации сотрудников |
| [tests/test_scenarios.json](tests/test_scenarios.json) | 12 сценариев проверки, включая эскалации и защиту системных инструкций |
| [scripts/run_eval_responses.py](scripts/run_eval_responses.py) | Автоматический прогон сценариев через Responses API |
| [scripts/custom_gpt_checklist.md](scripts/custom_gpt_checklist.md) | Чек-лист настройки и ручной проверки Custom GPT |

## Быстрый старт

### ChatGPT Custom GPT

1. Если в вашем рабочем пространстве доступен редактор GPT, откройте его и вставьте содержимое `prompts/system_prompt.md` в поле Instructions.
2. Загрузите в Knowledge пять файлов: `docs/company_profile.md` и все четыре CSV из `knowledge_base/`.
3. Откройте Preview и проверьте ответы по `tests/test_scenarios.json`. Используйте `scripts/custom_gpt_checklist.md` для последовательной проверки настроек и ответов.

### Responses API

Для прогона нужны Python и ключ OpenAI API. Из корня проекта выполните в PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install openai
```

Задайте `OPENAI_API_KEY` в текущей сессии PowerShell и запустите проверку:

```powershell
.\.venv\Scripts\python.exe scripts/run_eval_responses.py
```

Скрипт проверяет маркеры эскалации, отделы и ключевые фразы. Результаты сохраняются в `tests/eval_results.json`.

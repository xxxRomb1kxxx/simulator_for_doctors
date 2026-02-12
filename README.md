# 🏥 **Симулятор для врачей** (BFU Patient Bot) 🤖

> **Интеллектуальный Telegram-бот** для симуляции диалога с пациентом, первичной диагностики и формирования медицинской карты с использованием **GigaChat** и **FSM-архитектуры (aiogram 3.x)**.

<div align="center">

[![Tests](https://img.shields.io/github/actions/workflow/status/xxxRomb1kxxx/simulator_for_doctors/test.yml?branch=main&label=tests&logo=pytest)](https://github.com/xxxRomb1kxxx/simulator_for_doctors/actions/workflows/test.yml)
[![Coverage](https://codecov.io/gh/xxxRomb1kxxx/simulator_for_doctors/branch/main/graph/badge.svg)](https://codecov.io/gh/xxxRomb1kxxx/simulator_for_doctors)
[![Linting](https://img.shields.io/github/actions/workflow/status/xxxRomb1kxxx/simulator_for_doctors/lint.yml?branch=main&label=linting&logo=flake8)](https://github.com/xxxRomb1kxxx/simulator_for_doctors/actions/workflows/lint.yml)
[![Python](https://img.shields.io/badge/python-3.13+-blue?logo=python)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/xxxRomb1kxxx/coverage.json)](https://codecov.io/gh/xxxRomb1kxxx/simulator_for_doctors)

</div>

---

## 🎯 **Возможности**

| Функция | Описание |
|---------|----------|
| 🧑‍⚕️ **5 клинических кейсов** | Аппендицит, Диабет, Анемия, Туберкулёз, Эпилепсия |
| 💬 **Естественный диалог** | GigaChat имитирует речь пациента |
| 📝 **Сбор жалоб** | Интеллектуальное извлечение симптомов |
| 📋 **Медкарта** | Автоматическая структуризация данных |
| ✅ **Проверка диагноза** | Сравнение с эталоном (>0.8) |
| 🎮 **Управление** | `/диагноз`, `/завершить` всегда |
| 📊 **Тестирование** | Покрытие **>65%** (цель 80%) |
| 🚀 **CI/CD** | Автотесты, линтинг, деплой |

---

## 🎮 **Демонстрация**

👨‍⚕️ Вы: Здравствуйте, на что жалуетесь?
👤 Пациент: Добрый день, доктор. У меня болит живот, уже 6 часов.

👨‍⚕️ Вы: Где именно болит?
👤 Пациент: Сначала вокруг пупка, теперь внизу справа.

👨‍⚕️ Вы: Температура есть?
👤 Пациент: Да, 37.5, и тошнит немного.

> **`/диагноз`** → система оценит правильность ответа ✅

---

## 🛠 **Технологический стек**

### **Backend**
🐍 Python 3.13+
🤖 aiogram 3.x (FSM, роутинг)
🧠 GigaChat API
🔍 Pydantic (валидация)

### **Тестирование** 
🧪 Pytest + pytest-asyncio (68+ тестов)
📈 pytest-cov (>65% покрытие)
🎭 unittest.mock

### **Качество кода**
🎨 Black
🔤 isort
🔎 flake8
🧪 mypy (скоро)
🛡️ bandit

### **CI/CD**
⚡ GitHub Actions
📊 Codecov
🚀 Автодеплой VPS

---

## ⚡ **Быстрый старт**

### **Требования**
- Python 3.13+
- GigaChat токен
- Telegram Bot Token

### **Установка**
```bash
git clone https://github.com/xxxRomb1kxxx/simulator_for_doctors.git
cd simulator_for_doctors

python -m venv venv
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

cp .env.example .env
# GIGA_CREDENTIALS=... BOT_TOKEN=...

python main.py  # 🚀
🧪 Тестирование
bash
pip install -r requirements-test.txt
pytest --cov=. --cov-report=html --cov-report=term-missing
68+ тестов • Покрытие >65%

test/
├── conftest.py           # Фикстуры
├── test_diagnosis_checker.py  # Диагнозы (27 тестов)
├── test_patient.py      # Модель Patient
├── test_patient_factory.py  # 5 болезней
└── test_dialog_handlers.py  # FSM
🔄 CI/CD Workflow
Workflow	Триггер	Действия
Tests	push/PR	Python 3.10-3.13
Coverage	push/PR	Codecov
Lint	push/PR	Black, flake8, bandit
Deps	Еженедельно	Safety check
Deploy	push main	VPS
📁 Структура проекта
text
simulator_for_doctors/
├── .github/workflows/    # CI/CD
├── config/              # Pydantic
├── controllers/         # Telegram handlers
│   ├── handlers/
│   ├── keyboards/
│   └── states/
├── dialog_engine/       # GigaChat
├── models/             # Patient, Disease
├── services/           # Бизнес-логика
├── test/               # 68+ тестов
└── main.py             # 🚀

```
<div align="center"> <b>Сделано с ❤️ для обучения врачей</b><br> <sub>xxxRomb1kxxx/simulator_for_doctors</sub> </div> 

**Coverage:** ![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/xxxRomb1kxxx/coverage.json)


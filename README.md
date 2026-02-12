# 🏥 tg_bot_patient @bfu_patient_bot

**Интеллектуальный Telegram-бот для диалога с пациентом**

💡 Проект предназначен для ведения диалога с пациентом, первичной диагностики и формирования медицинской карты с использованием **GigaChat** и **FSM-архитектуры**.

---
## 📋 Описание компонентов

### **`bot/controllers/`** — Модуль приложения
| Папка/Файл | Назначение |
|------------|------------|
| `handlers/` | Обработчики команд и сообщений Telegram |
| `keyboards/` | Клавиатуры и кнопки интерфейса |
| `states/` | Конечные автоматы (FSM) для диалогов |

### **`bot/models/`** — Модели данных
| Папка/Файл | Назначение |
|------------|------------|
| `entities/` | Сущности предметной области |
| `intents/` | Классификация намерений пользователя |

### **`bot/services/`** — Сервисный слой
| Файл | Назначение |
|------|------------|
| `patient_factory.py` | Фабрика для создания объектов пациентов |
| `dialog_engine.py` | Движок диалога с интеграцией GigaChat |
| `diagnosis_checker.py` | Логика проверки диагнозов |

### Корневые файлы
| Файл | Назначение |
|------|------------|
| `config.py` | Конфигурация, ключи API, настройки |
| `main.py` | Точка входа, запуск бота |

---
[![Tests](https://github.com/xxxRomb1kxxx/simulator_for_doctors/actions/workflows/test.yml/badge.svg)](https://github.com/xxxRomb1kxxx/simulator_for_doctors/actions/workflows/test.yml)
[![Coverage](https://codecov.io/gh/xxxRomb1kxxx/simulator_for_doctors/branch/main/graph/badge.svg)](https://codecov.io/gh/xxxRomb1kxxx/simulator_for_doctors)
[![Lint](https://github.com/xxxRomb1kxxx/simulator_for_doctors/actions/workflows/lint.yml/badge.svg)](https://github.com/xxxRomb1kxxx/simulator_for_doctors/actions/workflows/lint.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Coverage:** ![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/xxxRomb1kxxx/coverage.json)


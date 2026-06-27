# Опрос «Цифровой этикет в мессенджерах»

Streamlit-приложение с опросом из 9 вопросов о привычках общения в мессенджерах. Ответы сохраняются в Firebase Firestore, есть встроенный дашборд аналитики.

## Метрики опроса

Ответы — скорость и привычки отвечать на сообщения (вопросы 1–3)
Голосовые — отношение к голосовым сообщениям (вопросы 4–6)
Рабочее время — границы переписки вне рабочего времени (вопросы 7–9)

## Установка

pip install -r requirements.txt


## Настройка Firebase

Ключ доступа к Firebase хранится через [`st.secrets`](https://docs.streamlit.io/develop/concepts/connections/secrets-management), а не в файле в репозитории — это безопасно для продакшена (Streamlit Cloud, контейнеры и т.д.).

1. В консоли Firebase создайте проект и сервис-аккаунт (Project Settings → Service accounts → Generate new private key) — скачается JSON-файл.
2. **Локально**: скопируйте `.streamlit/secrets.toml.example` в `.streamlit/secrets.toml` и заполните секцию `[firebase]` значениями из скачанного JSON. Файл `secrets.toml` уже в `.gitignore` — не коммитьте его.
3. **На Streamlit Cloud (продакшен)**: откройте App settings → Secrets и вставьте туда то же содержимое секции `[firebase]`.

## Запуск

streamlit run app.py

Приложение откроется на http://localhost:8501. Заполните форму и нажмите «Отправить» — ответ сохранится в коллекцию `responses` в Firestore. Чекбокс «Показать аналитику» открывает дашборд с метриками и графиками на основе всех собранных ответов.

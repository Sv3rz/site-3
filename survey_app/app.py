from datetime import datetime

import firebase_admin
import pandas as pd
import plotly.express as px
import streamlit as st
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    if "firebase" not in st.secrets:
        st.error(
            "Не настроены секреты Firebase. Добавьте секцию [firebase] с содержимым "
            "service account JSON в .streamlit/secrets.toml (локально) или в "
            "Settings → Secrets (на Streamlit Cloud)."
        )
        st.stop()
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.set_page_config(page_title="Цифровой этикет в мессенджерах", layout="wide")
st.title("Цифровой этикет в мессенджерах")
st.markdown(
    "Пройдите короткий опрос о привычках общения в мессенджерах. "
)

REPLY_SPEED_OPTIONS = ["Мгновенно", "В течение часа", "В течение дня", "Когда вспомню"]
VOICE_FREQ_OPTIONS = ["Никогда", "Редко", "Часто", "Почти всегда вместо текста"]
WORK_HOURS_OPTIONS = ["Да, без ограничений", "Только срочное", "Недопустимо"]

with st.form("survey"):
    st.subheader("О вас (необязательно)")
    col_name, col_age = st.columns(2)
    with col_name:
        q_name = st.text_input("Имя")
    with col_age:
        q_age = st.selectbox("Возраст", ["", "До 18", "18–24", "25–34", "35–44", "45+"])

    q_reply_speed = st.radio(
        "1. Как быстро вы обычно отвечаете на личные сообщения?", REPLY_SPEED_OPTIONS
    )
    q_reply_norm = st.slider(
        "2. Насколько нормальным вы считаете не отвечать сразу "
        "(1 — недопустимо, 10 — абсолютно нормально)",
        1, 10, 5,
    )
    q_reply_feel = st.multiselect(
        "3. Что вы чувствуете, если вам долго не отвечают?",
        ["Раздражение", "Тревогу", "Безразличие", "Понимание"],
    )

    q_voice_freq = st.radio(
        "4. Как часто вы отправляете голосовые сообщения?", VOICE_FREQ_OPTIONS
    )
    q_voice_comfort = st.slider(
        "5. Насколько комфортно получать голосовое без предупреждения "
        "(1 — неприятно, 10 — комфортно)",
        1, 10, 5,
    )
    q_voice_context = st.multiselect(
        "6. В каких чатах голосовые уместны?",
        ["Личное общение", "Рабочие чаты", "Учебные группы", "Никогда"],
    )

    q_work_hours = st.radio(
        "7. Допустимо ли писать по работе/учёбе вне рабочего времени?",
        WORK_HOURS_OPTIONS,
    )
    q_quiet_hours = st.slider(
        "8. В какие часы вы не хотите получать сообщения по работе/учёбе?",
        0, 23, (22, 8),
    )
    q_notifications = st.radio(
        "9. Отключаете ли уведомления в нерабочее время?",
        ["Да, всегда", "Иногда", "Нет"],
    )

    submit = st.form_submit_button("Отправить")

if submit:
    record = {
        "name": q_name,
        "age": q_age,
        "reply_speed": q_reply_speed,
        "reply_norm": int(q_reply_norm),
        "reply_feel": q_reply_feel,
        "voice_freq": q_voice_freq,
        "voice_comfort": int(q_voice_comfort),
        "voice_context": q_voice_context,
        "work_hours": q_work_hours,
        "quiet_hours_start": int(q_quiet_hours[0]),
        "quiet_hours_end": int(q_quiet_hours[1]),
        "notifications": q_notifications,
        "time": datetime.utcnow(),
    }
    try:
        db.collection("responses").add(record)
        st.success("Спасибо! Ваш ответ сохранён.")
    except Exception as e:
        st.error(f"Ошибка сохранения: {e}")

st.divider()
if st.checkbox("Показать аналитику"):
    docs = db.collection("responses").stream()
    data = [doc.to_dict() for doc in docs]

    if data:
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"])

        total = len(df)
        fast_replies = df["reply_speed"].isin(["Мгновенно", "В течение часа"]).mean() * 100
        frequent_voice = df["voice_freq"].isin(["Часто", "Почти всегда вместо текста"]).mean() * 100
        no_work_hours = (df["work_hours"] == "Недопустимо").mean() * 100

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Всего ответов", total)
        col2.metric("Отвечают быстро", f"{fast_replies:.0f}%")
        col3.metric("Часто шлют голосовые", f"{frequent_voice:.0f}%")
        col4.metric("Против сообщений вне работы", f"{no_work_hours:.0f}%")

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.plotly_chart(
                px.histogram(
                    df, x="reply_speed", category_orders={"reply_speed": REPLY_SPEED_OPTIONS},
                    title="Скорость ответа",
                ),
                use_container_width=True,
            )
        with chart_col2:
            st.plotly_chart(
                px.pie(df, names="voice_freq", title="Частота голосовых сообщений"),
                use_container_width=True,
            )

        work_hours_counts = df["work_hours"].value_counts().reindex(WORK_HOURS_OPTIONS).fillna(0)
        work_hours_df = pd.DataFrame(
            {"work_hours": work_hours_counts.index, "count": work_hours_counts.values}
        )
        st.plotly_chart(
            px.bar(
                work_hours_df,
                x="work_hours", y="count",
                title="Допустимость сообщений вне рабочего времени",
            ),
            use_container_width=True,
        )

        with st.expander("Ответы пользователей"):
            st.dataframe(df)
    else:
        st.info("Пока нет данных для отображения.")

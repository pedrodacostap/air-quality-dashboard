import streamlit as st
import asyncio
import calendar
from baixar_relatorio import main

st.set_page_config(
    page_title="Air Quality Dashboard",
    page_icon="🌍",
    layout="centered"
)

st.title("🌍 Air Quality Report Generator")

st.write("Gerar relatório automático da plataforma Aurassure")

mes = st.selectbox(
    "Selecione o mês",
    list(range(1,13))
)

ano = st.number_input(
    "Selecione o ano",
    min_value=2020,
    max_value=2100,
    value=2024
)

if st.button("Gerar relatório"):

    st.info("Executando automação...")

    try:
        asyncio.run(main())

        st.success("Relatório gerado com sucesso!")

    except Exception as e:
        st.error(f"Erro: {e}")
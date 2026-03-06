# --------------------------Imports ---------------------------------------

import os
import asyncio
import calendar
from playwright.async_api import async_playwright

# -------------------------CONFIGURAÇÕES---------------------------------------

USER_EMAIL = "theomar.neves@ufopa.edu.br"
PASSWORD = "Qu@l!ty100"
LOGIN_URL = "https://app.aurassure.com/enterprise/17429/reports/custom-reports"

HEADLESS = True

PASTA_DESTINO = os.path.join(os.getcwd(), "Aurassura_air_quality_reports")

MESES_NOMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}

MESES_NOME_COMPLETO = {
    "Jan": "january", "Feb": "february", "Mar": "march", "Apr": "april",
    "May": "may", "Jun": "june", "Jul": "july", "Aug": "august",
    "Sep": "september", "Oct": "october", "Nov": "november", "Dec": "december"
}

# =================================================

def obter_datas_relatorio():
    while True:
        try:
            entrada = input("\nDigite o mês e ano (ex: 3 2024): ").split()
            mes = int(entrada[0])
            ano = int(entrada[1])

            ultimo_dia = calendar.monthrange(ano, mes)[1]
            mes_abr = MESES_NOMES[mes]

            data_inicio = f"01 {mes_abr} {ano}, 00:00"
            data_fim = f"{ultimo_dia:02d} {mes_abr} {ano}, 23:59"

            print(f"\n✅ Período selecionado: {data_inicio} até {data_fim}")
            return data_inicio, data_fim

        except:
            print("❌ Entrada inválida.")

# =================================================

async def login(page):

    print("🔐 Fazendo login...")
    await page.goto(LOGIN_URL)

    await page.wait_for_selector('#email', timeout=60000)

    try:
        await page.click('#acceptCookie')
    except:
        pass

    await page.fill('#email', USER_EMAIL)
    await page.click('#next_btn')

    await page.wait_for_selector('#password')

    await page.fill('#password', PASSWORD)
    await page.click('#form_submit_btn')

    await page.wait_for_load_state("networkidle")

    print("✅ Login realizado!")

# =================================================

async def configurar_datas(page, data_inicio, data_fim):

    print("📅 Configurando datas...")

    await page.get_by_text('Last 7 days').click()
    await page.get_by_text('Custom', exact=True).click()

    await page.fill('#custom_range', data_inicio)

    await page.get_by_role("button", name="Ok").click()

    xpath_data_fim = '//*[@id="container"]/form/div[10]/div/div[2]/div/div/div[2]/div/div/div/div/div/div[3]/input'

    await page.fill(xpath_data_fim, data_fim)

    await page.get_by_role("button", name="Ok").click()

# =================================================

async def baixar_relatorio(page, data_inicio):

    print("📊 Gerando relatório...")

    await page.get_by_role("button", name="Generate Report").click()

    await page.wait_for_selector('#view_report_page', timeout=300000)

    await page.click('//*[@id="view_report_page"]/div[1]/div[2]/span[1]')

    print("⏳ Aguardando botão de download...")

    await page.wait_for_selector('button:has-text("Download")', timeout=300000)

    print("⬇️ Baixando arquivo...")

    async with page.expect_download(timeout=300000) as download_info:

        await page.click('button:has-text("Download")')

    download = await download_info.value

    partes = data_inicio.split()
    mes_abr = partes[1]
    ano_str = partes[2].replace(',', '')

    mes_nome_completo = MESES_NOME_COMPLETO.get(mes_abr, "unknown")

    nome_arquivo = f"{mes_nome_completo}_{ano_str}_air_quality.xlsx"

    caminho_final = os.path.join(PASTA_DESTINO, nome_arquivo)

    await download.save_as(caminho_final)

    print("\n✅ SUCESSO!")
    print(f"📁 Arquivo salvo em: {caminho_final}")

# =================================================

async def main():

    if not os.path.exists(PASTA_DESTINO):
        os.makedirs(PASTA_DESTINO)

    data_inicio, data_fim = obter_datas_relatorio()

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=HEADLESS, slow_mo=100)

        context = await browser.new_context(accept_downloads=True)

        page = await context.new_page()

        try:

            await login(page)

            await configurar_datas(page, data_inicio, data_fim)

            await baixar_relatorio(page, data_inicio)

        except Exception as e:

            print(f"❌ Erro durante execução: {e}")

            await page.screenshot(path="erro_debug.png")

            print("📸 Screenshot salva como erro_debug.png")

        finally:

            await browser.close()

            print("🔒 Navegador fechado.")

# =================================================

if __name__ == "__main__":
    asyncio.run(main())
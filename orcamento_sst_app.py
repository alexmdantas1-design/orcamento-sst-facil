# Requisitos: pip install streamlit fpdf pandas openpyxl

import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd

# Carregar planilhas
precos_df = pd.read_excel("Planilha de preços.xlsx", sheet_name="Preço por serviço")
alinhamento_df = pd.read_excel("Planilha de preços.xlsx", sheet_name="Alinhamento")

# Função para determinar faixa por número de trabalhadores
def obter_faixa(trabalhadores):
    if trabalhadores <= 5:
        return "ATÉ 5"
    elif trabalhadores <= 19:
        return "DE 6 A 19"
    elif trabalhadores <= 34:
        return "DE 20 A 34"
    elif trabalhadores <= 49:
        return "DE 35 A 49"
    elif trabalhadores <= 74:
        return "DE 50 A 74"
    elif trabalhadores <= 99:
        return "DE 75 A 99"
    else:
        return "ACIMA DE 100"

# Função para pegar preços por faixa
def pegar_preco(servico, faixa):
    linha = precos_df[(precos_df["Serviço"] == servico) & (precos_df["Faixa"] == faixa)]
    return float(linha["Valor"].values[0]) if not linha.empty else 0.0

# Função para pegar valor de alinhamento por cidade
def pegar_valor_alinhamento(cidade):
    linha = alinhamento_df[alinhamento_df["Cidade"].str.lower() == cidade.lower()]
    return float(linha["Valor"].values[0]) if not linha.empty else 0.0

# Função para gerar PDF
def gerar_pdf(dados, valores, desconto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "SST FÁCIL - PROPOSTA DE ORÇAMENTO", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Data de emissão: {datetime.today().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Dados do Cliente:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Razão Social: {dados['razao']}", ln=True)
    pdf.cell(0, 8, f"CNPJ: {dados['cnpj']}", ln=True)
    pdf.cell(0, 8, f"Cidade: {dados['cidade']}", ln=True)
    pdf.cell(0, 8, f"Nº de trabalhadores: {dados['funcionarios']}", ln=True)
    pdf.cell(0, 8, f"Porte da empresa: {dados['porte']}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Serviços Contratados:", ln=True)
    pdf.set_font("Arial", "", 11)
    total = 0
    for nome, valor in valores.items():
        pdf.multi_cell(0, 8, f"- {nome}\n  Valor: R$ {valor:.2f}".replace(".", ","))
        pdf.ln(1)
        total += valor

    valor_final = total * (1 - desconto)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"DESCONTO: - R$ {(total * desconto):.2f}".replace(".", ","), ln=True)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"TOTAL: R$ {valor_final:.2f}".replace(".", ","), ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, "Este orçamento inclui os principais programas obrigatórios para garantir a segurança e a saúde ocupacional da sua empresa.\n\nConte com a SST FÁCIL para um atendimento técnico, humanizado e eficiente.")
    pdf.set_font("Arial", "I", 11)
    pdf.ln(5)
    pdf.cell(0, 8, "Agradecemos pela confiança. Este orçamento é válido por 15 dias a partir da data de emissão.", ln=True)

    nome_arquivo = f"orcamento_{dados['cnpj'].replace('/', '').replace('.', '').replace('-', '')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# Interface
st.set_page_config(page_title="Orçamento SST Fácil", layout="centered")
st.title("📄 Gerador de Orçamento - SST FÁCIL")

with st.form("formulario"):
    st.subheader("Dados da empresa")
    cnpj = st.text_input("CNPJ")
    razao = st.text_input("Razão Social")
    cidade = st.text_input("Cidade")
    funcionarios = st.number_input("Nº de funcionários", min_value=1, step=1)
    porte = st.selectbox("Porte", ["MEI", "ME", "EPP", "Outros"])
    incluir_esocial = st.checkbox("Incluir ESOCIAL?")

    enviado = st.form_submit_button("Gerar Orçamento")

if enviado:
    faixa = obter_faixa(funcionarios)
    desconto = 0.5 if porte in ["MEI", "ME", "EPP"] else 0.0
    valores = {
        "PGR - Programa de Gerenciamento de Riscos": pegar_preco("PGR", faixa),
        "PCMSO - Controle Médico de Saúde Ocupacional": pegar_preco("PCMSO", faixa),
        "ALINHAMENTO - Relatório de Primeira Etapa": pegar_valor_alinhamento(cidade),
        "Visita Técnica": 0 if cidade.lower() == "parelhas" else (pegar_preco("Visita", faixa))
    }
    if incluir_esocial:
        valores["ESOCIAL - Transmissões e Atualizações"] = pegar_preco("ESOCIAL", faixa)

    dados = {
        "cnpj": cnpj,
        "razao": razao,
        "cidade": cidade,
        "funcionarios": funcionarios,
        "porte": porte
    }

    nome_pdf = gerar_pdf(dados, valores, desconto)
    with open(nome_pdf, "rb") as file:
        st.download_button(label="📥 Baixar PDF do Orçamento", data=file, file_name=nome_pdf, mime="application/pdf")

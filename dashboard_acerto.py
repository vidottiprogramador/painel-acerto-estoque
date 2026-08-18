import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# PAINEL GERENCIAL DE ACERTO DE ESTOQUE
# ============================================================

PASTA = Path(__file__).parent
ARQUIVO = PASTA / "resultados" / "Painel_Acerto_Entrada_x_Saida.xlsx"
PASTA_RESULTADOS = PASTA / "resultados"
PASTA_GRAFICOS = PASTA_RESULTADOS / "graficos"

PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)

ARQUIVO_FINAL = PASTA_RESULTADOS / "PAINEL_GERENCIAL_ACERTO_ESTOQUE.xlsx"


print("=" * 70)
print("PAINEL GERENCIAL DE ACERTO DE ESTOQUE")
print("=" * 70)


# ============================================================
# LEITURA
# ============================================================
st.write("TESTE 1 - Iniciando leitura da Entrada")
entrada = pd.read_excel(
    ARQUIVO,
    sheet_name="Detalhe Entrada"
)
st.write("TESTE 2 - Entrada carregada com sucesso")
saida = pd.read_excel(
    st.write("TESTE 3 - Iniciando leitura da Saída")
    ARQUIVO,
    sheet_name="Detalhe Saida"
)
st.write("TESTE 4 - Saída carregada com sucesso")

# ============================================================
# LIMPEZA
# ============================================================

def preparar(df):

    df = df.dropna(axis=1, how="all")

    df.columns = [
        str(c).strip()
        for c in df.columns
    ]

    if "SKU" in df.columns:

        df["SKU"] = (
            df["SKU"]
            .astype(str)
            .str.strip()
            .str.replace(".0", "", regex=False)
        )

    if "Quantidade" in df.columns:

        df["Quantidade"] = pd.to_numeric(
            df["Quantidade"],
            errors="coerce"
        ).fillna(0)

    if "Valor" in df.columns:

        df["Valor"] = pd.to_numeric(
            df["Valor"],
            errors="coerce"
        ).fillna(0)

    return df


entrada = preparar(entrada)
saida = preparar(saida)


# ============================================================
# TOTAIS
# ============================================================

total_entrada = entrada["Quantidade"].sum()
total_saida = saida["Quantidade"].sum()

saldo = total_entrada - total_saida

skus_entrada = entrada["SKU"].nunique()
skus_saida = saida["SKU"].nunique()


# ============================================================
# CONSOLIDAÇÃO POR SKU
# ============================================================

entrada_sku = (
    entrada
    .groupby("SKU", as_index=False)
    .agg(
        Entrada=("Quantidade", "sum")
    )
)


saida_sku = (
    saida
    .groupby("SKU", as_index=False)
    .agg(
        Saida=("Quantidade", "sum")
    )
)


comparativo = pd.merge(
    entrada_sku,
    saida_sku,
    on="SKU",
    how="outer"
)


comparativo["Entrada"] = (
    comparativo["Entrada"]
    .fillna(0)
)

comparativo["Saida"] = (
    comparativo["Saida"]
    .fillna(0)
)


comparativo["Saldo"] = (
    comparativo["Entrada"]
    -
    comparativo["Saida"]
)


# ============================================================
# DESCRIÇÃO
# ============================================================

if "Descricao" in entrada.columns:

    descricao = (
        entrada[
            ["SKU", "Descricao"]
        ]
        .drop_duplicates("SKU")
    )

    comparativo = pd.merge(
        comparativo,
        descricao,
        on="SKU",
        how="left"
    )

else:

    comparativo["Descricao"] = ""


comparativo["Descricao"] = (
    comparativo["Descricao"]
    .fillna("")
)


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classificar(row):

    if row["Entrada"] > 0 and row["Saida"] > 0:

        return "Entrada + Saída"

    if row["Entrada"] > 0 and row["Saida"] == 0:

        return "Somente Entrada"

    if row["Entrada"] == 0 and row["Saida"] > 0:

        return "Somente Saída"

    return "Sem Movimento"


comparativo["Classificacao"] = (
    comparativo.apply(
        classificar,
        axis=1
    )
)


# ============================================================
# INDICADORES
# ============================================================

skus_analisados = len(comparativo)

skus_ambos = len(
    comparativo[
        comparativo["Classificacao"]
        == "Entrada + Saída"
    ]
)

skus_somente_entrada = len(
    comparativo[
        comparativo["Classificacao"]
        == "Somente Entrada"
    ]
)

skus_somente_saida = len(
    comparativo[
        comparativo["Classificacao"]
        == "Somente Saída"
    ]
)


# ============================================================
# TOP 10
# ============================================================

top_entrada = (
    comparativo
    .sort_values(
        "Entrada",
        ascending=False
    )
    .head(10)
    [
        [
            "SKU",
            "Descricao",
            "Entrada"
        ]
    ]
)


top_saida = (
    comparativo
    .sort_values(
        "Saida",
        ascending=False
    )
    .head(10)
    [
        [
            "SKU",
            "Descricao",
            "Saida"
        ]
    ]
)


# ============================================================
# RESUMO
# ============================================================

resumo = pd.DataFrame({

    "Indicador": [

        "Registros de Entrada",
        "Registros de Saída",
        "SKUs Analisados",
        "SKUs com Entrada",
        "SKUs com Saída",
        "SKUs Entrada + Saída",
        "SKUs Somente Entrada",
        "SKUs Somente Saída",
        "Quantidade Entrada",
        "Quantidade Saída",
        "Saldo Entrada - Saída"

    ],

    "Resultado": [

        len(entrada),
        len(saida),
        skus_analisados,
        skus_entrada,
        skus_saida,
        skus_ambos,
        skus_somente_entrada,
        skus_somente_saida,
        total_entrada,
        total_saida,
        saldo

    ]

})


# ============================================================
# GRÁFICO ENTRADA X SAÍDA
# ============================================================

plt.figure(figsize=(9, 5))

plt.bar(
    ["Entrada", "Saída"],
    [total_entrada, total_saida]
)

plt.title(
    "Quantidade - Entrada x Saída"
)

plt.ylabel("Quantidade")

plt.tight_layout()

grafico1 = (
    PASTA_GRAFICOS
    / "01_Entrada_x_Saida.png"
)

plt.savefig(
    grafico1,
    dpi=150
)

plt.close()


# ============================================================
# GRÁFICO CLASSIFICAÇÃO
# ============================================================

plt.figure(figsize=(9, 5))

plt.bar(

    [
        "Entrada + Saída",
        "Somente Entrada",
        "Somente Saída"
    ],

    [
        skus_ambos,
        skus_somente_entrada,
        skus_somente_saida
    ]

)

plt.title(
    "Classificação dos SKUs"
)

plt.ylabel("Quantidade de SKUs")

plt.xticks(rotation=15)

plt.tight_layout()

grafico2 = (
    PASTA_GRAFICOS
    / "02_Classificacao_SKUs.png"
)

plt.savefig(
    grafico2,
    dpi=150
)

plt.close()


# ============================================================
# GRÁFICO TOP ENTRADA
# ============================================================

dados = top_entrada.sort_values(
    "Entrada"
)

plt.figure(figsize=(10, 6))

plt.barh(
    dados["SKU"].astype(str),
    dados["Entrada"]
)

plt.title(
    "Top 10 SKUs - Maior Entrada"
)

plt.xlabel("Quantidade")

plt.tight_layout()

grafico3 = (
    PASTA_GRAFICOS
    / "03_Top_Entrada.png"
)

plt.savefig(
    grafico3,
    dpi=150
)

plt.close()


# ============================================================
# GRÁFICO TOP SAÍDA
# ============================================================

dados = top_saida.sort_values(
    "Saida"
)

plt.figure(figsize=(10, 6))

plt.barh(
    dados["SKU"].astype(str),
    dados["Saida"]
)

plt.title(
    "Top 10 SKUs - Maior Saída"
)

plt.xlabel("Quantidade")

plt.tight_layout()

grafico4 = (
    PASTA_GRAFICOS
    / "04_Top_Saida.png"
)

plt.savefig(
    grafico4,
    dpi=150
)

plt.close()


# ============================================================
# CRIAR EXCEL
# ============================================================

print()
print("CRIANDO PAINEL GERENCIAL...")

with pd.ExcelWriter(
    ARQUIVO_FINAL,
    engine="xlsxwriter"
) as writer:

    # --------------------------------------------------------
    # ABA PAINEL
    # --------------------------------------------------------

    workbook = writer.book

    painel = workbook.add_worksheet(
        "PAINEL"
    )

    writer.sheets["PAINEL"] = painel


    # --------------------------------------------------------
    # FORMATOS
    # --------------------------------------------------------

    titulo = workbook.add_format({

        "bold": True,
        "font_size": 20,
        "align": "center",
        "valign": "vcenter"

    })


    indicador = workbook.add_format({

        "bold": True,
        "font_size": 12,
        "align": "center",
        "valign": "vcenter"

    })


    valor = workbook.add_format({

        "bold": True,
        "font_size": 18,
        "align": "center",
        "valign": "vcenter",
        "num_format": "#,##0"

    })


    valor_decimal = workbook.add_format({

        "bold": True,
        "font_size": 18,
        "align": "center",
        "valign": "vcenter",
        "num_format": "#,##0.00"

    })


    normal = workbook.add_format({

        "font_size": 11

    })


    # --------------------------------------------------------
    # CONFIGURAÇÃO DA PLANILHA
    # --------------------------------------------------------

    painel.set_column(
        "A:A",
        20
    )

    painel.set_column(
        "B:B",
        20
    )

    painel.set_column(
        "C:C",
        20
    )

    painel.set_column(
        "D:D",
        20
    )

    painel.set_column(
        "E:E",
        20
    )

    painel.set_column(
        "F:F",
        20
    )

    painel.set_row(
        0,
        35
    )


    # --------------------------------------------------------
    # TÍTULO
    # --------------------------------------------------------

    painel.merge_range(
        "A1:F2",
        "PAINEL DE ACERTO DE ESTOQUE",
        titulo
    )


    # --------------------------------------------------------
    # INDICADORES
    # --------------------------------------------------------

    painel.write(
        "A4",
        "ENTRADA",
        indicador
    )

    painel.write(
        "A5",
        total_entrada,
        valor
    )


    painel.write(
        "B4",
        "SAÍDA",
        indicador
    )

    painel.write(
        "B5",
        total_saida,
        valor
    )


    painel.write(
        "C4",
        "SALDO",
        indicador
    )

    painel.write(
        "C5",
        saldo,
        valor
    )


    painel.write(
        "D4",
        "SKUs ANALISADOS",
        indicador
    )

    painel.write(
        "D5",
        skus_analisados,
        valor
    )


    painel.write(
        "E4",
        "ENTRADA + SAÍDA",
        indicador
    )

    painel.write(
        "E5",
        skus_ambos,
        valor
    )


    painel.write(
        "F4",
        "SOMENTE SAÍDA",
        indicador
    )

    painel.write(
        "F5",
        skus_somente_saida,
        valor
    )


    # --------------------------------------------------------
    # SEGUNDA LINHA DE INDICADORES
    # --------------------------------------------------------

    painel.write(
        "A7",
        "SOMENTE ENTRADA",
        indicador
    )

    painel.write(
        "A8",
        skus_somente_entrada,
        valor
    )


    painel.write(
        "B7",
        "SKUs COM ENTRADA",
        indicador
    )

    painel.write(
        "B8",
        skus_entrada,
        valor
    )


    painel.write(
        "C7",
        "SKUs COM SAÍDA",
        indicador
    )

    painel.write(
        "C8",
        skus_saida,
        valor
    )


    # --------------------------------------------------------
    # INSERIR GRÁFICOS
    # --------------------------------------------------------

    painel.insert_image(
        "A10",
        str(grafico1),
        {
            "x_scale": 0.75,
            "y_scale": 0.75
        }
    )


    painel.insert_image(
        "D10",
        str(grafico2),
        {
            "x_scale": 0.75,
            "y_scale": 0.75
        }
    )


    painel.insert_image(
        "A27",
        str(grafico3),
        {
            "x_scale": 0.70,
            "y_scale": 0.70
        }
    )


    painel.insert_image(
        "D27",
        str(grafico4),
        {
            "x_scale": 0.70,
            "y_scale": 0.70
        }
    )


    # --------------------------------------------------------
    # ABA COMPARATIVO
    # --------------------------------------------------------

    comparativo.to_excel(
        writer,
        sheet_name="Comparativo SKU",
        index=False
    )


    ws = writer.sheets[
        "Comparativo SKU"
    ]

    ws.freeze_panes(
        1,
        0
    )

    ws.autofilter(
        0,
        0,
        len(comparativo),
        len(comparativo.columns) - 1
    )

    ws.set_column(
        "A:A",
        15
    )

    ws.set_column(
        "B:B",
        55
    )

    ws.set_column(
        "C:E",
        18
    )

    ws.set_column(
        "F:F",
        22
    )


    # --------------------------------------------------------
    # ABA RESUMO
    # --------------------------------------------------------

    resumo.to_excel(
        writer,
        sheet_name="Resumo",
        index=False
    )


    # --------------------------------------------------------
    # ABA TOP ENTRADA
    # --------------------------------------------------------

    top_entrada.to_excel(
        writer,
        sheet_name="Top Entrada",
        index=False
    )


    # --------------------------------------------------------
    # ABA TOP SAÍDA
    # --------------------------------------------------------

    top_saida.to_excel(
        writer,
        sheet_name="Top Saida",
        index=False
    )


print()
print("=" * 70)
print("PAINEL GERENCIAL CRIADO COM SUCESSO")
print("=" * 70)

print()
print("Arquivo criado:")

print(ARQUIVO_FINAL)

print()
print("Gráficos:")

print(PASTA_GRAFICOS)

print()
print("=" * 70)
print("FIM")
print("=" * 70)

input("\nPressione ENTER para sair...")
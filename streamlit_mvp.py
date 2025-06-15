import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 

st.set_page_config(page_title="Análise de Doenças 2025", layout="wide")

def ler_arquivo(nome_arquivo):
    df = pd.read_csv(nome_arquivo, sep=';', header=None, names=["Doença", "Masculino", "Feminino", "Total"])
    df["Doença"] = df["Doença"].str.strip()
    return df

def grafico_individual(df, mes):
    df['Total Calculado'] = df['Masculino'] + df['Feminino']
    df_melted = df.melt(
        id_vars='Doença',
        value_vars=['Masculino', 'Feminino', 'Total Calculado'],
        var_name='Sexo',
        value_name='Número de Casos'
    )
    cores = {"Masculino": "#189AB4", "Feminino": "#FD49A0", "Total Calculado": "#FAD02C"}
    fig = px.bar(
        df_melted,
        x='Doença',
        y='Número de Casos',
        color='Sexo',
        barmode='group',
        title=f"📊 Casos por Sexo - {mes}",
        color_discrete_map=cores
    )
    fig.update_layout(xaxis_tickangle=-45, margin=dict(t=60, l=20, r=20, b=60))
    return fig

def gerar_analise(df):
    top_doencas = df.sort_values("Total", ascending=False).head(3)["Doença"].tolist()
    diferenca_sexos = abs(df["Masculino"].sum() - df["Feminino"].sum())
    sexo_mais_afetado = "Masculino" if df["Masculino"].sum() > df["Feminino"].sum() else "Feminino"
    return (
        f"- As 3 doenças com maior número de casos são: **{', '.join(top_doencas)}**.\n"
        f"- O sexo mais afetado foi: **{sexo_mais_afetado}**, com uma diferença de {diferenca_sexos} casos."
    )

st.title("📈 Análise de Doenças por Mês - 2025")

meses = {
    "Janeiro": "dados_doencas_jan.txt",
    "Fevereiro": "dados_doencas_fev.txt",
    "Março": "dados_doencas_mar.txt"
}

df_geral = pd.DataFrame()

for mes, arquivo in meses.items():
    try:
        df_mes = ler_arquivo(arquivo)
        df_geral = pd.concat([df_geral, df_mes.assign(Mês=mes)], ignore_index=True)
        
        st.subheader(f"{mes}")
        st.plotly_chart(grafico_individual(df_mes, mes), use_container_width=True)
        st.markdown(gerar_analise(df_mes))
        st.markdown("---")
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar '{arquivo}': {e}")

if not df_geral.empty:
    df_totais = df_geral.groupby("Doença")[["Masculino", "Feminino", "Total"]].sum().reset_index()
    top5 = df_totais.sort_values("Total", ascending=False).head(5)

    fig_top5 = px.bar(
        top5,
        x="Doença",
        y="Total",
        title="🔥 Top 5 Doenças Mais Frequentes no Trimestre",
        text="Total",
        color="Doença"
    )
    fig_top5.update_traces(textposition='outside')
    fig_top5.update_layout(showlegend=False, xaxis_tickangle=-45)

    st.header("📊 Consolidado: Top 5 Doenças Mais Frequentes")
    st.plotly_chart(fig_top5, use_container_width=True)

try:
    st.header("💸 Custo Médio por Doença - Jan a Mar 2025")

    arquivos_custo = {
        "Janeiro": "custo_medio_int_jan.txt",
        "Fevereiro": "custo_medio_int_fev.txt",
        "Março": "custo_medio_int_mar.txt"
    }

    dfs_custo = []
    for mes, arquivo in arquivos_custo.items():
        df_temp = pd.read_csv(arquivo, sep=";", header=None, names=["Doença", "Custo Médio"])
        df_temp["Doença"] = df_temp["Doença"].str.strip()
        df_temp["Custo Médio"] = pd.to_numeric(df_temp["Custo Médio"].astype(str).str.replace(",", "."), errors="coerce")
        df_temp = df_temp.dropna(subset=["Custo Médio"])
        df_temp = df_temp.rename(columns={"Custo Médio": mes})
        dfs_custo.append(df_temp)

    
    df_custo_total = dfs_custo[0]
    for df_c in dfs_custo[1:]:
        df_custo_total = pd.merge(df_custo_total, df_c, on="Doença", how="inner")

    fig_custo = go.Figure()

    cores = {"Janeiro": "#4c72b0", "Fevereiro": "#55a868", "Março": "#c44e52"}

    for mes in arquivos_custo.keys():
        fig_custo.add_trace(go.Bar(
            x=df_custo_total["Doença"],
            y=df_custo_total[mes],
            name=mes,
            marker_color=cores[mes]
        ))

    fig_custo.update_layout(
        barmode='group',
        title="💰 Comparativo de Custo Médio por Doença - Jan a Mar 2025",
        xaxis_title="Doença",
        yaxis_title="Custo Médio (R$)",
        xaxis_tickangle=-45,
        legend_title="Mês",
        margin=dict(t=60, b=100),
        height=500
    )
    st.plotly_chart(fig_custo, use_container_width=True)

    st.markdown("- As doenças com **maior custo médio** representam impacto financeiro mais relevante para o sistema de saúde.")
except Exception as e:
    st.warning(f"⚠️ Não foi possível carregar o gráfico de custo médio: {e}")

try:
    df_poluicao = pd.read_csv('poluicao_vitoria2025.csv')

    meses_ordem = ['janeiro', 'fevereiro', 'março']
    df_poluicao['Mes_num'] = df_poluicao['Mes'].apply(lambda x: meses_ordem.index(x) + 1)

    df_poluicao = df_poluicao.sort_values('Mes_num')

    st.header("🌬️ Análise da Qualidade do Ar em Vitória - 2025")
    st.subheader("Evolução do Ozônio ao longo dos meses")
    fig_ozonio = px.line(df_poluicao, x='Mes_num', y='Ozônio', 
                         labels={'Mes_num': 'Mês', 'Ozônio': 'Concentração (ppb)'},
                         markers=True)
    fig_ozonio.update_xaxes(tickmode='array', tickvals=list(range(1,13)), ticktext=meses_ordem)
    st.plotly_chart(fig_ozonio, use_container_width=True)

    st.subheader("Evolução dos principais poluentes")
    poluentes = ['Ozônio', 'Dióxido de Nitrogênio', 'Monóxido de Nitrogênio', 'Óxidos de Nitrogênio']
    fig_multi = px.line(df_poluicao, x='Mes_num', y=poluentes, 
                         labels={'Mes_num': 'Mês', 'value': 'Concentração (ppb)', 'variable': 'Poluente'},
                         markers=True)
    fig_multi.update_xaxes(tickmode='array', tickvals=list(range(1,13)), ticktext=meses_ordem)
    st.plotly_chart(fig_multi, use_container_width=True)

    st.subheader("Correlação entre Poluentes e Variáveis Climáticas")
    cols_analise = ['Ozônio', 'Dióxido de Nitrogênio', 'Monóxido de Nitrogênio', 'Óxidos de Nitrogênio',
                    'Dióxido de Enxofre', 'Monóxido de Carbono', 'Partículas Respiráveis', 'Partículas Inaláveis',
                    'Umidade Relativa', 'Temperatura']

    corr = df_poluicao[cols_analise].corr()

    fig_corr = px.imshow(corr, text_auto=True, title='Correlação entre Poluentes e Variáveis Climáticas')
    st.plotly_chart(fig_corr, use_container_width=True)

except FileNotFoundError:
    st.error("❌ Erro: O arquivo 'poluicao_vitoria2025.csv' não foi encontrado. Por favor, verifique o caminho do arquivo.")
except Exception as e:
    st.error(f"❌ Ocorreu um erro ao carregar ou processar os dados de poluição: {e}")
    
st.markdown("""
Esta seção explora uma possível relação entre as doenças mais prevalentes e a qualidade do ar, focando na concentração de Ozônio nos meses de Janeiro, Fevereiro e Março de 2025.
""")

try:
    df_doencas_mensal = df_geral.groupby('Mês')['Total'].sum().reset_index()
    df_doencas_mensal.rename(columns={'Total': 'Total de Casos de Doença'}, inplace=True)
    
    meses_comuns = ['Janeiro', 'Fevereiro', 'Março']
    df_doencas_mensal = df_doencas_mensal[df_doencas_mensal['Mês'].isin(meses_comuns)]

    df_ozonio_mensal = df_poluicao[df_poluicao['Mes'].isin([m.lower() for m in meses_comuns])].groupby('Mes')['Ozônio'].mean().reset_index()
    df_ozonio_mensal.rename(columns={'Mes': 'Mês_lower'}, inplace=True)
    
    mes_map = {m.lower(): m for m in meses_comuns}
    df_ozonio_mensal['Mês'] = df_ozonio_mensal['Mês_lower'].map(mes_map)
    df_ozonio_mensal = df_ozonio_mensal.drop(columns=['Mês_lower'])
    
    df_combinado = pd.merge(df_doencas_mensal, df_ozonio_mensal, on='Mês', how='inner')
    
    df_combinado['Mes_num'] = df_combinado['Mês'].apply(lambda x: meses_ordem.index(x.lower()) + 1)
    df_combinado = df_combinado.sort_values('Mes_num')

    fig_comparativo = go.Figure()

    fig_comparativo.add_trace(go.Bar(
        x=df_combinado['Mês'],
        y=df_combinado['Total de Casos de Doença'],
        name='Total de Casos de Doença',
        marker_color='#1f77b4',
        yaxis='y1'
    ))

    fig_comparativo.add_trace(go.Scatter(
        x=df_combinado['Mês'],
        y=df_combinado['Ozônio'],
        mode='lines+markers',
        name='Ozônio Médio (ppb)',
        marker_color='#d62728',
        yaxis='y2'
    ))

    fig_comparativo.update_layout(
        title='Comparativo: Total de Casos de Doença vs. Ozônio Médio (Jan-Mar)',
        xaxis_title='Mês',
        yaxis=dict(
            title=dict(text='Total de Casos de Doença', font=dict(color='#1f77b4')),
            tickfont=dict(color='#1f77b4')
        ),
        yaxis2=dict(
            title=dict(text='Ozônio Médio (ppb)', font=dict(color='#d62728')),
            tickfont=dict(color='#d62728'),
            overlaying='y',
            side='right'
        ),
    )

    st.plotly_chart(fig_comparativo, use_container_width=True)

    st.markdown("""
    Este gráfico permite observar visualmente se há alguma tendência paralela entre o número total de casos de doenças e a concentração média de Ozônio ao longo dos primeiros três meses do ano. Lembre-se que esta é uma **análise exploratória** e não estabelece uma relação causal direta.
    """)

except NameError:
    st.warning("⚠️ Não foi possível gerar o gráfico de correlação. Verifique se os dados de doenças e poluição foram carregados corretamente (provavelmente faltam os arquivos ou ocorreu um erro de carregamento inicial).")
except Exception as e:
    st.error(f"❌ Ocorreu um erro ao gerar o gráfico de correlação: {e}")

st.header("📉 Correlação: Poluentes Específicos vs. Total de Casos de Doença (Jan-Mar)")
st.markdown("""
Esta seção permite explorar a relação entre a concentração de um poluente selecionado e o total de casos de doença nos meses de Janeiro, Fevereiro e Março.
""")

try:
    if 'df_geral' not in locals() or 'df_poluicao' not in locals() or df_geral.empty or df_poluicao.empty:
        st.warning("⚠️ Os dados de doenças ou poluição não foram carregados ou estão vazios. Não é possível gerar esta seção.")
    else:
        poluentes_cols_esperados = [
            'Ozônio', 'Dióxido de Nitrogênio', 'Monóxido de Nitrogênio', 
            'Óxidos de Nitrogênio', 'Dióxido de Enxofre', 'Monóxido de Carbono', 
            'Partículas Respiráveis', 'Partículas Inaláveis'
        ]
        
        poluentes_cols_existentes_em_df = [col for col in poluentes_cols_esperados if col in df_poluicao.columns]

        if not poluentes_cols_existentes_em_df:
            st.warning("⚠️ Nenhuma coluna de poluente esperada foi encontrada no arquivo 'poluicao_vitoria2025.csv'. Por favor, verifique os nomes das colunas no seu CSV.")
        else:
            selected_poluente_corr = st.selectbox(
                "Selecione um Poluente para Análise de Correlação:",
                options=poluentes_cols_existentes_em_df,
                key='corr_poluente_selectbox' 
            )

            df_doencas_mensal_total = df_geral.groupby('Mês')['Total'].sum().reset_index()
            df_doencas_mensal_total.rename(columns={'Total': 'Total de Casos de Doença'}, inplace=True)
            
            meses_comuns_corr = ['Janeiro', 'Fevereiro', 'Março'] 
            df_doencas_mensal_total = df_doencas_mensal_total[df_doencas_mensal_total['Mês'].isin(meses_comuns_corr)]

            df_poluentes_mensal_corr = df_poluicao[
                df_poluicao['Mes'].isin([m.lower() for m in meses_comuns_corr])
            ].groupby('Mes')[poluentes_cols_existentes_em_df].mean().reset_index()

            mes_map_corr = {m.lower(): m for m in meses_comuns_corr}
            df_poluentes_mensal_corr['Mês'] = df_poluentes_mensal_corr['Mes'].map(mes_map_corr)
            df_poluentes_mensal_corr = df_poluentes_mensal_corr.drop(columns=['Mes'])

            df_final_corr = pd.merge(df_doencas_mensal_total, df_poluentes_mensal_corr, on='Mês', how='inner')

            if not df_final_corr.empty and selected_poluente_corr in df_final_corr.columns:
                
                correlation_coefficient = df_final_corr['Total de Casos de Doença'].corr(df_final_corr[selected_poluente_corr])
                
                st.info(f"O coeficiente de correlação de Pearson entre o **Total de Casos de Doença** e **{selected_poluente_corr}** é: **{correlation_coefficient:.2f}**")

                try:
                    import statsmodels.api as sm
                    
                    df_plot_data = df_final_corr[[selected_poluente_corr, 'Total de Casos de Doença']].dropna()

                    if not df_plot_data.empty:
                        X = sm.add_constant(df_plot_data[selected_poluente_corr])
                        model = sm.OLS(df_plot_data['Total de Casos de Doença'], X)
                        results = model.fit()

                        fig_reg = px.scatter(
                            df_plot_data,
                            x=selected_poluente_corr, 
                            y='Total de Casos de Doença', 
                            title=f'Dispersão: Total de Casos vs. {selected_poluente_corr} (Jan-Mar)',
                            labels={
                                selected_poluente_corr: f'Concentração de {selected_poluente_corr}',
                                'Total de Casos de Doença': 'Total de Casos de Doença'
                            },
                            trendline="ols" 
                        )
                        st.plotly_chart(fig_reg, use_container_width=True)
                        st.markdown(f"""
                        O gráfico acima ilustra a relação entre as variáveis. A linha pontilhada representa a **linha de regressão linear**, 
                        que tenta mostrar a tendência geral dos dados.
                        """)
                    else:
                        st.info("ℹ️ Não há dados válidos (sem NaNs) para plotar o gráfico de dispersão com regressão para as variáveis selecionadas.")

                except ImportError:
                    st.warning("⚠️ A biblioteca 'statsmodels' não está instalada. A linha de tendência de regressão não será exibida.")
                    fig_reg = px.scatter(
                        df_final_corr, 
                        x=selected_poluente_corr, 
                        y='Total de Casos de Doença', 
                        title=f'Dispersão: Total de Casos vs. {selected_poluente_corr} (Jan-Mar)',
                        labels={
                            selected_poluente_corr: f'Concentração de {selected_poluente_corr}',
                            'Total de Casos de Doença': 'Total de Casos de Doença'
                        }
                    )
                    st.plotly_chart(fig_reg, use_container_width=True)
                
            else:
                st.info("ℹ️ Não há dados suficientes ou a coluna do poluente selecionado não existe nos dados finais para calcular a correlação.")

except Exception as e:
    st.error(f"❌ Ocorreu um erro ao gerar o gráfico de correlação poluente vs. doença: {e}")
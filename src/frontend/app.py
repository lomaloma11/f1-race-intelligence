import streamlit as st
import requests
import os
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="F1 Race Intelligence",
    page_icon="🏎",
    layout="wide"
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:5000/api/v1")

# ==============================================================================
# ESTADO DE SESSÃO (histórico de simulações)
# ==============================================================================
if "top10_history" not in st.session_state:
    st.session_state.top10_history = []
if "cluster_history" not in st.session_state:
    st.session_state.cluster_history = []

st.title("F1 Race Intelligence")
st.markdown("Painel Analítico e Preditivo para Estratégia de Corrida na Fórmula 1")
st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Previsão Top 10",
    "Estratégia de Pneus",
    "Perfis de Pilotagem (K-Means)",
    "Comparador de Cenários",
    "Simulador de Pit Stop"
])

# ==============================================================================
# ABA 1: PREVISÃO DE TOP 10 (Classificação) — com histórico e comparação
# ==============================================================================
with tab1:
    st.subheader("Simulador Preditivo de Pontuação")
    st.write("Insira os parâmetros de corrida do piloto para calcular a probabilidade de terminar no Top 10.")

    col1, col2 = st.columns(2)

    with col1:
        grid_pos = st.slider("Posição no Grid de Largada", 1, 20, 5)
        avg_lap = st.number_input("Tempo Médio de Volta (segundos)", value=76.5, step=0.1)
        std_lap = st.number_input("Desvio Padrão / Consistência (segundos)", value=0.8, step=0.05)

    with col2:
        pos_gained = st.slider("Posições Ganhas/Perdidas", -15, 15, 0)
        is_rain = st.selectbox("Condição Climática", options=[0, 1], format_func=lambda x: "Pista Molhada 🌧️" if x == 1 else "Pista Seca ☀️")
        driver_label = st.text_input("Rótulo do Piloto/Cenário (opcional)", value="")

    run_col, clear_col = st.columns([3, 1])
    with run_col:
        run_sim = st.button("Executar Simulação Top 10", type="primary")
    with clear_col:
        if st.button("Limpar Histórico"):
            st.session_state.top10_history = []
            st.rerun()

    if run_sim:
        payload = {
            "grid_position": grid_pos,
            "avg_lap_time": avg_lap,
            "std_lap_time": std_lap,
            "positions_gained": pos_gained,
            "is_rainy": is_rain
        }

        try:
            response = requests.post(f"{API_URL}/predictions/top10", json=payload)
            if response.status_code == 200:
                result = response.json()["data"]
                prob = result["probability_percentage"]
                will_score = result["will_score_points"]

                # Guarda no histórico da sessão
                st.session_state.top10_history.append({
                    "Rótulo": driver_label if driver_label else f"Cenário {len(st.session_state.top10_history)+1}",
                    "Grid": grid_pos,
                    "Ritmo Médio (s)": avg_lap,
                    "Consistência (s)": std_lap,
                    "Pos. Ganhas": pos_gained,
                    "Chuva": "Sim" if is_rain else "Não",
                    "Probabilidade (%)": prob,
                    "Previsão": "Top 10" if will_score else "Fora dos Pontos"
                })

                st.divider()
                st.subheader("Resultado da Previsão")

                m1, m2, m3 = st.columns(3)
                m1.metric("Probabilidade de Pontuar", f"{prob}%")
                m2.metric("Previsão Final", "Vai Pontuar (Top 10)" if will_score else "Fora dos Pontos ❌")
                delta_grid = grid_pos - (grid_pos - pos_gained)
                m3.metric("Posição Final Estimada", max(1, grid_pos - pos_gained), delta=f"{pos_gained:+d} posições")

                g1, g2 = st.columns(2)

                with g1:
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=prob,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Chance de Top 10"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "#e10600"},
                            'steps': [
                                {'range': [0, 40], 'color': "#f4f4f4"},
                                {'range': [40, 70], 'color': "#e0e0e0"},
                                {'range': [70, 100], 'color': "#c4c4c4"}
                            ],
                            'threshold': {
                                'line': {'color': "black", 'width': 3},
                                'thickness': 0.8,
                                'value': 50
                            }
                        }
                    ))
                    st.plotly_chart(fig_gauge, use_container_width=True)

                with g2:
                    # Radar dos fatores de entrada normalizados (visão rápida do "perfil" do cenário)
                    categories = ['Grid (invertido)', 'Ritmo', 'Consistência', 'Ganho de Posições', 'Condição Seca']
                    values = [
                        max(0, (21 - grid_pos) / 20 * 100),
                        max(0, (80 - avg_lap) / 10 * 100),
                        max(0, (2 - std_lap) / 2 * 100),
                        max(0, min(100, (pos_gained + 15) / 30 * 100)),
                        0 if is_rain else 100
                    ]
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values + [values[0]],
                        theta=categories + [categories[0]],
                        fill='toself',
                        line_color="#e10600",
                        name="Cenário Atual"
                    ))
                    fig_radar.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        showlegend=False,
                        title="Perfil do Cenário (Normalizado)"
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)

            else:
                st.error(f"Erro na API ({response.status_code}): {response.json().get('message')}")
        except Exception as e:
            st.error(f"Não foi possível conectar à API Flask: {e}")

    # Tabela e gráfico de histórico comparativo
    if st.session_state.top10_history:
        st.divider()
        st.subheader("Histórico de Simulações desta Sessão")
        df_hist = pd.DataFrame(st.session_state.top10_history)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)

# ==============================================================================
# ABA 2: ESTRATÉGIA DE PNEUS (Regressão) — comparação multi-composto
# ==============================================================================
with tab2:
    st.subheader("Curva de Degradação por Composto")
    st.write("Consulte e compare os coeficientes de degradação calculados pelos modelos de regressão.")

    col_a, col_b = st.columns([1, 1])
    with col_a:
        compare_mode = st.toggle("Modo Comparação (SOFT vs HARD)", value=False)
    with col_b:
        num_laps_sim = st.slider("Número de voltas para simular", 5, 60, 30)

    compound_colors = {"SOFT": "#e10600", "HARD": "#4a4a4a", "MEDIUM": "#f1c40f"}

    if not compare_mode:
        compound_choice = st.selectbox("Selecione o Composto", ["SOFT", "HARD"])

        if st.button("Analisar Composto"):
            try:
                response = requests.get(f"{API_URL}/analytics/tires/{compound_choice}")
                if response.status_code == 200:
                    data = response.json()["data"]
                    base_pace = data["base_pace_seconds"]
                    deg_rate = data["degradation_per_lap_seconds"]

                    m1, m2, m3 = st.columns(3)
                    m1.metric("Ritmo Base (Volta 0)", f"{base_pace}s")
                    m2.metric("Degradação por Volta", f"{deg_rate}s")
                    m3.metric(f"Tempo Estimado (Volta {num_laps_sim})", f"{base_pace + deg_rate * num_laps_sim:.2f}s")

                    laps = list(range(1, num_laps_sim + 1))
                    lap_times = [base_pace + (deg_rate * l) for l in laps]

                    fig = px.line(
                        x=laps, y=lap_times,
                        labels={'x': 'Idade do Pneu (Voltas)', 'y': 'Tempo de Volta Estimado (s)'},
                        title=f"Evolução do Tempo de Volta — Composto {compound_choice}"
                    )
                    fig.update_traces(line_color=compound_colors.get(compound_choice, "#333"), line_width=3)
                    st.plotly_chart(fig, use_container_width=True)

                    # Tempo total acumulado (área sob a curva) — útil pra visão de estratégia
                    cumulative = np.cumsum(lap_times)
                    fig_cum = px.area(
                        x=laps, y=cumulative,
                        labels={'x': 'Volta', 'y': 'Tempo Acumulado (s)'},
                        title=f"Tempo Total Acumulado no Stint — {compound_choice}"
                    )
                    fig_cum.update_traces(line_color=compound_colors.get(compound_choice, "#333"))
                    st.plotly_chart(fig_cum, use_container_width=True)
                else:
                    st.error("Erro ao consultar dados do pneu.")
            except Exception as e:
                st.error(f"Erro ao conectar com a API: {e}")

    else:
        # Modo comparação lado a lado
        if st.button("Comparar SOFT vs HARD"):
            try:
                resp_soft = requests.get(f"{API_URL}/analytics/tires/SOFT")
                resp_hard = requests.get(f"{API_URL}/analytics/tires/HARD")

                if resp_soft.status_code == 200 and resp_hard.status_code == 200:
                    data_soft = resp_soft.json()["data"]
                    data_hard = resp_hard.json()["data"]

                    laps = list(range(1, num_laps_sim + 1))
                    soft_times = [data_soft["base_pace_seconds"] + data_soft["degradation_per_lap_seconds"] * l for l in laps]
                    hard_times = [data_hard["base_pace_seconds"] + data_hard["degradation_per_lap_seconds"] * l for l in laps]

                    df_compare = pd.DataFrame({
                        "Volta": laps + laps,
                        "Tempo (s)": soft_times + hard_times,
                        "Composto": ["SOFT"] * len(laps) + ["HARD"] * len(laps)
                    })

                    fig_compare = px.line(
                        df_compare, x="Volta", y="Tempo (s)", color="Composto",
                        color_discrete_map=compound_colors,
                        title="Comparação de Degradação: SOFT vs HARD"
                    )
                    fig_compare.update_traces(line_width=3)
                    st.plotly_chart(fig_compare, use_container_width=True)

                    # Ponto de cruzamento (crossover) — quando HARD se torna mais rápido que SOFT
                    diffs = np.array(hard_times) - np.array(soft_times)
                    crossover_idx = np.where(diffs < 0)[0]

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Ritmo Base SOFT", f"{data_soft['base_pace_seconds']}s")
                    c2.metric("Ritmo Base HARD", f"{data_hard['base_pace_seconds']}s")
                    if len(crossover_idx) > 0:
                        c3.metric("Volta de Crossover", f"Volta {crossover_idx[0] + 1}")
                        st.success(f"A partir da volta **{crossover_idx[0] + 1}**, o composto HARD se torna mais rápido que o SOFT devido à degradação.")
                    else:
                        c3.metric("Volta de Crossover", "Não ocorre no intervalo")
                else:
                    st.error("Erro ao consultar um ou ambos os compostos.")
            except Exception as e:
                st.error(f"Erro ao conectar com a API: {e}")

# ==============================================================================
# ABA 3: CLUSTERIZAÇÃO DE PILOTOS (K-Means) — com mapa de dispersão
# ==============================================================================
with tab3:
    st.subheader("Classificação de Estilo de Pilotagem")
    st.write("Envie a telemetria agregada para identificar o perfil do piloto via K-Means.")

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        test_avg = st.number_input("Ritmo Médio (s)", value=77.5, key="cluster_avg")
    with c2:
        test_std = st.number_input("Desvio Padrão (s)", value=0.5, key="cluster_std")
    with c3:
        test_label = st.text_input("Nome/Identificador do Piloto", value="", key="cluster_label")

    profiles = {
        0: ("🟢 Cluster 0: Alta Consistência e Ritmo Forte", "Pilotos de Elite/Líderes"),
        1: ("🔴 Cluster 1: Ritmo Lento e Fundo de Grid", "Pilotos com tempos altos"),
        2: ("🟡 Cluster 2: Ritmo Intermediário, mas Inconsistente", "Pilotos Agressivos/Oscilantes")
    }
    cluster_colors = {0: "#2ecc71", 1: "#e74c3c", 2: "#f1c40f"}

    b1, b2 = st.columns([3, 1])
    with b1:
        run_cluster = st.button("Identificar Cluster")
    with b2:
        if st.button("Limpar Mapa"):
            st.session_state.cluster_history = []
            st.rerun()

    if run_cluster:
        payload = {"avg_lap_time": test_avg, "std_lap_time": test_std}
        try:
            response = requests.post(f"{API_URL}/analytics/drivers/cluster", json=payload)
            if response.status_code == 200:
                cluster_id = response.json()["data"]["assigned_cluster"]

                st.session_state.cluster_history.append({
                    "Piloto": test_label if test_label else f"Piloto {len(st.session_state.cluster_history)+1}",
                    "Ritmo Médio (s)": test_avg,
                    "Desvio Padrão (s)": test_std,
                    "Cluster": cluster_id
                })

                title, desc = profiles.get(cluster_id, ("Cluster não mapeado", ""))
                st.success(f"Piloto classificado no **Cluster {cluster_id}**")
                st.markdown(f"**{title}**")
                st.caption(desc)
            else:
                st.error("Erro ao processar clusterização.")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")

    # Mapa de dispersão acumulado de todos os pilotos classificados na sessão
    if st.session_state.cluster_history:
        st.divider()
        st.subheader("Mapa de Dispersão dos Pilotos Classificados")
        df_cluster = pd.DataFrame(st.session_state.cluster_history)
        df_cluster["Cluster"] = df_cluster["Cluster"].astype(str)

        fig_scatter = px.scatter(
            df_cluster, x="Ritmo Médio (s)", y="Desvio Padrão (s)",
            color="Cluster", text="Piloto", size=[15] * len(df_cluster),
            color_discrete_map={"0": "#2ecc71", "1": "#f1c40f", "2": "#e74c3c"},
            title="Distribuição dos Pilotos por Ritmo e Consistência"
        )
        fig_scatter.update_traces(textposition="top center")
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.dataframe(df_cluster, use_container_width=True, hide_index=True)

        # Contagem por cluster
        counts = df_cluster["Cluster"].value_counts().reset_index()
        counts.columns = ["Cluster", "Quantidade"]
        fig_counts = px.pie(
            counts, names="Cluster", values="Quantidade",
            color="Cluster",
            color_discrete_map={"0": "#2ecc71", "1": "#f1c40f", "2": "#e74c3c"},
            title="Distribuição de Pilotos por Perfil"
        )
        st.plotly_chart(fig_counts, use_container_width=True)

# ==============================================================================
# ABA 4: COMPARADOR DE CENÁRIOS (Head-to-Head)
# ==============================================================================
with tab4:
    st.subheader("Comparador de Cenários Lado a Lado")
    st.write("Compare dois cenários de corrida completos, incluindo previsão de pontuação e cluster de pilotagem.")

    scenario_col1, scenario_col2 = st.columns(2)

    with scenario_col1:
        st.markdown("### 🔵 Cenário A")
        a_grid = st.slider("Grid A", 1, 20, 3, key="a_grid")
        a_avg = st.number_input("Ritmo Médio A (s)", value=76.0, key="a_avg")
        a_std = st.number_input("Consistência A (s)", value=0.6, key="a_std")
        a_gained = st.slider("Pos. Ganhas A", -15, 15, 2, key="a_gained")
        a_rain = st.selectbox("Clima A", [0, 1], format_func=lambda x: "Molhada 🌧️" if x else "Seca ☀️", key="a_rain")

    with scenario_col2:
        st.markdown("### 🟠 Cenário B")
        b_grid = st.slider("Grid B", 1, 20, 8, key="b_grid")
        b_avg = st.number_input("Ritmo Médio B (s)", value=77.2, key="b_avg")
        b_std = st.number_input("Consistência B (s)", value=1.1, key="b_std")
        b_gained = st.slider("Pos. Ganhas B", -15, 15, -1, key="b_gained")
        b_rain = st.selectbox("Clima B", [0, 1], format_func=lambda x: "Molhada 🌧️" if x else "Seca ☀️", key="b_rain")

    if st.button("Comparar Cenários", type="primary"):
        payload_a = {"grid_position": a_grid, "avg_lap_time": a_avg, "std_lap_time": a_std, "positions_gained": a_gained, "is_rainy": a_rain}
        payload_b = {"grid_position": b_grid, "avg_lap_time": b_avg, "std_lap_time": b_std, "positions_gained": b_gained, "is_rainy": b_rain}

        try:
            resp_a = requests.post(f"{API_URL}/predictions/top10", json=payload_a)
            resp_b = requests.post(f"{API_URL}/predictions/top10", json=payload_b)

            if resp_a.status_code == 200 and resp_b.status_code == 200:
                data_a = resp_a.json()["data"]
                data_b = resp_b.json()["data"]

                res_col1, res_col2 = st.columns(2)
                res_col1.metric("Probabilidade A", f"{data_a['probability_percentage']}%")
                res_col2.metric("Probabilidade B", f"{data_b['probability_percentage']}%")

                fig_compare = go.Figure(data=[
                    go.Bar(name="Cenário A", x=["Probabilidade Top 10 (%)"], y=[data_a["probability_percentage"]], marker_color="#3498db"),
                    go.Bar(name="Cenário B", x=["Probabilidade Top 10 (%)"], y=[data_b["probability_percentage"]], marker_color="#e67e22")
                ])
                fig_compare.update_layout(title="Cenário A vs Cenário B", barmode='group', bargap=0.8, bargroupgap=0.1)
                st.plotly_chart(fig_compare, use_container_width=True)

                if data_a["probability_percentage"] > data_b["probability_percentage"]:
                    st.success("🔵 O **Cenário A** apresenta maior probabilidade de pontuação.")
                elif data_b["probability_percentage"] > data_a["probability_percentage"]:
                    st.success("🟠 O **Cenário B** apresenta maior probabilidade de pontuação.")
                else:
                    st.info("Os cenários apresentam probabilidades equivalentes.")
            else:
                st.error("Erro ao processar um ou ambos os cenários.")
        except Exception as e:
            st.error(f"Erro ao conectar com a API: {e}")

# ==============================================================================
# ABA 5: SIMULADOR DE PIT STOP
# ==============================================================================
# ==============================================================================
# ABA 5: SIMULADOR DE PIT STOP (Simulação Volta-a-Volta)
# ==============================================================================
with tab5:
    st.subheader("Simulador de Estratégia de Pit Stop")
    st.write("Simule a evolução volta-a-volta de corridas comparando 1 e 2 paradas nos boxes.")

    total_race_laps = st.slider("Total de Voltas da Corrida", 20, 78, 58)
    pit_loss = st.number_input("Tempo Perdido por Pit Stop (segundos)", value=22.0, step=0.5)

    strat_col1, strat_col2 = st.columns(2)

    with strat_col1:
        st.markdown("#### 🔴 Estratégia 1: 1 Parada")
        st1_c1 = st.selectbox("Stint 1 (Composto)", ["SOFT", "HARD"], index=0, key="s1_c1")
        st1_laps1 = st.slider("Voltas no Stint 1", 1, total_race_laps - 1, total_race_laps // 2, key="s1_laps1")
        st1_c2 = st.selectbox("Stint 2 (Composto)", ["SOFT", "HARD"], index=1, key="s1_c2")

    with strat_col2:
        st.markdown("#### 🔵 Estratégia 2: 2 Paradas")
        st2_c1 = st.selectbox("Stint A (Composto)", ["SOFT", "HARD"], index=0, key="s2_c1")
        st2_laps_a = st.slider("Voltas Stint A", 1, total_race_laps - 2, total_race_laps // 3, key="s2_laps_a")
        st2_c2 = st.selectbox("Stint B (Composto)", ["SOFT", "HARD"], index=1, key="s2_c2")
        
        max_laps_b = max(1, total_race_laps - st2_laps_a - 1)
        default_b = min(total_race_laps // 3, max_laps_b)
        
    st2_laps_b = st.slider("Voltas Stint B", 1, max_laps_b, default_b, key="s2_laps_b")
    st2_c3 = st.selectbox("Stint C (Composto)", ["SOFT", "HARD"], index=0, key="s2_c3")

    if st.button("Simular Estratégias", type="primary"):
        try:
            resp_soft = requests.get(f"{API_URL}/analytics/tires/SOFT")
            resp_hard = requests.get(f"{API_URL}/analytics/tires/HARD")

            if resp_soft.status_code == 200 and resp_hard.status_code == 200:
                tire_data = {
                    "SOFT": resp_soft.json()["data"],
                    "HARD": resp_hard.json()["data"]
                }

                # Simulação Lap-by-Lap para Estratégia 1 (1 Parada)
                st1_laps2 = max(0, total_race_laps - st1_laps1)
                laps_s1_times = []
                
                # Stint 1
                for lap in range(1, st1_laps1 + 1):
                    t = tire_data[st1_c1]["base_pace_seconds"] + tire_data[st1_c1]["degradation_per_lap_seconds"] * lap
                    if lap == st1_laps1:
                        t += pit_loss  # Adiciona tempo do pit stop na última volta do stint
                    laps_s1_times.append(t)
                
                # Stint 2
                for lap in range(1, st1_laps2 + 1):
                    t = tire_data[st1_c2]["base_pace_seconds"] + tire_data[st1_c2]["degradation_per_lap_seconds"] * lap
                    laps_s1_times.append(t)

                # Simulação Lap-by-Lap para Estratégia 2 (2 Paradas)
                st2_laps_c = max(0, total_race_laps - st2_laps_a - st2_laps_b)
                laps_s2_times = []

                # Stint A
                for lap in range(1, st2_laps_a + 1):
                    t = tire_data[st2_c1]["base_pace_seconds"] + tire_data[st2_c1]["degradation_per_lap_seconds"] * lap
                    if lap == st2_laps_a:
                        t += pit_loss
                    laps_s2_times.append(t)
                
                # Stint B
                for lap in range(1, st2_laps_b + 1):
                    t = tire_data[st2_c2]["base_pace_seconds"] + tire_data[st2_c2]["degradation_per_lap_seconds"] * lap
                    if lap == st2_laps_b:
                        t += pit_loss
                    laps_s2_times.append(t)

                # Stint C
                for lap in range(1, st2_laps_c + 1):
                    t = tire_data[st2_c3]["base_pace_seconds"] + tire_data[st2_c3]["degradation_per_lap_seconds"] * lap
                    laps_s2_times.append(t)

                # Métricas Totais
                time_s1 = sum(laps_s1_times)
                time_s2 = sum(laps_s2_times)
                delta = time_s1 - time_s2

                m1, m2, m3 = st.columns(3)
                m1.metric("Tempo Total (1 Parada)", f"{time_s1:,.1f}s")
                m2.metric("Tempo Total (2 Paradas)", f"{time_s2:,.1f}s")
                m3.metric("Diferença Final", f"{abs(delta):.1f}s", delta=f"{'2 Paradas mais rápida' if delta > 0 else '1 Parada mais rápida'}")

                # Preparação dos dados para os gráficos
                race_laps = list(range(1, total_race_laps + 1))
                df_race = pd.DataFrame({
                    "Volta": race_laps + race_laps,
                    "Tempo de Volta (s)": laps_s1_times + laps_s2_times,
                    "Estratégia": ["1 Parada"] * total_race_laps + ["2 Paradas"] * total_race_laps
                })

                #"" Gráfico 1: Ritmo por Volta (com o 'pulo' visual do Pit Stop)
                fig_laps = px.line(
                    df_race, x="Volta", y="Tempo de Volta (s)", color="Estratégia",
                    color_discrete_map={"1 Parada": "#e10600", "2 Paradas": "#3498db"},
                    title="Ritmo por Volta e Janela de Pit Stops (Picos indicam entradas nos boxes)"
                )
                fig_laps.update_traces(line_width=2.5)
                st.plotly_chart(fig_laps, use_container_width=True)

                #"" Gráfico 2: Vantagem Acumulada da Estratégia de 2 Paradas (Gap Chart)
                cum_s1 = np.cumsum(laps_s1_times)
                cum_s2 = np.cumsum(laps_s2_times)
                gap = cum_s1 - cum_s2  # Posição relativa: valores > 0 significam que 2 Paradas está na frente

                df_gap = pd.DataFrame({
                    "Volta": race_laps,
                    "Vantagem da 2 Paradas (s)": gap
                })

                fig_gap = px.area(
                    df_gap, x="Volta", y="Vantagem da 2 Paradas (s)",
                    title="Evolução da Vantagem Acumulada (Acima de 0 = 2 Paradas Liderando)"
                )
                fig_gap.update_traces(line_color="#2ecc71" if delta > 0 else "#e74c3c")
                st.plotly_chart(fig_gap, use_container_width=True)

                if delta > 0:
                    st.success(f" A estratégia de **2 paradas** é mais rápida em {abs(delta):.1f} segundos no tempo total da corrida.")
                else:
                    st.success(f" A estratégia de **1 parada** é mais rápida em {abs(delta):.1f} segundos no tempo total da corrida.")

            else:
                st.error("Erro ao obter dados de degradação dos compostos.")
        except Exception as e:
            st.error(f"Erro ao conectar com a API: {e}")

# ==============================================================================
# RODAPÉ
# ==============================================================================
st.divider()
st.caption("F1 Race Intelligence • Painel construído com Streamlit + Plotly • Backend em Flask")
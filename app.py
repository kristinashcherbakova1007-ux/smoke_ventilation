import streamlit as st
import pandas as pd
import numpy as np
from formulas import calculate_scenario_1, create_floors_data
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf
from matplotlib.backends.backend_pdf import PdfPages
from io import BytesIO
import datetime

# Настройка страницы
st.set_page_config(page_title="Расчет основных параметров противодымной вентиляции зданий", layout="wide")

# Создаем состояние для хранения результатов
results_state = st.session_state

# Инициализируем переменные состояния
if 'results' not in results_state:
    results_state.results = None
if 'calculated' not in results_state:
    results_state.calculated = False

# Заголовок приложения
st.title("Расчет основных параметров противодымной вентиляции зданий")

# Выбор сценария
st.subheader("Выбор сценария расчета")
scenario = st.selectbox(
    "Выберите сценарий расчета:",
    options=range(1, 20),
    format_func=lambda x: f"Сценарий {x}"
)

if scenario == 1:
    st.info("Выбран сценарий: вытяжная противодымная вентиляция из помещений пожара: из зальных помещений; из атриумов, на нескольких уровнях которого находятся галереи, или из атриумов, конструктивно изолированных от этажей здания; из закрытых надземных и подземных автостоянок")

    col1, col2 = st.columns(2)
    with col1:

        # Ввод параметров помещения
        st.subheader("1. Параметры помещения")
        t_r = st.number_input("Температура воздуха в помещении, °C", value=10, step=1)
        A = st.number_input("Длина помещения, м", value=3.0, step=0.1)
        B = st.number_input("Ширина помещения, м", value=3.0, step=0.1)
        H = st.number_input("Высота помещения, м", value=2.5, step=0.1)
        AUPT = st.number_input("Система АУПТ (0 - отсутствует, 1 - скринклеры 3x3 , 2 - спринклеры 4x4)", value=0, step=1)

        # Ввод параметров пожарной нагрузки
        st.subheader("2. Параметры пожарной нагрузки")
        eta = st.number_input("Полнота сгорания пожарной нагрузки", value=0.85, step=0.01)
        Q_average = st.number_input("Средняя теплота сгорания пожарной нагрузки, кДж/кг", value=13800, step=1)
        U_average = st.number_input("Линейная скорость распространения пламени по поверхности пожарной нагрузки, м/с", value=0.0108, step=0.0001)
        psi_average = st.number_input("Средняя скорость потери массы пожарной нагрузки, кг/(м²·с)", value=0.0145, step=0.0001)

    with col2:

        # Ввод параметров пожара
        st.subheader("3. Параметры пожара")
        tau_f = st.number_input("Время развития очага пожара (600 с - город, 1200 с - за городом), с", value=600, step=1)
        r = st.number_input("Коэффициент, характеризующий теплопотери на излучение", value=0.70, step=0.01)
        z = st.number_input("Высота незадымляемой зоны, м", value=2.5, step=0.1)

        # Ввод параметров компенсирующей подачи воздуха
        st.subheader("4. Параметры компенсирующей подачи воздуха")
        n = st.number_input("Коэффициент дисбаланса", value=-0.3, step=0.1)
        t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
        R_a = st.number_input("Эквивалентное сопротивление воздухоприточного канала, кг⁻¹·м⁻¹", value=0.01, step=0.01)

        # Ввод параметров вентилятора
        st.subheader("5. Параметры вентилятора")
        P_d = st.number_input("Суммарное сопротивление присоединительных воздуховодов, Па", value=50, step=1)
        
    # Ввод параметров начального участка вытяжного канала
    st.subheader("6. Параметры начального участка вытяжного канала")
    initial_data = pd.DataFrame({
        'A_0': [0.50],
        'B_0': [0.50],
        'F_0': [0.2025],
        'l_0': [0.10],
        'xi_0': [2.39],
        'k_0': [0.10]
    }, index=['Значение'])

    initial_table = st.data_editor(
        initial_data,
        column_config={
            'A_0': st.column_config.NumberColumn("A_0, м", format="%.2f"),
            'B_0': st.column_config.NumberColumn("B_0, м", format="%.2f"),
            'F_0': st.column_config.NumberColumn("F_0, м²", format="%.4f"),
            'l_0': st.column_config.NumberColumn("l_0, м", format="%.2f"),
            'xi_0': st.column_config.NumberColumn("ξ_0", format="%.2f"),
            'k_0': st.column_config.NumberColumn("k_0, мм", format="%.2f")
        },
        num_rows="fixed"
    )
    
    # Ввод параметров промежуточного участка вытяжного канала
    st.subheader("7. Параметры промежуточного участка вытяжного канала")
    intermediate_data = pd.DataFrame({
        'A_int': [0.50],
        'B_int': [0.50],
        'l_int': [0.50],
        'xi_int': [0.00],
        'k_int': [0.10],
        'R_int': [0.00],
        'epsilon_l_int': [1.00],
        'delta_h_2_int': [0.0010],
        'delta_h_3_int': [0.0100],
        'lambda_1_int': [52.00],
        'lambda_2_int': [0.030]
    }, index=['Значение'])

    intermediate_table = st.data_editor(
        intermediate_data,
        column_config={
            'A_int': st.column_config.NumberColumn("A'_0, м", format="%.2f"),
            'B_int': st.column_config.NumberColumn("B'_0, м", format="%.2f"),
            'l_int': st.column_config.NumberColumn("l'_0, м", format="%.2f"),
            'xi_int': st.column_config.NumberColumn("ξ'_0", format="%.2f"),
            'k_int': st.column_config.NumberColumn("k'_0, мм", format="%.2f"),
            'R_int': st.column_config.NumberColumn("R'_0, м", format="%.2f"),
            'epsilon_l_int': st.column_config.NumberColumn("ε'_l0", format="%.2f"),
            'delta_h_2_int': st.column_config.NumberColumn("Δh'_20, м", format="%.4f"),
            'delta_h_3_int': st.column_config.NumberColumn("Δh'_30, м", format="%.4f"),
            'lambda_1_int': st.column_config.NumberColumn("λ'_10, Вт/(м·К)", format="%.2f"),
            'lambda_2_int': st.column_config.NumberColumn("λ'_20, Вт/(м·К)", format="%.4f")
        },
        num_rows="fixed"
    )

    # Ввод параметров узла присоединения начального участка вытяжного канала к вертикальному коллектору
    st.subheader("8. Параметры узла присоединения начального участка вытяжного канала к вертикальному коллектору")
    node_data = pd.DataFrame({
        'A_node': [1.00],
        'B_node': [1.00],
        'xi_node': [0.00]
    }, index=['Значение'])

    node_table = st.data_editor(
        node_data,
        column_config={
            'A_node': st.column_config.NumberColumn('A"_0, м', format="%.2f"),
            'B_node': st.column_config.NumberColumn('B"_0, м', format="%.2f"),
            'xi_node': st.column_config.NumberColumn('ξ"_0', format="%.2f")
        },
        num_rows="fixed"
    )

    # Ввод параметров вертикального коллектора
    st.subheader("9. Параметры вертикального коллектора")
    N = st.number_input("Количество участков вертикального коллектора", value=10, step=1)
    # Создаем редактируемую таблицу
    collector_data = pd.DataFrame({
        'A': [0.5]*N,
        'B': [0.5]*N,
        'l': [2.5]*N,
        'xi': [0.0]*N,
        'k': [0.1]*N,
        'A_dp': [0.5]*N,
        'B_dp': [0.5]*N,
        'F_dp': [0.2025]*N,
        'R': [0.0]*N,
        'epsilon_l': [1.0]*N,
        'delta_h_2': [0.001]*N,
        'delta_h_3': [0.01]*N,
        'lambda_1': [52.0]*N,
        'lambda_2': [0.03]*N
    }, index=[f'Участок {i}' for i in range(1, N+1)])

    columns = {
        'A': st.column_config.NumberColumn("A, м", format="%.2f"),
        'B': st.column_config.NumberColumn("B, м", format="%.2f"),
        'l': st.column_config.NumberColumn("l, м", format="%.2f"),
        'xi': st.column_config.NumberColumn("ξ", format="%.2f"),
        'k': st.column_config.NumberColumn("k, мм", format="%.2f"),
        'A_dp': st.column_config.NumberColumn("A_dp, м", format="%.2f"),
        'B_dp': st.column_config.NumberColumn("B_dp, м", format="%.2f"),
        'F_dp': st.column_config.NumberColumn("F_dp, м²", format="%.2f"),
        'R': st.column_config.NumberColumn("R, м", format="%.2f"),
        'epsilon_l': st.column_config.NumberColumn("ε_l", format="%.2f"),
        'delta_h_2': st.column_config.NumberColumn("Δh_2, м", format="%.4f"),
        'delta_h_3': st.column_config.NumberColumn("Δh_3, м", format="%.4f"),
        'lambda_1': st.column_config.NumberColumn("λ_1, Вт/(м·К)", format="%.2f"),
        'lambda_2': st.column_config.NumberColumn("λ_2, Вт/(м·К)", format="%.2f")
    }

    edited_collector = st.data_editor(
        collector_data,
        column_config=columns,
        key='collector_editor'
    )
    
    # Собираем все параметры в единый список словарей
    floors_data = []
    for i in range(1, N+1):
        floor = {
            'A': edited_collector.loc[f'Участок {i}', 'A'],
            'B': edited_collector.loc[f'Участок {i}', 'B'],
            'l': edited_collector.loc[f'Участок {i}', 'l'],
            'xi': edited_collector.loc[f'Участок {i}', 'xi'],
            'k': edited_collector.loc[f'Участок {i}', 'k'],
            'A_dp': edited_collector.loc[f'Участок {i}', 'A_dp'],
            'B_dp': edited_collector.loc[f'Участок {i}', 'B_dp'],
            'F_dp': edited_collector.loc[f'Участок {i}', 'F_dp'],
            'R': edited_collector.loc[f'Участок {i}', 'R'],
            'epsilon_l': edited_collector.loc[f'Участок {i}', 'epsilon_l'],
            'delta_h_2': edited_collector.loc[f'Участок {i}', 'delta_h_2'],
            'delta_h_3': edited_collector.loc[f'Участок {i}', 'delta_h_3'],
            'lambda_1': edited_collector.loc[f'Участок {i}', 'lambda_1'],
            'lambda_2': edited_collector.loc[f'Участок {i}', 'lambda_2']
        }
        floors_data.append(floor)

    # Собираем все входные данные
    input_data = {
        # Параметры помещения
        't_r': t_r,
        'A': A,
        'B': B,
        'H': H,
        'AUPT': AUPT,
    
        # Параметры пожарной нагрузки
        'eta': eta,
        'Q_average': Q_average,
        'U_average': U_average,
        'psi_average': psi_average,
    
        # Параметры пожара
        'tau_f': tau_f,
        'r': r,
        'z': z,
    
        # Параметры компенсирующей подачи воздуха
        'n': n,
        't_a': t_a,
        'R_a': R_a,
    
        # Параметры начального участка вытяжного канала
        'A_0': initial_table['A_0'][0],
        'B_0': initial_table['B_0'][0],
        'F_0': initial_table['F_0'][0],
        'l_0': initial_table['l_0'][0],
        'xi_0': initial_table['xi_0'][0],
        'k_0': initial_table['k_0'][0],
    
        # Параметры промежуточного участка вытяжного канала
        'A_int': intermediate_table['A_int'][0],
        'B_int': intermediate_table['B_int'][0],
        'l_int': intermediate_table['l_int'][0],
        'xi_int': intermediate_table['xi_int'][0],
        'k_int': intermediate_table['k_int'][0],
        'R_int': intermediate_table['R_int'][0],
        'epsilon_l_int': intermediate_table['epsilon_l_int'][0],
        'delta_h_2_int': intermediate_table['delta_h_2_int'][0],
        'delta_h_3_int': intermediate_table['delta_h_3_int'][0],
        'lambda_1_int': intermediate_table['lambda_1_int'][0],
        'lambda_2_int': intermediate_table['lambda_2_int'][0],
    
        # Параметры узла присоединения начального участка вытяжного канала к вертикальному коллектору
        'A_node': node_table['A_node'][0],
        'B_node': node_table['B_node'][0],
        'xi_node': node_table['xi_node'][0],

        # Параметры вертикального коллектора
        'floors_data': floors_data,
        'N': N,  # Количество участков
    
        # Параметры вентилятора
        'P_d': P_d
    }

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Получаем параметры первого участка
            first_floor = floors_data[0]
            first_floor_params = {
                'A_1': first_floor['A'],
                'B_1': first_floor['B'],
                'l_1': first_floor['l'],
                'xi_1': first_floor['xi'],
                'k_1': first_floor['k'],
                'A_dp_1': first_floor['A_dp'],
                'B_dp_1': first_floor['B_dp'],
                'F_dp_1': first_floor['F_dp'],
                'R_1': first_floor['R'],
                'epsilon_l_1': first_floor['epsilon_l'],
                'delta_h_2_1': first_floor['delta_h_2'],
                'delta_h_3_1': first_floor['delta_h_3'],
                'lambda_1_1': first_floor['lambda_1'],
                'lambda_2_1': first_floor['lambda_2']
            }
            
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_1(**input_data, **first_floor_params)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            # Вывод параметров пожара
            st.subheader("1. Параметры пожара")
            col1, col2 = st.columns(2)
            with col1:
                st.number_input(
                    label="Площадь помещения, м²",
                    value=formatted_results.get('F', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Площадь очага пожара, м²",
                    value=formatted_results.get('F_f', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Мощность тепловыделения очага пожара, кВт",
                    value=formatted_results.get('Q_f', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Высота факела пламени, м",
                    value=formatted_results.get('z_1', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Толщина дымового слоя, м",
                    value=formatted_results.get('h_sm', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Массовый расход продуктов горения в конвективной колонке, кг/с",
                    value=formatted_results.get('G_k', 0.0),
                    disabled=True,
                    format="%.2f"
                )

                st.number_input(
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Удельная теплоемкость газа при температуре T_sm, кДж/(кг·К)",
                    value=formatted_results.get('c_psm', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Удельная теплоемкость газа при температуре T_k, кДж/(кг·К)",
                    value=formatted_results.get('c_pk', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура в конвективной колонке, К",
                    value=formatted_results.get('T_k', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Коэффициент теплоотдачи, кВт/(м²·К)",
                    value=formatted_results.get('alpha', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            # Вывод параметров компенсирующей подачи воздуха
            with col2:
                st.number_input(
                    label="Максимальный периметр сечения дымового слоя в горизонтальной плоскости, м",
                    value=formatted_results.get('l_sm', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Эквивалентная площадь сечения дымового слоя в горизонтальной плоскости, м²",
                    value=formatted_results.get('A_sm', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура газа в дымовом слое, К",
                    value=formatted_results.get('T_sm', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность газа при температуре T_sm, кг/м³",
                    value=formatted_results.get('rho_sm', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Массовый расход продуктов горения в дымовом слое, кг/с",
                    value=formatted_results.get('G_sm', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                
                st.subheader("2. Параметры компенсирующей подачи воздуха")
                st.number_input(
                    label="Массовый расход подаваемого воздуха, кг/с",
                    value=formatted_results.get('G_a', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура наружного воздуха, К",
                    value=formatted_results.get('T_a', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_a, кг/м³",
                    value=formatted_results.get('rho_a', 0.0),
                    disabled=True,
                    format="%.2f"
                )

                st.number_input(
                    label="Объемный расход подаваемого воздуха, м³/ч",
                    value=formatted_results.get('L_a', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            # Вывод параметров начального участка вытяжного канала
            st.subheader("3. Параметры начального участка вытяжного канала")
            initial_results = pd.DataFrame({
                'G_sm0, кг/с': [results['G_sm_0']],
                'T_sm0, К': [results['T_sm_0']],
                'ρ_sm0, кг/м³': [results['rho_sm_0']],
                'P_0, Па': [results['P_0']],
                'ν_sm0, м/с': [results['nu_sm_0']],
                'd_e0, м': [results['d_e_0']],
                't_sm0, °C': [results['t_sm_0']],
                'μ_sm0, кг/(м·с)': [results['mu_sm_0']],
                'Re_0': [results['Re_0']],
                'λ_0': [results['lambda_0']],
                'P_sm0, Па': [results['P_sm_0']]
            }, index=['Значение'])
            st.dataframe(initial_results)

            # Вывод параметров промежуточного участка вытяжного канала
            st.subheader("4. Параметры промежуточного участка вытяжного канала")
            intermediate_results = pd.DataFrame({
                "F'_0, м²": [results['F_int']],
                "ν'_sm0, м/с": [results['nu_sm_int']],
                "d'_e0, м": [results['d_e_int']],
                "t'_sm0, °C": [results['t_sm_int']],
                "μ'_sm0, кг/(м·с)": [results['mu_sm_int']],
                "Re'_0": [results['Re_int']],
                "λ'_0": [results['lambda_int']],
                "P'_sm0, Па": [results['P_sm_int']],
                "ρ_r, кг/м³": [results['rho_r']],
                "ΔG'_da0, кг/с": [results['delta_G_da_int']],
                "G'_sm0, кг/с": [results['G_sm_int']],
                "D'_0, м": [results['D_int']],
                "ε'_R0": [results['epsilon_R_int']],
                "Pr'_f0": [results['Pr_f_int']],
                "t'_w0, °C": [results['t_w_int']],
                "Pr'_w0": [results['Pr_w_int']],
                "Nu'_f0": [results['Nu_f_int']],
                "A'_10, м": [results['A_1_int']],
                "B'_10, м": [results['B_1_int']],
                "d'_e10, м": [results['d_e_1_int']],
                "A'_20, м": [results['A_2_int']],
                "B'_20, м": [results['B_2_int']],
                "d'_e20, м": [results['d_e_2_int']],
                "A'_30, м": [results['A_3_int']],
                "B'_30, м": [results['B_3_int']],
                "d'_e30, м": [results['d_e_3_int']],
                "α'_10, Вт/(м²·К)": [results['alpha_1_int']],
                "α'_20, Вт/(м²·К)": [results['alpha_2_int']],
                "k'_l0, Вт/(м·К)": [results['k_l_int']],
                "q'_l0, кВт/м": [results['q_l_int']],
                "c_pr, кДж/(кг·К)": [results['c_pr']],
                "c'_psm0, кДж/(кг·К)": [results['c_psm_int']],
                "T'_sm0, К": [results['T_sm_int']],
                "ρ'_sm0, кг/м³": [results['rho_sm_int']]
            }, index=['Значение'])
            st.dataframe(intermediate_results)
      
            # Вывод параметров узла присоединения начального участка вытяжного канала к вертикальному коллектору
            st.subheader("5. Параметры узла присоединения начального участка вытяжного канала к вертикальному коллектору")
            node_results = pd.DataFrame({
                'F"_0, м²': [results['F_node']],
                'ν"_sm0, м/с': [results['nu_sm_node']],
                'P"_sm0, Па': [results['P_sm_node']]
            }, index=['Значение'])
            st.dataframe(node_results)

            # Вывод параметров вертикального коллектора
            st.subheader("6. Параметры вертикального коллектора")

            # Создаем пустой список для хранения данных
            collector_data = []

            # Список всех обязательных параметров для проверки
            required_params = [
                'F', 'nu_sm', 'd_e', 't_sm', 'mu_sm', 'Re', 'lambda', 'P_sm', 
                'delta_G_da', 'S_dpsm', 'delta_G_dpa', 'G_sm', 'D', 'epsilon_R', 
                'Pr_f', 't_w', 'Pr_w', 'Nu_f', 'A_1', 'B_1', 'd_e_1', 
                'A_2', 'B_2', 'd_e_2', 'A_3', 'B_3', 'd_e_3', 
                'alpha_1', 'alpha_2', 'k_l', 'q_l', 'c_psm', 
                'T_sm_new', 'rho_sm'
            ]

            for i in range(1, N+1):
                try:
                    # Создаем словарь с данными для текущего участка
                    row_data = {
                        'F, м²': results.get(f'F_{i}', 0),
                        'ν_sm, м/с': results.get(f'nu_sm_{i}', 0),
                        'd_e, м': results.get(f'd_e_{i}', 0),
                        't_sm, °C': results.get(f't_sm_{i}', 0),
                        'μ_sm, кг/(м·с)': results.get(f'mu_sm_{i}', 0),
                        'Re': results.get(f'Re_{i}', 0),
                        'λ': results.get(f'lambda_{i}', 0),
                        'P_sm, Па': results.get(f'P_sm_{i}', 0),
                        'ΔG_da, кг/с': results.get(f'delta_G_da_{i}', 0),
                        'S_dpsm, м³/кг': results.get(f'S_dpsm_{i}', 0),
                        'ΔG_dpa, кг/с': results.get(f'delta_G_dpa_{i}', 0),
                        'G_sm, кг/с': results.get(f'G_sm_{i}', 0),
                        'D, м': results.get(f'D_{i}', 0),
                        'ε_R': results.get(f'epsilon_R_{i}', 0),
                        'Pr_f': results.get(f'Pr_f_{i}', 0),
                        't_w, °C': results.get(f't_w_{i}', 0),
                        'Pr_w': results.get(f'Pr_w_{i}', 0),
                        'Nu_f': results.get(f'Nu_f_{i}', 0),
                        'A_1, м': results.get(f'A_1_{i}', 0),
                        'B_1, м': results.get(f'B_1_{i}', 0),
                        'd_e1, м': results.get(f'd_e_1_{i}', 0),
                        'A_2, м': results.get(f'A_2_{i}', 0),
                        'B_2, м': results.get(f'B_2_{i}', 0),
                        'd_e2, м': results.get(f'd_e_2_{i}', 0),
                        'A_3, м': results.get(f'A_3_{i}', 0),
                        'B_3, м': results.get(f'B_3_{i}', 0),
                        'd_e3, м': results.get(f'd_e_3_{i}', 0),
                        'α_1, Вт/(м²·К)': results.get(f'alpha_1_{i}', 0),
                        'α_2, Вт/(м²·К)': results.get(f'alpha_2_{i}', 0),
                        'k_l, Вт/(м·К)': results.get(f'k_l_{i}', 0),
                        'q_l, кВт/м': results.get(f'q_l_{i}', 0),
                        'c_psm, кДж/(кг·К)': results.get(f'c_psm_{i}', 0),
                        'T_sm, К': results.get(f'T_sm_{i}', 0),
                        'ρ_sm, кг/м³': results.get(f'rho_sm_{i}', 0)
                    }

                    # Проверяем, есть ли хотя бы одно ненулевое значение
                    if all(value == 0 for value in row_data.values() if isinstance(value, (int, float))):
                        continue  # Пропускаем полностью нулевой участок

                    # Добавляем строку в список
                    collector_data.append(row_data)

                except Exception as e:
                    st.error(f"Ошибка при обработке участка {i}: {e}")

            # Создаем итоговый DataFrame
            collector_df = pd.DataFrame(collector_data, index=[f'Участок {i}' for i in range(1, N+1)])
            st.dataframe(collector_df)
                    
            # Вывод параметров вентилятора
            st.subheader("7. Параметры вентилятора")
            st.number_input(
                label="Подача вентилятора, м³/ч",
                value=formatted_results.get('L_v', 0.0),
                disabled=True,
                format="%.2f"
            )

            st.number_input(
                label="Статическое давление вентилятора, Па",
                value=formatted_results.get('P_sv', 0.0),
                disabled=True,
                format="%.2f"
            )





            st.subheader("Зависимость температуры газа от участка вытяжного канала")

            # Создаем словарь для данных графика (остается без изменений)
            temperature_data = {
                'Участки': ['Начальный'] + ['Промежуточный'] + [f'Участок {i}' for i in range(1, N+1)],
                'Температура, К': [
                    results.get('T_sm_0', np.nan),
                    results.get('T_sm_int', np.nan),
                    * [results.get(f'T_sm_{i}', np.nan) for i in range(1, N+1)]
                ]
            }

            temp_df = pd.DataFrame(temperature_data)

            if temp_df.isnull().values.any():
                st.warning("Не все данные для построения графика доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # СТРОИМ ЕДИНУЮ КРИВУЮ
                ax.plot(
                    temp_df['Участки'],
                    temp_df['Температура, К'],
                    marker='o',
                    color='red',
                    linestyle='-',
                    label='Температурный профиль'
                )

                # Оформление (остается прежним)
                plt.xticks(rotation=45)
                ax.set_title('Зависимость температуры газа от участка вытяжного канала')
                ax.set_xlabel('Участок вытяжного канала')
                ax.set_ylabel('Температура, К')
                ax.grid(True)
                ax.legend()
                plt.tight_layout()
                st.pyplot(fig)

            # График зависимости давления
            st.subheader("Зависимость давления от участка вытяжного канала")

            # Создаем словарь для данных графика
            pressure_data = {
                'Участки': [
                    'Начальный', 
                    'Промежуточный', 
                    'Узел присоединения',
                    *[f'Участок {i}' for i in range(1, N+1)]
                ],
                'Давление, Па': [
                    results.get('P_sm_0', np.nan),  # Начальный участок
                    results.get('P_sm_int', np.nan),  # Промежуточный участок
                    results.get('P_sm_node', np.nan),  # Узел присоединения
                    *[results.get(f'P_sm_{i}', np.nan) for i in range(1, N+1)]  # Остальные участки
                ]
            }

            pressure_df = pd.DataFrame(pressure_data)

            if pressure_df.isnull().values.any():
                st.warning("Не все данные для построения графика давления доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую давления
                ax.plot(
                    pressure_df['Участки'],
                    pressure_df['Давление, Па'],
                    marker='o',
                    color='green',
                    linestyle='-',
                    label='Профиль давления'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость давления от участка вытяжного канала')
                ax.set_xlabel('Участок вытяжного канала')
                ax.set_ylabel('Давление, Па')
                ax.grid(True)
                ax.legend()
                plt.tight_layout()
    
                # Добавляем сетку и подписи
                ax.grid(axis='y', linestyle='--', alpha=0.7)
    
                # Отображаем график
                st.pyplot(fig)

            # График зависимости массового расхода
            st.subheader("Зависимость массового расхода продуктов горения от участка вытяжного канала")

            # Создаем словарь для данных графика
            mass_flow_data = {
                'Участки': [
                    'Начальный', 
                    'Промежуточный',
                    *[f'Участок {i}' for i in range(1, N+1)]
                ],
                'Массовый расход, кг/с': [
                    results.get('G_sm_0', np.nan),  # Начальный участок
                    results.get('G_sm_int', np.nan),  # Промежуточный участок
                    *[results.get(f'G_sm_{i}', np.nan) for i in range(1, N+1)]  # Остальные участки
                ]
            }

            mass_flow_df = pd.DataFrame(mass_flow_data)

            if mass_flow_df.isnull().values.any():
                st.warning("Не все данные для построения графика массового расхода доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую массового расхода
                ax.plot(
                    mass_flow_df['Участки'],
                    mass_flow_df['Массовый расход, кг/с'],
                    marker='o',
                    color='blue',
                    linestyle='-',
                    label='Профиль массового расхода'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость массового расхода от участка вытяжного канала')
                ax.set_xlabel('Участок вытяжного канала')
                ax.set_ylabel('Массовый расход, кг/с')
                ax.grid(True)
                ax.legend()
                plt.tight_layout()
    
                # Добавляем дополнительные элементы
                ax.grid(axis='y', linestyle='--', alpha=0.7)
    
                # Отображаем график
                st.pyplot(fig)

        except Exception as e:
            st.error(f"Произошла ошибка при расчете: {e}")

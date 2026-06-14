import streamlit as st
import pandas as pd
import numpy as np
from formulas import calculate_scenario_1, create_floors_data
from formulas import calculate_scenario_2, create_floors_data
from formulas import calculate_scenario_3, create_floors_data
from formulas import calculate_scenario_4, create_floors_data
from formulas import calculate_scenario_5, create_floors_data
from formulas import calculate_scenario_6, create_floors_data
from formulas import calculate_scenario_7, create_floors_data
from formulas import calculate_scenario_8, create_floors_data
from formulas import calculate_scenario_9, create_floors_data
from formulas import calculate_scenario_10, create_floors_data
from formulas import calculate_scenario_11, create_floors_data
from formulas import calculate_scenario_12, create_floors_data
from formulas import calculate_scenario_13, create_floors_data
from formulas import calculate_scenario_14
from formulas import calculate_scenario_15
from formulas import calculate_scenario_16
from formulas import calculate_scenario_17
from formulas import calculate_scenario_18
from formulas import calculate_scenario_19
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
    st.info("Выбран сценарий 1: вытяжная противодымная вентиляция из помещений пожара:")
    st.text("- из зальных помещений;")
    st.text("- из атриумов, на нескольких уровнях которого находятся галереи, или из атриумов, конструктивно изолированных от этажей здания;")
    st.text("- из закрытых надземных и подземных автостоянок.")

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




#############################################################################################################################################################################################################################################
if scenario == 2:
    st.info("Выбран сценарий 2: вытяжная вентиляция из помещений, смежных с помещением пожара:")
    st.text("- из коридоров;")
    st.text("- из холлов;")
    st.text("- из одноуровневых вестибюлей.")

    col1, col2 = st.columns(2)
    
    with col1:
        # Ввод параметров помещения
        st.subheader("1. Параметры помещения")
        t_r = st.number_input("Температура воздуха в помещении, °C", value=20, step=1)
        A = st.number_input("Длина помещения, м", value=3.0, step=0.1)
        B = st.number_input("Ширина помещения, м", value=3.0, step=0.1)
        H = st.number_input("Высота помещения, м", value=2.5, step=0.1)
        b_01 = st.number_input("Ширина 1-го проема помещения, м", value=1.0, step=0.1)
        h_01 = st.number_input("Высота 1-го проема помещения, м", value=2.0, step=0.1)
        b_02 = st.number_input("Ширина 2-го проема помещения, м", value=0.0, step=0.1)
        h_02 = st.number_input("Высота 2-го проема помещения, м", value=0.0, step=0.1)
        b_03 = st.number_input("Ширина 3-го проема помещения, м", value=0.0, step=0.1)
        h_03 = st.number_input("Высота 3-го проема помещения, м", value=0.0, step=0.1)
        b_04 = st.number_input("Ширина 4-го проема помещения, м", value=0.0, step=0.1)
        h_04 = st.number_input("Высота 4-го проема помещения, м", value=0.0, step=0.1)
        b_05 = st.number_input("Ширина 5-го проема помещения, м", value=0.0, step=0.1)
        h_05 = st.number_input("Высота 5-го проема помещения, м", value=0.0, step=0.1)
        A_c = st.number_input("Длина смежного помещения, м", value=3.0, step=0.1)
        B_c = st.number_input("Ширина смежного помещения, м", value=3.0, step=0.1)
        H_c = st.number_input("Высота смежного помещения, м", value=2.5, step=0.1)
        k_sm = st.number_input("Коэффициент (1,0 - для жилых зданий, 1,2 - для общественных зданий)", value=1.0, step=0.1)
        B_d = st.number_input("Ширина двери при выходе из смежного помещения по путям эвакуации, м", value=1.0, step=0.1)
        H_d = st.number_input("Высота двери при выходе из смежного помещения по путям эвакуации, м", value=2.0, step=0.1)

    with col2:
        # Ввод параметров пожарной нагрузки
        st.subheader("2. Параметры пожарной нагрузки")
        M = st.number_input("Масса пожарной нагрузки помещения, кг", value=50.0, step=0.1)
        Q_average = st.number_input("Средняя теплота сгорания пожарной нагрузки, кДж/кг", value=13800, step=1)
        U_average = st.number_input("Линейная скорость распространения пламени по поверхности пожарной нагрузки, м/с", value=0.0108, step=0.0001)
        psi_average = st.number_input("Средняя скорость потери массы пожарной нагрузки, кг/(м²·с)", value=0.0145, step=0.0001)

        # Ввод параметров компенсирующей подачи воздуха
        st.subheader("3. Параметры компенсирующей подачи воздуха")
        n = st.number_input("Коэффициент дисбаланса", value=-0.3, step=0.1)
        t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
        R_a = st.number_input("Эквивалентное сопротивление воздухоприточного канала, кг⁻¹·м⁻¹", value=0.01, step=0.01)

        # Ввод параметров вентилятора
        st.subheader("4. Параметры вентилятора")
        P_d = st.number_input("Суммарное сопротивление присоединительных воздуховодов, Па", value=50, step=1)
        
    # Ввод параметров начального участка вытяжного канала
    st.subheader("5. Параметры начального участка вытяжного канала")
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
    st.subheader("6. Параметры промежуточного участка вытяжного канала")
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
    st.subheader("7. Параметры узла присоединения начального участка вытяжного канала к вертикальному коллектору")
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
    st.subheader("8. Параметры вертикального коллектора")
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
        'A': A, 'B': B, 'H': H,
        'b_01': b_01, 'h_01': h_01, 'b_02': b_02, 'h_02': h_02, 'b_03': b_03, 'h_03': h_03, 'b_04': b_04, 'h_04': h_04, 'b_05': b_05, 'h_05': h_05,
        'A_c': A_c, 'B_c': B_c, 'H_c': H_c,
        'k_sm': k_sm,
        'B_d': B_d, 'H_d': H_d,

        # Параметры пожарной нагрузки
        'M': M,
        'Q_average': Q_average,
        'U_average': U_average,
        'psi_average': psi_average,
    
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
            results_state.results = calculate_scenario_2(**input_data, **first_floor_params)
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
                    label="Cуммарная площадь внутренней поверхности ограждающих строительных конструкций помещения, м²",
                    value=formatted_results.get('F_w', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Суммарная площадь проемов помещения, м²",
                    value=formatted_results.get('F_0', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Удельная приведенная пожарная нагрузка, отнесенная к площади тепловоспринимающей поверхности ограждающих строительных конструкций помещения, кг/м²",
                    value=formatted_results.get('g_k', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Проемность помещения, м^̇1/2",
                    value=formatted_results.get('P', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Удельное количество воздуха, необходимое для полного сгорания пожарной нагрузки помещения, м³/кг",
                    value=formatted_results.get('V_0', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Удельное критическое количество пожарной нагрузки, кг/м²",
                    value=formatted_results.get('g_kkp', 0.0),
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
                    label="Площадь помещения, м²",
                    value=formatted_results.get('F', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Удельная приведенная пожарная нагрузка, отнесенная к площади помещения, кг/м²",
                    value=formatted_results.get('g_0', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Максимальная среднеобъемная температура в помещении, К",
                    value=formatted_results.get('T_0_max', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура газов, поступающих из горящего помещения в смежное помещение, К",
                    value=formatted_results.get('T_0', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Предельная толщина дымового слоя, м",
                    value=formatted_results.get('h_sm', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Площадь смежного помещения, м²",
                    value=formatted_results.get('F_c', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Средняя температура дымового слоя, К",
                    value=formatted_results.get('T_sm', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Площадь двери при выходе из смежного помещения по путям эвакуации, м²",
                    value=formatted_results.get('F_d', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Массовый расход удаляемых непосредственно из смежного помещения продуктов горения, кг/с",
                    value=formatted_results.get('G_sm', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            # Вывод параметров компенсирующей подачи воздуха
            with col2:
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
                "c_psm0, кДж/(кг·К)": [results['c_psm_0']],            
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




#############################################################################################################################################################################################################################################
if scenario == 3:
    st.info("Выбран сценарий 3: приточная противодымная вентиляция в лестничную клетку надземной части здания, имеющую следующие характеристики:")
    st.text("- расположена у наружных ограждающих конструкций здания;")
    st.text("- имеет обособленный выход наружу;")
    st.text("- не сообщается с нижним надземным этажом либо сообщается с ним через тамбур-шлюз, защищенный приточной противодымной вентиляцией;")
    st.text("- поэтажные выходы в лестничную клетку выполнены через одинарную дверь.")

#---------------------------------------------------------------------

    col1, col2 = st.columns(2)
    with col1:

        # Ввод параметров воздуха
        st.subheader("1. Параметры воздуха")
        nu_a = st.number_input("Скорость ветра, м/с", value=1.3, step=0.1)
        t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
        k_alpha_ww = st.number_input("Аэродинамический коэффициент ветрового напора для наветренной стороны", value=0.50, step=0.01)
        k_alpha_w0 = st.number_input("Аэродинамический коэффициент ветрового напора для заветренной стороны", value=-0.60, step=0.01)
        t_r = st.number_input("Температура воздуха в помещении, °C", value=0, step=1)

        # Ввод параметров наружного выхода лестничной клетки
        st.subheader("2. Параметры наружного выхода лестничной клетки")
        n = st.number_input("Количество последовательно расположенных дверей наружного выхода лестничной клетки", value=1, step=1)
        xi_d = st.number_input("Коэффициент местного сопротивления дверного проема наружного выхода лестничной клетки (ξ_d=2,44)", value=2.44, step=0.01)
        xi_r = st.number_input("Коэффициент местного сопротивления тамбура наружного выхода лестничной клетки (ξr=0 - для прямого тамбура, ξr=0,99 - для прямоугольного тамбура, ξr=2,9...4,0 - для z-образного тамбура)", value=0.00, step=0.01)
        b_da = st.number_input("Ширина дверного проема наружного выхода лестничной клетки, м", value=1.00, step=0.01)
        h_da = st.number_input("Ширина дверного проема наружного выхода лестничной клетки, м", value=2.00, step=0.01)

    with col2:

        # Ввод параметров лестничной клетки
        st.subheader("3. Параметры лестничной клетки")
        z = st.number_input("Коэффициент сопротивления маршей лестничной клетки", value=1.00, step=0.01)
        xi_s = st.number_input("Коэффициент местного сопротивления лестничной клетки (ξ_s=60)", value=60, step=1)
        F_s = st.number_input("Площадь горизонтальной проекции маршей и площадок лестничной клетки, м²", value=10, step=1)

        # Ввод параметров пожара
        st.subheader("4. Параметры пожара")
        G_sm = st.number_input("Массовый расход продуктов горения в дымовом слое, кг/с", value=1.00, step=0.01)
        p = st.number_input("Фактическое количество лестничных клеток, имеющих выходы в коридор (помещение) на этаже пожара и защищаемых приточной противодымной вентиляцией", value=1, step=1)

        # Ввод параметров 2-го этажа
        st.subheader("5. Параметры 2-го этажа")
        h_2 = st.number_input("Уровень отметки пола 2-го этажа относительно уровня отметки пола 1-го этажа, м", value=2.5, step=0.1)
        h_d_2 = st.number_input("Высота дверного проема лестничной клетки на уровне 2-го этаже, м", value=2.00, step=0.01)

        # Ввод параметров вентилятора
        st.subheader("6. Параметры вентилятора")
        P_ds = st.number_input("Суммарное сопротивление присоединительных воздуховодов, Па", value=1, step=1)
        h_s_N = st.number_input("Высота лестничной клетки между уровнями нижнего и верхнего этажей, м", value=22.50, step=0.01)
        h_s_0 = st.number_input("Разность между уровнями расположения приемного устройства наружного воздуха и оголовка лестничной клетки, м", value=0.50, step=0.01)

    # Ввод параметров 3-го-N-го этажей
    st.subheader("7. Параметры 3-го-N-го этажей")
    N = st.number_input("Количество этажей", value=10, step=1)
    # Создаем редактируемую таблицу
    floors_df = pd.DataFrame({
        'h': [5.0] * (N-2),
        'D': [0] * (N-2),
        'S_da_dsm': [0.0] * (N-2),
        'b_d': [1.0] * (N-2),
        'h_d': [2.0] * (N-2),
        'R_n': [0.12] * (N-2),
        'b_w': [0.50] * (N-2),
        'h_w': [0.50] * (N-2)
    }, index=[f'Этаж {i}' for i in range(3, N+1)])

    columns = {
        'h': st.column_config.NumberColumn("h, м", format="%.2f"),
        'D': st.column_config.NumberColumn("D", format="%.0f"),
        'S_da_dsm': st.column_config.NumberColumn("S_da_dsm, м³/кг", format="%.2f"),
        'b_d': st.column_config.NumberColumn("b_d, м", format="%.2f"),
        'h_d': st.column_config.NumberColumn("h_d, м", format="%.2f"),
        'R_n': st.column_config.NumberColumn("R_n, м", format="%.2f"),
        'b_w': st.column_config.NumberColumn("b_w, м", format="%.2f"),
        'h_w': st.column_config.NumberColumn("h_w, м", format="%.2f")
    }

    edited_floor = st.data_editor(
        floors_df,
        column_config=columns,
        key='floor_editor'
    )
    
    # Собираем все параметры в единый список словарей
    floors_list = []
    for i in range(3, N + 1):
        floor = {
            'h': edited_floor.loc[f'Этаж {i}', 'h'],
            'D': edited_floor.loc[f'Этаж {i}', 'D'],
            'S_da_dsm': edited_floor.loc[f'Этаж {i}', 'S_da_dsm'],
            'b_d': edited_floor.loc[f'Этаж {i}', 'b_d'],
            'h_d': edited_floor.loc[f'Этаж {i}', 'h_d'],
            'R_n': edited_floor.loc[f'Этаж {i}', 'R_n'],
            'b_w': edited_floor.loc[f'Этаж {i}', 'b_w'],
            'h_w': edited_floor.loc[f'Этаж {i}', 'h_w'],
        }
        floors_list.append(floor)

    # Собираем все входные данные
    input_data = {
        # Параметры воздуха
        'nu_a': nu_a,
        't_a': t_a,
        'k_alpha_ww': k_alpha_ww,
        'k_alpha_w0': k_alpha_w0,
        't_r': t_r,
    
        # Параметры наружного выхода лестничной клетки
        'n': n,
        'xi_d': xi_d,
        'xi_r': xi_r,
        'b_da': b_da,
        'h_da': h_da,

        # Параметры лестничной клетки
        'z': z,
        'xi_s': xi_s,
        'F_s': F_s,
        
        # Параметры пожара
        'G_sm': G_sm,
        'p': p,
    
        # Параметры 2-го этажа
        'h_2': h_2,
        'h_d_2': h_d_2,

        # Параметры вентилятора
        'P_ds': P_ds,
        'h_s_N': h_s_N,
        'h_s_0': h_s_0,
        
        # Параметры 3-го-N-го этажей
        'floors_data': floors_list,
        'N': N
    }
    
#---------------------------------------------------------------------

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_3(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_r, кг/м³",
                    value=formatted_results.get('rho_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура воздуха в лестничной клетке, К",
                    value=formatted_results.get('T_s', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_s, кг/м³",
                    value=formatted_results.get('rho_s', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            with col2:
                # Вывод параметров 2-го этажа
                st.subheader("2. Параметры 2-го этажа")
                st.number_input(
                    label="Давление на уровне 2-го этажа лестничной клетки, Па",
                    value=formatted_results.get('P_s_2', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Площадь дверного проема наружного выхода лестничной клетки, м²",
                    value=formatted_results.get('F_da', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Массовый расход воздуха через наружный выход лестничной клетки, кг/с",
                    value=formatted_results.get('G_sa', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Расчетное количество лестничных клеток, имеющих выходы в коридор (помещение) на этаже пожара и защищаемых приточной противодымной вентиляцией",
                    value=formatted_results.get('q', 0.0),
                    disabled=True,
                    format="%.0f"
                )
                st.number_input(
                    label="Массовый расход воздуха на уровне 2-го этажа лестничной клетки, кг/с",
                    value=formatted_results.get('G_s_2', 0.0),
                    disabled=True,
                    format="%.2f"   
                )
                st.number_input(
                    label="Скорость воздуха на уровне 2-го этажа лестничной клетки, м/с",
                    value=formatted_results.get('nu_s_2', 0.0),
                    disabled=True,
                    format="%.2f"   
                )

            # Вывод параметров 2-го-N-го этажей
            st.subheader("3. Параметры 3-го-N-го этажей")

            # Создаём пустой список для хранения данных
            floor_data = []

            # Список всех обязательных параметров для проверки
            required_params = [
                'P_s', 'F_d', 'S_da_dsm', 'delta_G_sd', 'F_w_3', 'k_z', 'delta_G_sw', 'delta_G_s', 'G_s', 'nu_s'
            ]

            for i in range(3, N + 1):
                try:
                    # Создаём словарь с данными для текущего этажа
                    row_data = {
                        'P_s, Па': results.get(f'P_s_{i}', 0),
                        'F_d, м²': results.get(f'F_d_{i}', 0),
                        'S_da_dsm, м³/кг': results.get(f'S_da_dsm_{i}_new', 0),
                        'ΔG_sd, кг/с': results.get(f'delta_G_sd_{i}', 0),
                        'F_w, м²': results.get(f'F_w_{i}', 0),
                        'k_z': results.get(f'k_z_{i}', 0),
                        'ΔG_sw, кг/с': results.get(f'delta_G_sw_{i}', 0),
                        'ΔG_s, кг/с': results.get(f'delta_G_s_{i}', 0),
                        'G_s, кг/с': results.get(f'G_s_{i}', 0),
                        'ν_s, м/с': results.get(f'nu_s_{i}', 0)
                    }

                    # Проверяем, есть ли хотя бы одно ненулевое значение
                    if all(value == 0 for value in row_data.values() if isinstance(value, (int, float))):
                        continue  # Пропускаем полностью нулевой этаж

                    # Добавляем строку в список
                    floor_data.append(row_data)

                except Exception as e:
                    st.error(f"Ошибка при обработке этажа {i}: {e}")

            # Создаём итоговый DataFrame
            floor_df = pd.DataFrame(floor_data, index=[f'Этаж {i}' for i in range(3, N + 1)])
            st.dataframe(floor_df)

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

#---------------------------------------------------------------------

            # График зависимости давления
            st.subheader("Зависимость давления от этажа")

            # Создаем словарь для данных графика
            pressure_data = {
                'Этаж': [f'Этаж {i}' for i in range(2, N+1)],
                'Давление, Па': [results.get(f'P_s_{i}', np.nan) for i in range(2, N+1)]
            }

            pressure_df = pd.DataFrame(pressure_data)

            if pressure_df.isnull().values.any():
                st.warning("Не все данные для построения графика давления доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую давления
                ax.plot(
                    pressure_df['Этаж'],
                    pressure_df['Давление, Па'],
                    marker='o',
                    color='green',
                    linestyle='-',
                    label='Профиль давления'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость давления от этажа')
                ax.set_xlabel('Этаж')
                ax.set_ylabel('Давление, Па')
                ax.grid(True)
                ax.legend()
                plt.tight_layout()
    
                # Добавляем сетку и подписи
                ax.grid(axis='y', linestyle='--', alpha=0.7)
    
                # Отображаем график
                st.pyplot(fig)

            # График зависимости массового расхода
            st.subheader("Зависимость массового расхода воздуха от этажа")

            # Создаем словарь для данных графика
            mass_flow_data = {
                'Этаж': [f'Этаж {i}' for i in range(2, N+1)],
                'Массовый расход, кг/с': [results.get(f'G_s_{i}', np.nan) for i in range(2, N+1)]
            }

            mass_flow_df = pd.DataFrame(mass_flow_data)

            if mass_flow_df.isnull().values.any():
                st.warning("Не все данные для построения графика массового расхода доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую массового расхода
                ax.plot(
                    mass_flow_df['Этаж'],
                    mass_flow_df['Массовый расход, кг/с'],
                    marker='o',
                    color='blue',
                    linestyle='-',
                    label='Профиль массового расхода'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость массового расхода воздуха от этажа')
                ax.set_xlabel('Этаж')
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




#############################################################################################################################################################################################################################################
if scenario == 4:
    st.info("Выбран сценарий 4: приточная противодымная вентиляция в лестничную клетку надземной части здания, имеющую следующие характеристики:")
    st.text("- расположена у наружных ограждающих конструкций здания;")
    st.text("- имеет обособленный выход наружу;")
    st.text("- не сообщается с нижним надземным этажом либо сообщается с ним через тамбур-шлюз, защищенный приточной противодымной вентиляцией;")
    st.text("- поэтажные выходы в лестничную клетку выполнены через тамбур-шлюзы, защищенные приточной противодымной вентиляцией.")

#---------------------------------------------------------------------

    col1, col2 = st.columns(2)
    with col1:

        # Ввод параметров воздуха
        st.subheader("1. Параметры воздуха")
        nu_a = st.number_input("Скорость ветра, м/с", value=1.3, step=0.1)
        t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
        k_alpha_ww = st.number_input("Аэродинамический коэффициент ветрового напора для наветренной стороны", value=0.50, step=0.01)
        k_alpha_w0 = st.number_input("Аэродинамический коэффициент ветрового напора для заветренной стороны", value=-0.60, step=0.01)
        t_r = st.number_input("Температура воздуха в помещении, °C", value=0, step=1)

        # Ввод параметров наружного выхода лестничной клетки
        st.subheader("2. Параметры наружного выхода лестничной клетки")
        n = st.number_input("Количество последовательно расположенных дверей наружного выхода лестничной клетки", value=1, step=1)
        xi_d = st.number_input("Коэффициент местного сопротивления дверного проема наружного выхода лестничной клетки (ξ_d=2,44)", value=2.44, step=0.01)
        xi_r = st.number_input("Коэффициент местного сопротивления тамбура наружного выхода лестничной клетки (ξr=0 - для прямого тамбура, ξr=0,99 - для прямоугольного тамбура, ξr=2,9...4,0 - для z-образного тамбура)", value=0.00, step=0.01)
        b_da = st.number_input("Ширина дверного проема наружного выхода лестничной клетки, м", value=1.00, step=0.01)
        h_da = st.number_input("Ширина дверного проема наружного выхода лестничной клетки, м", value=2.00, step=0.01)

    with col2:

        # Ввод параметров лестничной клетки
        st.subheader("3. Параметры лестничной клетки")
        z = st.number_input("Коэффициент сопротивления маршей лестничной клетки", value=1.00, step=0.01)
        xi_s = st.number_input("Коэффициент местного сопротивления лестничной клетки (ξ_s=60)", value=60, step=1)
        F_s = st.number_input("Площадь горизонтальной проекции маршей и площадок лестничной клетки, м²", value=10, step=1) 

        # Ввод параметров 2-го этажа
        st.subheader("4. Параметры 2-го этажа")
        h_2 = st.number_input("Уровень отметки пола 2-го этажа относительно уровня отметки пола 1-го этажа, м", value=2.5, step=0.1)
        h_d_2 = st.number_input("Высота дверного проема лестничной клетки на уровне 2-го этажа, м", value=2.00, step=0.01)

        # Ввод параметров вентилятора
        st.subheader("5. Параметры вентилятора")
        P_ds = st.number_input("Суммарное сопротивление присоединительных воздуховодов, Па", value=1, step=1)
        h_s_N = st.number_input("Высота лестничной клетки между уровнями нижнего и верхнего этажей, м", value=22.50, step=0.01)
        h_s_0 = st.number_input("Разность между уровнями расположения приемного устройства наружного воздуха и оголовка лестничной клетки, м", value=0.50, step=0.01)

    # Ввод параметров 3-го-N-го этажей
    st.subheader("6. Параметры 3-го-N-го этажей")
    N = st.number_input("Количество этажей", value=10, step=1)
    # Создаем редактируемую таблицу
    floors_df = pd.DataFrame({
        'h': [5.0] * (N-2),
        'D': [0] * (N-2),
        'S_da_dsm': [0.0] * (N-2),
        'b_d': [1.0] * (N-2),
        'h_d': [2.0] * (N-2),
        'R_n': [0.12] * (N-2),
        'b_w': [0.50] * (N-2),
        'h_w': [0.50] * (N-2)
    }, index=[f'Этаж {i}' for i in range(3, N+1)])

    columns = {
        'h': st.column_config.NumberColumn("h, м", format="%.2f"),
        'D': st.column_config.NumberColumn("D", format="%.0f"),
        'S_da_dsm': st.column_config.NumberColumn("S_da_dsm, м³/кг", format="%.2f"),
        'b_d': st.column_config.NumberColumn("b_d, м", format="%.2f"),
        'h_d': st.column_config.NumberColumn("h_d, м", format="%.2f"),
        'R_n': st.column_config.NumberColumn("R_n, м", format="%.2f"),
        'b_w': st.column_config.NumberColumn("b_w, м", format="%.2f"),
        'h_w': st.column_config.NumberColumn("h_w, м", format="%.2f")
    }

    edited_floor = st.data_editor(
        floors_df,
        column_config=columns,
        key='floor_editor'
    )
    
    # Собираем все параметры в единый список словарей
    floors_list = []
    for i in range(3, N + 1):
        floor = {
            'h': edited_floor.loc[f'Этаж {i}', 'h'],
            'D': edited_floor.loc[f'Этаж {i}', 'D'],
            'S_da_dsm': edited_floor.loc[f'Этаж {i}', 'S_da_dsm'],
            'b_d': edited_floor.loc[f'Этаж {i}', 'b_d'],
            'h_d': edited_floor.loc[f'Этаж {i}', 'h_d'],
            'R_n': edited_floor.loc[f'Этаж {i}', 'R_n'],
            'b_w': edited_floor.loc[f'Этаж {i}', 'b_w'],
            'h_w': edited_floor.loc[f'Этаж {i}', 'h_w'],
        }
        floors_list.append(floor)

    # Собираем все входные данные
    input_data = {
        # Параметры воздуха
        'nu_a': nu_a,
        't_a': t_a,
        'k_alpha_ww': k_alpha_ww,
        'k_alpha_w0': k_alpha_w0,
        't_r': t_r,
    
        # Параметры наружного выхода лестничной клетки
        'n': n,
        'xi_d': xi_d,
        'xi_r': xi_r,
        'b_da': b_da,
        'h_da': h_da,

        # Параметры лестничной клетки
        'z': z,
        'xi_s': xi_s,
        'F_s': F_s,
        
        # Параметры 2-го этажа
        'h_2': h_2,
        'h_d_2': h_d_2,

        # Параметры вентилятора
        'P_ds': P_ds,
        'h_s_N': h_s_N,
        'h_s_0': h_s_0,
        
        # Параметры 3-го-N-го этажей
        'floors_data': floors_list,
        'N': N
    }
    
#---------------------------------------------------------------------

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_4(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_r, кг/м³",
                    value=formatted_results.get('rho_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура воздуха в лестничной клетке, К",
                    value=formatted_results.get('T_s', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_s, кг/м³",
                    value=formatted_results.get('rho_s', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            with col2:
                # Вывод параметров 2-го этажа
                st.subheader("2. Параметры 2-го этажа")
                st.number_input(
                    label="Давление на уровне 2-го этажа лестничной клетки, Па",
                    value=formatted_results.get('P_s_2', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Площадь дверного проема наружного выхода лестничной клетки, м²",
                    value=formatted_results.get('F_da', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Массовый расход воздуха через наружный выход лестничной клетки, кг/с",
                    value=formatted_results.get('G_sa', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Массовый расход воздуха на уровне 2-го этажа лестничной клетки, кг/с",
                    value=formatted_results.get('G_s_2', 0.0),
                    disabled=True,
                    format="%.2f"   
                )
                st.number_input(
                    label="Скорость воздуха на уровне 2-го этажа лестничной клетки, м/с",
                    value=formatted_results.get('nu_s_2', 0.0),
                    disabled=True,
                    format="%.2f"   
                )

            # Вывод параметров 3-го-N-го этажей
            st.subheader("3. Параметры 3-го-N-го этажей")

            # Создаём пустой список для хранения данных
            floor_data = []

            # Список всех обязательных параметров для проверки
            required_params = [
                'P_s', 'F_d', 'S_da_dsm', 'delta_G_sd', 'F_w_3', 'k_z', 'delta_G_sw', 'delta_G_s', 'G_s', 'nu_s'
            ]

            for i in range(3, N + 1):
                try:
                    # Создаём словарь с данными для текущего этажа
                    row_data = {
                        'P_s, Па': results.get(f'P_s_{i}', 0),
                        'F_d, м²': results.get(f'F_d_{i}', 0),
                        'S_da_dsm, м³/кг': results.get(f'S_da_dsm_{i}_new', 0),
                        'ΔG_sd, кг/с': results.get(f'delta_G_sd_{i}', 0),
                        'F_w, м²': results.get(f'F_w_{i}', 0),
                        'k_z': results.get(f'k_z_{i}', 0),
                        'ΔG_sw, кг/с': results.get(f'delta_G_sw_{i}', 0),
                        'ΔG_s, кг/с': results.get(f'delta_G_s_{i}', 0),
                        'G_s, кг/с': results.get(f'G_s_{i}', 0),
                        'ν_s, м/с': results.get(f'nu_s_{i}', 0)
                    }

                    # Проверяем, есть ли хотя бы одно ненулевое значение
                    if all(value == 0 for value in row_data.values() if isinstance(value, (int, float))):
                        continue  # Пропускаем полностью нулевой этаж

                    # Добавляем строку в список
                    floor_data.append(row_data)

                except Exception as e:
                    st.error(f"Ошибка при обработке этажа {i}: {e}")

            # Создаём итоговый DataFrame
            floor_df = pd.DataFrame(floor_data, index=[f'Этаж {i}' for i in range(3, N + 1)])
            st.dataframe(floor_df)

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

#---------------------------------------------------------------------

            # График зависимости давления
            st.subheader("Зависимость давления от этажа")

            # Создаем словарь для данных графика
            pressure_data = {
                'Этаж': [f'Этаж {i}' for i in range(2, N+1)],
                'Давление, Па': [results.get(f'P_s_{i}', np.nan) for i in range(2, N+1)]
            }

            pressure_df = pd.DataFrame(pressure_data)

            if pressure_df.isnull().values.any():
                st.warning("Не все данные для построения графика давления доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую давления
                ax.plot(
                    pressure_df['Этаж'],
                    pressure_df['Давление, Па'],
                    marker='o',
                    color='green',
                    linestyle='-',
                    label='Профиль давления'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость давления от этажа')
                ax.set_xlabel('Этаж')
                ax.set_ylabel('Давление, Па')
                ax.grid(True)
                ax.legend()
                plt.tight_layout()
    
                # Добавляем сетку и подписи
                ax.grid(axis='y', linestyle='--', alpha=0.7)
    
                # Отображаем график
                st.pyplot(fig)

            # График зависимости массового расхода
            st.subheader("Зависимость массового расхода воздуха от этажа")

            # Создаем словарь для данных графика
            mass_flow_data = {
                'Этаж': [f'Этаж {i}' for i in range(2, N+1)],
                'Массовый расход, кг/с': [results.get(f'G_s_{i}', np.nan) for i in range(2, N+1)]
            }

            mass_flow_df = pd.DataFrame(mass_flow_data)

            if mass_flow_df.isnull().values.any():
                st.warning("Не все данные для построения графика массового расхода доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую массового расхода
                ax.plot(
                    mass_flow_df['Этаж'],
                    mass_flow_df['Массовый расход, кг/с'],
                    marker='o',
                    color='blue',
                    linestyle='-',
                    label='Профиль массового расхода'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость массового расхода воздуха от этажа')
                ax.set_xlabel('Этаж')
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




#############################################################################################################################################################################################################################################
if scenario == 5:
    st.info("Выбран сценарий 5: приточная противодымная вентиляция в лестничную клетку надземной части здания, имеющую следующие характеристики:")
    st.text("- расположена у наружных ограждающих конструкций здания;")
    st.text("- имеет обособленный выход наружу;")
    st.text("- сообщается с нижним надземным этажом через одинарную дверь;")
    st.text("- поэтажные выходы в лестничную клетку выполнены через одинарную дверь.")

#---------------------------------------------------------------------

    col1, col2 = st.columns(2)
    with col1:

        # Ввод параметров воздуха
        st.subheader("1. Параметры воздуха")
        nu_a = st.number_input("Скорость ветра, м/с", value=1.3, step=0.1)
        t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
        k_alpha_ww = st.number_input("Аэродинамический коэффициент ветрового напора для наветренной стороны", value=0.50, step=0.01)
        k_alpha_w0 = st.number_input("Аэродинамический коэффициент ветрового напора для заветренной стороны", value=-0.60, step=0.01)
        t_r = st.number_input("Температура воздуха в помещении, °C", value=0, step=1)

        # Ввод параметров наружного выхода лестничной клетки
        st.subheader("2. Параметры наружного выхода лестничной клетки")
        n = st.number_input("Количество последовательно расположенных дверей наружного выхода лестничной клетки", value=1, step=1)
        xi_d = st.number_input("Коэффициент местного сопротивления дверного проема наружного выхода лестничной клетки (ξ_d=2,44)", value=2.44, step=0.01)
        xi_r = st.number_input("Коэффициент местного сопротивления тамбура наружного выхода лестничной клетки (ξr=0 - для прямого тамбура, ξr=0,99 - для прямоугольного тамбура, ξr=2,9...4,0 - для z-образного тамбура)", value=0.00, step=0.01)
        b_da = st.number_input("Ширина дверного проема наружного выхода лестничной клетки, м", value=1.00, step=0.01)
        h_da = st.number_input("Ширина дверного проема наружного выхода лестничной клетки, м", value=2.00, step=0.01)

    with col2:

        # Ввод параметров лестничной клетки
        st.subheader("3. Параметры лестничной клетки")
        z = st.number_input("Коэффициент сопротивления маршей лестничной клетки", value=1.00, step=0.01)
        xi_s = st.number_input("Коэффициент местного сопротивления лестничной клетки (ξ_s=60)", value=60, step=1)
        F_s = st.number_input("Площадь горизонтальной проекции маршей и площадок лестничной клетки, м²", value=10, step=1)

        # Ввод параметров пожара
        st.subheader("4. Параметры пожара")
        G_sm = st.number_input("Массовый расход продуктов горения в дымовом слое, кг/с", value=1.00, step=0.01)
        p = st.number_input("Фактическое количество лестничных клеток, имеющих выходы в коридор (помещение) на этаже пожара и защищаемых приточной противодымной вентиляцией", value=1, step=1)

        # Ввод параметров 1-го этажа
        st.subheader("5. Параметры 1-го этажа")
        h_d_1 = st.number_input("Высота дверного проема лестничной клетки на уровне 1-го этажа, м", value=2.00, step=0.01)

        # Ввод параметров вентилятора
        st.subheader("6. Параметры вентилятора")
        P_ds = st.number_input("Суммарное сопротивление присоединительных воздуховодов, Па", value=1, step=1)
        h_s_N = st.number_input("Высота лестничной клетки между уровнями нижнего и верхнего этажей, м", value=22.50, step=0.01)
        h_s_0 = st.number_input("Разность между уровнями расположения приемного устройства наружного воздуха и оголовка лестничной клетки, м", value=0.50, step=0.01)

    # Ввод параметров 2-го-N-го этажей
    st.subheader("7. Параметры 2-го-N-го этажей")
    N = st.number_input("Количество этажей", value=10, step=1)
    # Создаем редактируемую таблицу
    floors_df = pd.DataFrame({
        'h': [2.5] * (N-1),
        'D': [0] * (N-1),
        'S_da_dsm': [0.0] * (N-1),
        'b_d': [1.0] * (N-1),
        'h_d': [2.0] * (N-1),
        'R_n': [0.12] * (N-1),
        'b_w': [0.50] * (N-1),
        'h_w': [0.50] * (N-1)
    }, index=[f'Этаж {i}' for i in range(2, N+1)])

    columns = {
        'h': st.column_config.NumberColumn("h, м", format="%.2f"),
        'D': st.column_config.NumberColumn("D", format="%.0f"),
        'S_da_dsm': st.column_config.NumberColumn("S_da_dsm, м³/кг", format="%.2f"),
        'b_d': st.column_config.NumberColumn("b_d, м", format="%.2f"),
        'h_d': st.column_config.NumberColumn("h_d, м", format="%.2f"),
        'R_n': st.column_config.NumberColumn("R_n, м", format="%.2f"),
        'b_w': st.column_config.NumberColumn("b_w, м", format="%.2f"),
        'h_w': st.column_config.NumberColumn("h_w, м", format="%.2f")
    }

    edited_floor = st.data_editor(
        floors_df,
        column_config=columns,
        key='floor_editor'
    )
    
    # Собираем все параметры в единый список словарей
    floors_list = []
    for i in range(2, N + 1):
        floor = {
            'h': edited_floor.loc[f'Этаж {i}', 'h'],
            'D': edited_floor.loc[f'Этаж {i}', 'D'],
            'S_da_dsm': edited_floor.loc[f'Этаж {i}', 'S_da_dsm'],
            'b_d': edited_floor.loc[f'Этаж {i}', 'b_d'],
            'h_d': edited_floor.loc[f'Этаж {i}', 'h_d'],
            'R_n': edited_floor.loc[f'Этаж {i}', 'R_n'],
            'b_w': edited_floor.loc[f'Этаж {i}', 'b_w'],
            'h_w': edited_floor.loc[f'Этаж {i}', 'h_w'],
        }
        floors_list.append(floor)

    # Собираем все входные данные
    input_data = {
        # Параметры воздуха
        'nu_a': nu_a,
        't_a': t_a,
        'k_alpha_ww': k_alpha_ww,
        'k_alpha_w0': k_alpha_w0,
        't_r': t_r,
    
        # Параметры наружного выхода лестничной клетки
        'n': n,
        'xi_d': xi_d,
        'xi_r': xi_r,
        'b_da': b_da,
        'h_da': h_da,

        # Параметры лестничной клетки
        'z': z,
        'xi_s': xi_s,
        'F_s': F_s,
        
        # Параметры пожара
        'G_sm': G_sm,
        'p': p,
    
        # Параметры 1-го этажа
        'h_d_1': h_d_1,

        # Параметры вентилятора
        'P_ds': P_ds,
        'h_s_N': h_s_N,
        'h_s_0': h_s_0,
        
        # Параметры 2-го-N-го этажей
        'floors_data': floors_list,
        'N': N
    }
    
#---------------------------------------------------------------------

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_5(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_r, кг/м³",
                    value=formatted_results.get('rho_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура воздуха в лестничной клетке, К",
                    value=formatted_results.get('T_s', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_s, кг/м³",
                    value=formatted_results.get('rho_s', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            with col2:
                # Вывод параметров 1-го этажа
                st.subheader("2. Параметры 1-го этажа")
                st.number_input(
                    label="Давление на уровне 1-го этажа лестничной клетки, Па",
                    value=formatted_results.get('P_s_1', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Площадь дверного проема наружного выхода лестничной клетки, м²",
                    value=formatted_results.get('F_da', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Массовый расход воздуха через наружный выход лестничной клетки, кг/с",
                    value=formatted_results.get('G_sa', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Расчетное количество лестничных клеток, имеющих выходы в коридор (помещение) на этаже пожара и защищаемых приточной противодымной вентиляцией",
                    value=formatted_results.get('q', 0.0),
                    disabled=True,
                    format="%.0f"
                )
                st.number_input(
                    label="Массовый расход воздуха на уровне 1-го этажа лестничной клетки, кг/с",
                    value=formatted_results.get('G_s_1', 0.0),
                    disabled=True,
                    format="%.2f"   
                )
                st.number_input(
                    label="Скорость воздуха на уровне 1-го этажа лестничной клетки, м/с",
                    value=formatted_results.get('nu_s_1', 0.0),
                    disabled=True,
                    format="%.2f"   
                )

            # Вывод параметров 2-го-N-го этажей
            st.subheader("3. Параметры 2-го-N-го этажей")

            # Создаём пустой список для хранения данных
            floor_data = []

            # Список всех обязательных параметров для проверки
            required_params = [
                'P_s', 'F_d', 'S_da_dsm', 'delta_G_sd', 'F_w_3', 'k_z', 'delta_G_sw', 'delta_G_s', 'G_s', 'nu_s'
            ]

            for i in range(2, N + 1):
                try:
                    # Создаём словарь с данными для текущего этажа
                    row_data = {
                        'P_s, Па': results.get(f'P_s_{i}', 0),
                        'F_d, м²': results.get(f'F_d_{i}', 0),
                        'S_da_dsm, м³/кг': results.get(f'S_da_dsm_{i}_new', 0),
                        'ΔG_sd, кг/с': results.get(f'delta_G_sd_{i}', 0),
                        'F_w, м²': results.get(f'F_w_{i}', 0),
                        'k_z': results.get(f'k_z_{i}', 0),
                        'ΔG_sw, кг/с': results.get(f'delta_G_sw_{i}', 0),
                        'ΔG_s, кг/с': results.get(f'delta_G_s_{i}', 0),
                        'G_s, кг/с': results.get(f'G_s_{i}', 0),
                        'ν_s, м/с': results.get(f'nu_s_{i}', 0)
                    }

                    # Проверяем, есть ли хотя бы одно ненулевое значение
                    if all(value == 0 for value in row_data.values() if isinstance(value, (int, float))):
                        continue  # Пропускаем полностью нулевой этаж

                    # Добавляем строку в список
                    floor_data.append(row_data)

                except Exception as e:
                    st.error(f"Ошибка при обработке этажа {i}: {e}")

            # Создаём итоговый DataFrame
            floor_df = pd.DataFrame(floor_data, index=[f'Этаж {i}' for i in range(2, N + 1)])
            st.dataframe(floor_df)

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

#---------------------------------------------------------------------

            # График зависимости давления
            st.subheader("Зависимость давления от этажа")

            # Создаем словарь для данных графика
            pressure_data = {
                'Этаж': [f'Этаж {i}' for i in range(1, N+1)],
                'Давление, Па': [results.get(f'P_s_{i}', np.nan) for i in range(1, N+1)]
            }

            pressure_df = pd.DataFrame(pressure_data)

            if pressure_df.isnull().values.any():
                st.warning("Не все данные для построения графика давления доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую давления
                ax.plot(
                    pressure_df['Этаж'],
                    pressure_df['Давление, Па'],
                    marker='o',
                    color='green',
                    linestyle='-',
                    label='Профиль давления'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость давления от этажа')
                ax.set_xlabel('Этаж')
                ax.set_ylabel('Давление, Па')
                ax.grid(True)
                ax.legend()
                plt.tight_layout()
    
                # Добавляем сетку и подписи
                ax.grid(axis='y', linestyle='--', alpha=0.7)
    
                # Отображаем график
                st.pyplot(fig)

            # График зависимости массового расхода
            st.subheader("Зависимость массового расхода воздуха от этажа")

            # Создаем словарь для данных графика
            mass_flow_data = {
                'Этаж': [f'Этаж {i}' for i in range(1, N+1)],
                'Массовый расход, кг/с': [results.get(f'G_s_{i}', np.nan) for i in range(1, N+1)]
            }

            mass_flow_df = pd.DataFrame(mass_flow_data)

            if mass_flow_df.isnull().values.any():
                st.warning("Не все данные для построения графика массового расхода доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую массового расхода
                ax.plot(
                    mass_flow_df['Этаж'],
                    mass_flow_df['Массовый расход, кг/с'],
                    marker='o',
                    color='blue',
                    linestyle='-',
                    label='Профиль массового расхода'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость массового расхода воздуха от этажа')
                ax.set_xlabel('Этаж')
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




#############################################################################################################################################################################################################################################
if scenario == 6:
    st.info("Выбран сценарий 6: приточная противодымная вентиляция в лестничную клетку надземной части здания, имеющую следующие характеристики:")
    st.text("- расположена в центральном ядре здания;")
    st.text("- имеет обособленный выход наружу;")
    st.text("- не сообщается с нижним надземным этажом либо сообщается с ним через тамбур-шлюз, защищенный приточной противодымной вентиляцией;")
    st.text("- поэтажные выходы в лестничную клетку выполнены через одинарную дверь.")

#---------------------------------------------------------------------

    col1, col2 = st.columns(2)
    with col1:

        # Ввод параметров воздуха
        st.subheader("1. Параметры воздуха")
        nu_a = st.number_input("Скорость ветра, м/с", value=1.0, step=0.1)
        t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
        k_alpha_ww = st.number_input("Аэродинамический коэффициент ветрового напора для наветренной стороны", value=0.50, step=0.01)
        k_alpha_w0 = st.number_input("Аэродинамический коэффициент ветрового напора для заветренной стороны", value=-0.60, step=0.01)
        t_r = st.number_input("Температура воздуха в помещении, °C", value=0, step=1)

        # Ввод параметров наружного выхода лестничной клетки
        st.subheader("2. Параметры наружного выхода лестничной клетки")
        n = st.number_input("Количество последовательно расположенных дверей наружного выхода лестничной клетки", value=1, step=1)
        xi_d = st.number_input("Коэффициент местного сопротивления дверного проема наружного выхода лестничной клетки (ξ_d=2,44)", value=2.44, step=0.01)
        xi_r = st.number_input("Коэффициент местного сопротивления тамбура наружного выхода лестничной клетки (ξr=0 - для прямого тамбура, ξr=0,99 - для прямоугольного тамбура, ξr=2,9...4,0 - для z-образного тамбура)", value=0.00, step=0.01)
        b_da = st.number_input("Ширина дверного проема наружного выхода лестничной клетки, м", value=1.00, step=0.01)
        h_da = st.number_input("Ширина дверного проема наружного выхода лестничной клетки, м", value=2.00, step=0.01)

    with col2:

        # Ввод параметров лестничной клетки
        st.subheader("3. Параметры лестничной клетки")
        z = st.number_input("Коэффициент сопротивления маршей лестничной клетки", value=1.00, step=0.01)
        xi_s = st.number_input("Коэффициент местного сопротивления лестничной клетки (ξ_s=60)", value=60, step=1)
        F_s = st.number_input("Площадь горизонтальной проекции маршей и площадок лестничной клетки, м²", value=10, step=1)

        # Ввод параметров пожара
        st.subheader("4. Параметры пожара")
        G_sm = st.number_input("Массовый расход продуктов горения в дымовом слое, кг/с", value=1.00, step=0.01)
        p = st.number_input("Фактическое количество лестничных клеток, имеющих выходы в коридор (помещение) на этаже пожара и защищаемых приточной противодымной вентиляцией", value=1, step=1)

        # Ввод параметров 2-го этажа
        st.subheader("5. Параметры 2-го этажа")
        h_2 = st.number_input("Уровень отметки пола 2-го этажа относительно уровня отметки пола 1-го этажа, м", value=2.5, step=0.1)
        h_d_2 = st.number_input("Высота дверного проема лестничной клетки на уровне 2-го этаже, м", value=2.00, step=0.01)

        # Ввод параметров вентилятора
        st.subheader("6. Параметры вентилятора")
        P_ds = st.number_input("Суммарное сопротивление присоединительных воздуховодов, Па", value=1, step=1)
        h_s_N = st.number_input("Высота лестничной клетки между уровнями нижнего и верхнего этажей, м", value=22.50, step=0.01)
        h_s_0 = st.number_input("Разность между уровнями расположения приемного устройства наружного воздуха и оголовка лестничной клетки, м", value=0.50, step=0.01)

    # Ввод параметров 3-го-N-го этажей
    st.subheader("7. Параметры 3-го-N-го этажей")
    N = st.number_input("Количество этажей", value=10, step=1)
    # Создаем редактируемую таблицу
    floors_df = pd.DataFrame({
        'h': [5.0] * (N-2),
        'D': [0] * (N-2),
        'S_da_dsm': [0.0] * (N-2),
        'b_d': [1.0] * (N-2),
        'h_d': [2.0] * (N-2)
    }, index=[f'Этаж {i}' for i in range(3, N+1)])

    columns = {
        'h': st.column_config.NumberColumn("h, м", format="%.2f"),
        'D': st.column_config.NumberColumn("D", format="%.0f"),
        'S_da_dsm': st.column_config.NumberColumn("S_da_dsm, м³/кг", format="%.2f"),
        'b_d': st.column_config.NumberColumn("b_d, м", format="%.2f"),
        'h_d': st.column_config.NumberColumn("h_d, м", format="%.2f")
    }

    edited_floor = st.data_editor(
        floors_df,
        column_config=columns,
        key='floor_editor'
    )
    
    # Собираем все параметры в единый список словарей
    floors_list = []
    for i in range(3, N + 1):
        floor = {
            'h': edited_floor.loc[f'Этаж {i}', 'h'],
            'D': edited_floor.loc[f'Этаж {i}', 'D'],
            'S_da_dsm': edited_floor.loc[f'Этаж {i}', 'S_da_dsm'],
            'b_d': edited_floor.loc[f'Этаж {i}', 'b_d'],
            'h_d': edited_floor.loc[f'Этаж {i}', 'h_d']
        }
        floors_list.append(floor)

    # Собираем все входные данные
    input_data = {
        # Параметры воздуха
        'nu_a': nu_a,
        't_a': t_a,
        'k_alpha_ww': k_alpha_ww,
        'k_alpha_w0': k_alpha_w0,
        't_r': t_r,
    
        # Параметры наружного выхода лестничной клетки
        'n': n,
        'xi_d': xi_d,
        'xi_r': xi_r,
        'b_da': b_da,
        'h_da': h_da,

        # Параметры лестничной клетки
        'z': z,
        'xi_s': xi_s,
        'F_s': F_s,
        
        # Параметры пожара
        'G_sm': G_sm,
        'p': p,
    
        # Параметры 2-го этажа
        'h_2': h_2,
        'h_d_2': h_d_2,

        # Параметры вентилятора
        'P_ds': P_ds,
        'h_s_N': h_s_N,
        'h_s_0': h_s_0,
        
        # Параметры 3-го-N-го этажей
        'floors_data': floors_list,
        'N': N
    }
    
#---------------------------------------------------------------------

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_6(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_r, кг/м³",
                    value=formatted_results.get('rho_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура воздуха в лестничной клетке, К",
                    value=formatted_results.get('T_s', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_s, кг/м³",
                    value=formatted_results.get('rho_s', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            with col2:
                # Вывод параметров 2-го этажа
                st.subheader("2. Параметры 2-го этажа")
                st.number_input(
                    label="Давление на уровне 2-го этажа лестничной клетки, Па",
                    value=formatted_results.get('P_s_2', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Площадь дверного проема наружного выхода лестничной клетки, м²",
                    value=formatted_results.get('F_da', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Массовый расход воздуха через наружный выход лестничной клетки, кг/с",
                    value=formatted_results.get('G_sa', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Расчетное количество лестничных клеток, имеющих выходы в коридор (помещение) на этаже пожара и защищаемых приточной противодымной вентиляцией",
                    value=formatted_results.get('q', 0.0),
                    disabled=True,
                    format="%.0f"
                )
                st.number_input(
                    label="Массовый расход воздуха на уровне 2-го этажа лестничной клетки, кг/с",
                    value=formatted_results.get('G_s_2', 0.0),
                    disabled=True,
                    format="%.2f"   
                )
                st.number_input(
                    label="Скорость воздуха на уровне 2-го этажа лестничной клетки, м/с",
                    value=formatted_results.get('nu_s_2', 0.0),
                    disabled=True,
                    format="%.2f"   
                )

            # Вывод параметров 2-го-N-го этажей
            st.subheader("3. Параметры 3-го-N-го этажей")

            # Создаём пустой список для хранения данных
            floor_data = []

            # Список всех обязательных параметров для проверки
            required_params = [
                'P_s', 'F_d', 'S_da_dsm', 'delta_G_sd', 'G_s', 'nu_s'
            ]

            for i in range(3, N + 1):
                try:
                    # Создаём словарь с данными для текущего этажа
                    row_data = {
                        'P_s, Па': results.get(f'P_s_{i}', 0),
                        'F_d, м²': results.get(f'F_d_{i}', 0),
                        'S_da_dsm, м³/кг': results.get(f'S_da_dsm_{i}_new', 0),
                        'ΔG_sd, кг/с': results.get(f'delta_G_sd_{i}', 0),
                        'ΔG_s, кг/с': results.get(f'delta_G_s_{i}', 0),
                        'G_s, кг/с': results.get(f'G_s_{i}', 0),
                        'ν_s, м/с': results.get(f'nu_s_{i}', 0)
                    }

                    # Проверяем, есть ли хотя бы одно ненулевое значение
                    if all(value == 0 for value in row_data.values() if isinstance(value, (int, float))):
                        continue  # Пропускаем полностью нулевой этаж

                    # Добавляем строку в список
                    floor_data.append(row_data)

                except Exception as e:
                    st.error(f"Ошибка при обработке этажа {i}: {e}")

            # Создаём итоговый DataFrame
            floor_df = pd.DataFrame(floor_data, index=[f'Этаж {i}' for i in range(3, N + 1)])
            st.dataframe(floor_df)

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

#---------------------------------------------------------------------

            # График зависимости давления
            st.subheader("Зависимость давления от этажа")

            # Создаем словарь для данных графика
            pressure_data = {
                'Этаж': [f'Этаж {i}' for i in range(2, N+1)],
                'Давление, Па': [results.get(f'P_s_{i}', np.nan) for i in range(2, N+1)]
            }

            pressure_df = pd.DataFrame(pressure_data)

            if pressure_df.isnull().values.any():
                st.warning("Не все данные для построения графика давления доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую давления
                ax.plot(
                    pressure_df['Этаж'],
                    pressure_df['Давление, Па'],
                    marker='o',
                    color='green',
                    linestyle='-',
                    label='Профиль давления'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость давления от этажа')
                ax.set_xlabel('Этаж')
                ax.set_ylabel('Давление, Па')
                ax.grid(True)
                ax.legend()
                plt.tight_layout()
    
                # Добавляем сетку и подписи
                ax.grid(axis='y', linestyle='--', alpha=0.7)
    
                # Отображаем график
                st.pyplot(fig)

            # График зависимости массового расхода
            st.subheader("Зависимость массового расхода воздуха от этажа")

            # Создаем словарь для данных графика
            mass_flow_data = {
                'Этаж': [f'Этаж {i}' for i in range(2, N+1)],
                'Массовый расход, кг/с': [results.get(f'G_s_{i}', np.nan) for i in range(2, N+1)]
            }

            mass_flow_df = pd.DataFrame(mass_flow_data)

            if mass_flow_df.isnull().values.any():
                st.warning("Не все данные для построения графика массового расхода доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую массового расхода
                ax.plot(
                    mass_flow_df['Этаж'],
                    mass_flow_df['Массовый расход, кг/с'],
                    marker='o',
                    color='blue',
                    linestyle='-',
                    label='Профиль массового расхода'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость массового расхода воздуха от этажа')
                ax.set_xlabel('Этаж')
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




#############################################################################################################################################################################################################################################
if scenario == 7:
    st.info("Выбран сценарий 7: приточная противодымная вентиляция в лестничную клетку надземной части здания, имеющую следующие характеристики:")
    st.text("- расположена в центральном ядре здания;")
    st.text("- не имеет обособленный выход наружу;")
    st.text("- сообщается с нижним надземным этажом через тамбур-шлюз, защищенный приточной противодымной вентиляцией;")
    st.text("- поэтажные выходы в лестничную клетку выполнены через одинарную дверь.")

#---------------------------------------------------------------------

    col1, col2 = st.columns(2)
    with col1:
        # Ввод параметров воздуха
        st.subheader("1. Параметры воздуха")
        t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
        t_r = st.number_input("Температура воздуха в помещении, °C", value=0, step=1)

        # Ввод параметров лестничной клетки
        st.subheader("3. Параметры лестничной клетки")
        xi_s = st.number_input("Коэффициент местного сопротивления лестничной клетки (ξ_s=60)", value=60, step=1)
        F_s = st.number_input("Площадь горизонтальной проекции маршей и площадок лестничной клетки, м²", value=10, step=1)

        # Ввод параметров пожара
        st.subheader("4. Параметры пожара")
        G_sm = st.number_input("Массовый расход продуктов горения в дымовом слое, кг/с", value=1.00, step=0.01)
        p = st.number_input("Фактическое количество лестничных клеток, имеющих выходы в коридор (помещение) на этаже пожара и защищаемых приточной противодымной вентиляцией", value=1, step=1)

    with col2:
        # Ввод параметров 2-го этажа
        st.subheader("5. Параметры 2-го этажа")
        h_2 = st.number_input("Уровень отметки пола 2-го этажа относительно уровня отметки пола 1-го этажа, м", value=2.5, step=0.1)
        h_d_2 = st.number_input("Высота дверного проема лестничной клетки на уровне 2-го этаже, м", value=2.00, step=0.01)

        # Ввод параметров вентилятора
        st.subheader("6. Параметры вентилятора")
        P_ds = st.number_input("Суммарное сопротивление присоединительных воздуховодов, Па", value=1, step=1)
        h_s_N = st.number_input("Высота лестничной клетки между уровнями нижнего и верхнего этажей, м", value=22.50, step=0.01)
        h_s_0 = st.number_input("Разность между уровнями расположения приемного устройства наружного воздуха и оголовка лестничной клетки, м", value=0.50, step=0.01)

    # Ввод параметров 3-го-N-го этажей
    st.subheader("7. Параметры 3-го-N-го этажей")
    N = st.number_input("Количество этажей", value=10, step=1)
    # Создаем редактируемую таблицу
    floors_df = pd.DataFrame({
        'h': [5.0] * (N-2),
        'D': [0] * (N-2),
        'S_da_dsm': [0.0] * (N-2),
        'b_d': [1.0] * (N-2),
        'h_d': [2.0] * (N-2)
    }, index=[f'Этаж {i}' for i in range(3, N+1)])

    columns = {
        'h': st.column_config.NumberColumn("h, м", format="%.2f"),
        'D': st.column_config.NumberColumn("D", format="%.0f"),
        'S_da_dsm': st.column_config.NumberColumn("S_da_dsm, м³/кг", format="%.2f"),
        'b_d': st.column_config.NumberColumn("b_d, м", format="%.2f"),
        'h_d': st.column_config.NumberColumn("h_d, м", format="%.2f")
    }

    edited_floor = st.data_editor(
        floors_df,
        column_config=columns,
        key='floor_editor'
    )
    
    # Собираем все параметры в единый список словарей
    floors_list = []
    for i in range(3, N + 1):
        floor = {
            'h': edited_floor.loc[f'Этаж {i}', 'h'],
            'D': edited_floor.loc[f'Этаж {i}', 'D'],
            'S_da_dsm': edited_floor.loc[f'Этаж {i}', 'S_da_dsm'],
            'b_d': edited_floor.loc[f'Этаж {i}', 'b_d'],
            'h_d': edited_floor.loc[f'Этаж {i}', 'h_d']
        }
        floors_list.append(floor)

    # Собираем все входные данные
    input_data = {
        # Параметры воздуха
        't_a': t_a,
        't_r': t_r,
    
        # Параметры лестничной клетки
        'xi_s': xi_s,
        'F_s': F_s,
        
        # Параметры пожара
        'G_sm': G_sm,
        'p': p,
    
        # Параметры 2-го этажа
        'h_2': h_2,
        'h_d_2': h_d_2,

        # Параметры вентилятора
        'P_ds': P_ds,
        'h_s_N': h_s_N,
        'h_s_0': h_s_0,
        
        # Параметры 3-го-N-го этажей
        'floors_data': floors_list,
        'N': N
    }
    
#---------------------------------------------------------------------

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_7(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_r, кг/м³",
                    value=formatted_results.get('rho_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура воздуха в лестничной клетке, К",
                    value=formatted_results.get('T_s', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_s, кг/м³",
                    value=formatted_results.get('rho_s', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            with col2:
                # Вывод параметров 2-го этажа
                st.subheader("2. Параметры 2-го этажа")
                st.number_input(
                    label="Давление на уровне 2-го этажа лестничной клетки, Па",
                    value=formatted_results.get('P_s_2', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Расчетное количество лестничных клеток, имеющих выходы в коридор (помещение) на этаже пожара и защищаемых приточной противодымной вентиляцией",
                    value=formatted_results.get('q', 0.0),
                    disabled=True,
                    format="%.0f"
                )
                st.number_input(
                    label="Массовый расход воздуха на уровне 2-го этажа лестничной клетки, кг/с",
                    value=formatted_results.get('G_s_2', 0.0),
                    disabled=True,
                    format="%.2f"   
                )
                st.number_input(
                    label="Скорость воздуха на уровне 2-го этажа лестничной клетки, м/с",
                    value=formatted_results.get('nu_s_2', 0.0),
                    disabled=True,
                    format="%.2f"   
                )

            # Вывод параметров 2-го-N-го этажей
            st.subheader("3. Параметры 3-го-N-го этажей")

            # Создаём пустой список для хранения данных
            floor_data = []

            # Список всех обязательных параметров для проверки
            required_params = [
                'P_s', 'F_d', 'S_da_dsm', 'delta_G_sd', 'G_s', 'nu_s'
            ]

            for i in range(3, N + 1):
                try:
                    # Создаём словарь с данными для текущего этажа
                    row_data = {
                        'P_s, Па': results.get(f'P_s_{i}', 0),
                        'F_d, м²': results.get(f'F_d_{i}', 0),
                        'S_da_dsm, м³/кг': results.get(f'S_da_dsm_{i}_new', 0),
                        'ΔG_sd, кг/с': results.get(f'delta_G_sd_{i}', 0),
                        'ΔG_s, кг/с': results.get(f'delta_G_s_{i}', 0),
                        'G_s, кг/с': results.get(f'G_s_{i}', 0),
                        'ν_s, м/с': results.get(f'nu_s_{i}', 0)
                    }

                    # Проверяем, есть ли хотя бы одно ненулевое значение
                    if all(value == 0 for value in row_data.values() if isinstance(value, (int, float))):
                        continue  # Пропускаем полностью нулевой этаж

                    # Добавляем строку в список
                    floor_data.append(row_data)

                except Exception as e:
                    st.error(f"Ошибка при обработке этажа {i}: {e}")

            # Создаём итоговый DataFrame
            floor_df = pd.DataFrame(floor_data, index=[f'Этаж {i}' for i in range(3, N + 1)])
            st.dataframe(floor_df)

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

#---------------------------------------------------------------------

            # График зависимости давления
            st.subheader("Зависимость давления от этажа")

            # Создаем словарь для данных графика
            pressure_data = {
                'Этаж': [f'Этаж {i}' for i in range(2, N+1)],
                'Давление, Па': [results.get(f'P_s_{i}', np.nan) for i in range(2, N+1)]
            }

            pressure_df = pd.DataFrame(pressure_data)

            if pressure_df.isnull().values.any():
                st.warning("Не все данные для построения графика давления доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую давления
                ax.plot(
                    pressure_df['Этаж'],
                    pressure_df['Давление, Па'],
                    marker='o',
                    color='green',
                    linestyle='-',
                    label='Профиль давления'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость давления от этажа')
                ax.set_xlabel('Этаж')
                ax.set_ylabel('Давление, Па')
                ax.grid(True)
                ax.legend()
                plt.tight_layout()
    
                # Добавляем сетку и подписи
                ax.grid(axis='y', linestyle='--', alpha=0.7)
    
                # Отображаем график
                st.pyplot(fig)

            # График зависимости массового расхода
            st.subheader("Зависимость массового расхода воздуха от этажа")

            # Создаем словарь для данных графика
            mass_flow_data = {
                'Этаж': [f'Этаж {i}' for i in range(2, N+1)],
                'Массовый расход, кг/с': [results.get(f'G_s_{i}', np.nan) for i in range(2, N+1)]
            }

            mass_flow_df = pd.DataFrame(mass_flow_data)

            if mass_flow_df.isnull().values.any():
                st.warning("Не все данные для построения графика массового расхода доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую массового расхода
                ax.plot(
                    mass_flow_df['Этаж'],
                    mass_flow_df['Массовый расход, кг/с'],
                    marker='o',
                    color='blue',
                    linestyle='-',
                    label='Профиль массового расхода'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость массового расхода воздуха от этажа')
                ax.set_xlabel('Этаж')
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




#############################################################################################################################################################################################################################################
if scenario == 8:
    st.info("Выбран сценарий 8: приточная противодымная вентиляция в лестничную клетку подземной части здания, имеющую следующие характеристики:")
    st.text("- имеет обособленный выход наружу;")
    st.text("- не сообщается с нижним надземным этажом;")
    st.text("- поэтажные выходы в лестничную клетку выполнены через одинарную дверь.")

#---------------------------------------------------------------------

    col1, col2 = st.columns(2)
    with col1:

        # Ввод параметров воздуха
        st.subheader("1. Параметры воздуха")
        nu_a = st.number_input("Скорость ветра, м/с", value=1.0, step=0.1)
        t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
        k_alpha_ww = st.number_input("Аэродинамический коэффициент ветрового напора для наветренной стороны", value=0.50, step=0.01)
        k_alpha_w0 = st.number_input("Аэродинамический коэффициент ветрового напора для заветренной стороны", value=-0.60, step=0.01)
        t_r = st.number_input("Температура воздуха в помещении, °C", value=0, step=1)

        # Ввод параметров наружного выхода лестничной клетки
        st.subheader("2. Параметры наружного выхода лестничной клетки")
        n = st.number_input("Количество последовательно расположенных дверей наружного выхода лестничной клетки", value=1, step=1)
        xi_d = st.number_input("Коэффициент местного сопротивления дверного проема наружного выхода лестничной клетки (ξ_d=2,44)", value=2.44, step=0.01)
        xi_r = st.number_input("Коэффициент местного сопротивления тамбура наружного выхода лестничной клетки (ξr=0 - для прямого тамбура, ξr=0,99 - для прямоугольного тамбура, ξr=2,9...4,0 - для z-образного тамбура)", value=0.00, step=0.01)
        b_da = st.number_input("Ширина дверного проема наружного выхода лестничной клетки, м", value=1.00, step=0.01)
        h_da = st.number_input("Ширина дверного проема наружного выхода лестничной клетки, м", value=2.00, step=0.01)

    with col2:

        # Ввод параметров лестничной клетки
        st.subheader("3. Параметры лестничной клетки")
        z = st.number_input("Коэффициент сопротивления маршей лестничной клетки", value=1.00, step=0.01)
        xi_s = st.number_input("Коэффициент местного сопротивления лестничной клетки (ξ_s=60)", value=60, step=1)
        F_s = st.number_input("Площадь горизонтальной проекции маршей и площадок лестничной клетки, м²", value=10, step=1)  

        # Ввод параметров пожара
        st.subheader("4. Параметры пожара")
        G_sm = st.number_input("Массовый расход продуктов горения в дымовом слое, кг/с", value=1.00, step=0.01)
        p = st.number_input("Фактическое количество лестничных клеток, имеющих выходы в коридор (помещение) на этаже пожара и защищаемых приточной противодымной вентиляцией", value=1, step=1)

        # Ввод параметров (-1)-го этажа
        st.subheader("5. Параметры (-1)-го этажа")
        h_minus_1 = st.number_input("Уровень отметки пола (-1)-го этажа относительно уровня отметки пола 1-го этажа, м", value=-2.5, step=0.1)
        h_d_minus_1 = st.number_input("Высота дверного проема лестничной клетки на уровне (-1)-го этаже, м", value=2.00, step=0.01)

        # Ввод параметров вентилятора
        st.subheader("6. Параметры вентилятора")
        P_ds = st.number_input("Суммарное сопротивление присоединительных воздуховодов, Па", value=1, step=1)
        h_s_N = st.number_input("Высота лестничной клетки между уровнями нижнего и верхнего этажей, м", value=10.00, step=0.01)
        h_s_0 = st.number_input("Разность между уровнями расположения приемного устройства наружного воздуха и оголовка лестничной клетки, м", value=0.50, step=0.01)

    # Ввод параметров (-2)-го-(-N)-го этажей
    st.subheader("7. Параметры (-2)-го-(-N)-го этажей")
    N = st.number_input("Количество этажей", value=5, step=1)
    h_minus_N = st.number_input("Уровень отметки пола нижнего подземного этажа, м", value=-12.5, step=0.1)

    # Создаем редактируемую таблицу
    floors_df = pd.DataFrame({
        'h': [-5.0] * (N-1),
        'D': [0] * (N-1),
        'S_da_dsm': [0.0] * (N-1),
        'b_d': [1.0] * (N-1),
        'h_d': [2.0] * (N-1)
    }, index=[f'Этаж -{i}' for i in range(2, N+1)])

    columns = {
        'h': st.column_config.NumberColumn("h, м", format="%.2f"),
        'D': st.column_config.NumberColumn("D", format="%.0f"),
        'S_da_dsm': st.column_config.NumberColumn("S_da_dsm, м³/кг", format="%.2f"),
        'b_d': st.column_config.NumberColumn("b_d, м", format="%.2f"),
        'h_d': st.column_config.NumberColumn("h_d, м", format="%.2f")
    }

    edited_floor = st.data_editor(
        floors_df,
        column_config=columns,
        key='floor_editor'
    )
    
    # Собираем все параметры в единый список словарей
    floors_list = []
    for i in range(2, N + 1):
        floor = {
            'h': edited_floor.loc[f'Этаж -{i}', 'h'],
            'D': edited_floor.loc[f'Этаж -{i}', 'D'],
            'S_da_dsm': edited_floor.loc[f'Этаж -{i}', 'S_da_dsm'],
            'b_d': edited_floor.loc[f'Этаж -{i}', 'b_d'],
            'h_d': edited_floor.loc[f'Этаж -{i}', 'h_d']
        }
        floors_list.append(floor)

    # Собираем все входные данные
    input_data = {
        # Параметры воздуха
        'nu_a': nu_a,
        't_a': t_a,
        'k_alpha_ww': k_alpha_ww,
        'k_alpha_w0': k_alpha_w0,
        't_r': t_r,
    
        # Параметры наружного выхода лестничной клетки
        'n': n,
        'xi_d': xi_d,
        'xi_r': xi_r,
        'b_da': b_da,
        'h_da': h_da,

        # Параметры лестничной клетки
        'z': z,
        'xi_s': xi_s,
        'F_s': F_s,
        
        # Параметры пожара
        'G_sm': G_sm,
        'p': p,
    
        # Параметры (-1)-го этажа
        'h_minus_1': h_minus_1,
        'h_d_minus_1': h_d_minus_1,

        # Параметры вентилятора
        'P_ds': P_ds,
        'h_s_N': h_s_N,
        'h_s_0': h_s_0,
        
        # Параметры 3-го-N-го этажей
        'floors_data': floors_list,
        'N': N,
        'h_minus_N': h_minus_N
    }
    
#---------------------------------------------------------------------

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_8(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_r, кг/м³",
                    value=formatted_results.get('rho_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура воздуха в лестничной клетке, К",
                    value=formatted_results.get('T_s', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_s, кг/м³",
                    value=formatted_results.get('rho_s', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            with col2:
                # Вывод параметров (-1)-го этажа
                st.subheader("2. Параметры (-1)-го этажа")
                st.number_input(
                    label="Давление на уровне (-1)-го этажа лестничной клетки, Па",
                    value=formatted_results.get('P_s_minus_1', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Площадь дверного проема наружного выхода лестничной клетки, м²",
                    value=formatted_results.get('F_da', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Массовый расход воздуха через наружный выход лестничной клетки, кг/с",
                    value=formatted_results.get('G_sa', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Расчетное количество лестничных клеток, имеющих выходы в коридор (помещение) на этаже пожара и защищаемых приточной противодымной вентиляцией",
                    value=formatted_results.get('q', 0.0),
                    disabled=True,
                    format="%.0f"
                )
                st.number_input(
                    label="Массовый расход воздуха на уровне (-1)-го этажа лестничной клетки, кг/с",
                    value=formatted_results.get('G_s_minus_1', 0.0),
                    disabled=True,
                    format="%.2f"   
                )
                st.number_input(
                    label="Скорость воздуха на уровне (-1)-го этажа лестничной клетки, м/с",
                    value=formatted_results.get('nu_s_minus_1', 0.0),
                    disabled=True,
                    format="%.2f"   
                )

            # Вывод параметров (-2)-го-(-N)-го этажей
            st.subheader("3. Параметры (-2)-го-(-N)-го этажей")

            # Создаём пустой список для хранения данных
            floor_data = []

            # Список всех обязательных параметров для проверки
            required_params = [
                'P_s_minus', 'F_d_minus', 'S_da_dsm_minus', 'delta_G_sd_minus', 'G_s_minus', 'nu_s_minus'
            ]

            for i in range(2, N + 1):
                try:
                    # Создаём словарь с данными для текущего этажа
                    row_data = {
                        'P_s, Па': results.get(f'P_s_minus_{i}', 0),
                        'F_d, м²': results.get(f'F_d_minus_{i}', 0),
                        'S_da_dsm, м³/кг': results.get(f'S_da_dsm_minus_{i}_new', 0),
                        'ΔG_sd, кг/с': results.get(f'delta_G_sd_minus_{i}', 0),
                        'G_s, кг/с': results.get(f'G_s_minus_{i}', 0),
                        'ν_s, м/с': results.get(f'nu_s_minus_{i}', 0)
                    }

                    # Проверяем, есть ли хотя бы одно ненулевое значение
                    if all(value == 0 for value in row_data.values() if isinstance(value, (int, float))):
                        continue  # Пропускаем полностью нулевой этаж

                    # Добавляем строку в список
                    floor_data.append(row_data)

                except Exception as e:
                    st.error(f"Ошибка при обработке этажа {i}: {e}")

            # Создаём итоговый DataFrame
            floor_df = pd.DataFrame(floor_data, index=[f'Этаж -{i}' for i in range(2, N + 1)])
            st.dataframe(floor_df)

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

#---------------------------------------------------------------------

            # График зависимости давления
            st.subheader("Зависимость давления от этажа")

            # Создаем словарь для данных графика
            pressure_data = {
                'Этаж': [f'Этаж -{i}' for i in range(1, N+1)],
                'Давление, Па': [results.get(f'P_s_minus_{i}', np.nan) for i in range(1, N+1)]
            }

            pressure_df = pd.DataFrame(pressure_data)

            if pressure_df.isnull().values.any():
                st.warning("Не все данные для построения графика давления доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую давления
                ax.plot(
                    pressure_df['Этаж'],
                    pressure_df['Давление, Па'],
                    marker='o',
                    color='green',
                    linestyle='-',
                    label='Профиль давления'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость давления от этажа')
                ax.set_xlabel('Этаж')
                ax.set_ylabel('Давление, Па')
                ax.grid(True)
                ax.legend()
                plt.tight_layout()
    
                # Добавляем сетку и подписи
                ax.grid(axis='y', linestyle='--', alpha=0.7)
    
                # Отображаем график
                st.pyplot(fig)

            # График зависимости массового расхода
            st.subheader("Зависимость массового расхода воздуха от этажа")

            # Создаем словарь для данных графика
            mass_flow_data = {
                'Этаж': [f'Этаж -{i}' for i in range(1, N+1)],
                'Массовый расход, кг/с': [results.get(f'G_s_minus_{i}', np.nan) for i in range(1, N+1)]
            }

            mass_flow_df = pd.DataFrame(mass_flow_data)

            if mass_flow_df.isnull().values.any():
                st.warning("Не все данные для построения графика массового расхода доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую массового расхода
                ax.plot(
                    mass_flow_df['Этаж'],
                    mass_flow_df['Массовый расход, кг/с'],
                    marker='o',
                    color='blue',
                    linestyle='-',
                    label='Профиль массового расхода'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость массового расхода воздуха от этажа')
                ax.set_xlabel('Этаж')
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





#############################################################################################################################################################################################################################################
if scenario == 9:
    st.info("Выбран сценарий 9: приточная противодымная вентиляция в лифтовую шахту, имеющую следующие характеристики:")
    st.text("- расположена в центральном ядре здания;")
    st.text("- остановки лифта только на надземных этажах;")
    st.text("- имеет выгороженные лифтовые холлы на каждом этаже, кроме нижнего.")

#---------------------------------------------------------------------

    col1, col2 = st.columns(2)
    with col1:

        # Ввод параметров воздуха
        st.subheader("1. Параметры воздуха")
        t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
        t_r = st.number_input("Температура воздуха в помещении, °C", value=0, step=1)

        # Ввод параметров лифтовой шахты
        st.subheader("2. Параметры лифтовой шахты")
        F_lc = st.number_input("Площадь поперечного сечения кабины лифта, м²", value=1.0, step=0.1)                
        F_ls = st.number_input("Площадь поперечного сечения лифтовой шахты, м²", value=1.5, step=0.1)

        # Ввод параметров 1-го этажа
        st.subheader("3. Параметры 1-го этажа")
        n_1 = st.number_input("Количество дверей лифтовой шахты на уровне 1-го этажа", value=1, step=1)
        xi_l_1 = st.number_input("Коэффициент местного сопротивления узла «кабина-шахта» при открытых дверях кабины и шахты на уровне 1-го этажа (0 - нет данных)", value=0.0, step=0.1)        
        b_dl_1 = st.number_input("Ширина дверей лифтовой шахты на уровне 1-го этажа, м", value=1.00, step=0.01)
        h_dl_1 = st.number_input("Высота дверей лифтовой шахты на уровне 1-го этажа, м", value=2.00, step=0.01)

    with col2:
        # Ввод параметров вентилятора
        st.subheader("4. Параметры вентилятора")
        P_dl = st.number_input("Суммарное сопротивление присоединительных воздуховодов, Па", value=1, step=1)
        h_l_N = st.number_input("Высота лифтовой шахты между уровнями нижнего и верхнего этажей, м", value=22.50, step=0.01)
        h_l_0 = st.number_input("Разность между уровнями расположения приемного устройства наружного воздуха и оголовка лифтовой шахты, м", value=0.50, step=0.01)

    # Ввод параметров 2-го-N-го этажей
    st.subheader("4. Параметры 2-го-N-го этажей")
    N = st.number_input("Количество этажей", value=10, step=1)
    # Создаем редактируемую таблицу
    floors_df = pd.DataFrame({
        'h': [2.5] * (N-1),
        'S_dl': [0] * (N-1),
        'n': [1.0] * (N-1),
        'b_dl': [1.0] * (N-1),
        'h_dl': [2.0] * (N-1),
        'S_dr': [0] * (N-1),
        'm': [1.0] * (N-1),
        'b_dr': [1.0] * (N-1),
        'h_dr': [2.0] * (N-1),
    }, index=[f'Этаж {i}' for i in range(2, N+1)])

    columns = {
        'h': st.column_config.NumberColumn("h, м", format="%.2f"),
        'S_dl': st.column_config.NumberColumn("S_dl, м³/кг", format="%.0f"),
        'n': st.column_config.NumberColumn("n", format="%.0f"),
        'b_dl': st.column_config.NumberColumn("b_dl, м", format="%.2f"),
        'h_dl': st.column_config.NumberColumn("h_dl, м", format="%.2f"),
        'S_dr': st.column_config.NumberColumn("S_dr, м³/кг", format="%.0f"),
        'm': st.column_config.NumberColumn("m", format="%.0f"),
        'b_dr': st.column_config.NumberColumn("b_dr, м", format="%.2f"),
        'h_dr': st.column_config.NumberColumn("h_dr, м", format="%.2f")
    }

    edited_floor = st.data_editor(
        floors_df,
        column_config=columns,
        key='floor_editor'
    )

    # Извлекаем параметры для 2-го этажа из отредактированной таблицы
    h_2 = edited_floor.loc['Этаж 2', 'h']
    h_dl_2 = edited_floor.loc['Этаж 2', 'h_dl']
    
    # Собираем все параметры в единый список словарей
    floors_list = []
    for i in range(2, N + 1):
        floor = {
            'h': edited_floor.loc[f'Этаж {i}', 'h'],
            'S_dl': edited_floor.loc[f'Этаж {i}', 'S_dl'],
            'n': edited_floor.loc[f'Этаж {i}', 'n'],
            'b_dl': edited_floor.loc[f'Этаж {i}', 'b_dl'],
            'h_dl': edited_floor.loc[f'Этаж {i}', 'h_dl'],
            'S_dr': edited_floor.loc[f'Этаж {i}', 'S_dr'],
            'm': edited_floor.loc[f'Этаж {i}', 'm'],
            'b_dr': edited_floor.loc[f'Этаж {i}', 'b_dr'],
            'h_dr': edited_floor.loc[f'Этаж {i}', 'h_dr']
        }
        floors_list.append(floor)

    # Собираем все входные данные
    input_data = {
        # Параметры воздуха
        't_a': t_a,
        't_r': t_r,

        # Параметры лифтовой шахты
        'F_lc': F_lc,
        'F_ls': F_ls,
    
        # Параметры 1-го этажа
        'n_1': n_1,
        'xi_l_1': xi_l_1,
        'b_dl_1': b_dl_1,
        'h_dl_1': h_dl_1,

        # Параметры вентилятора
        'P_dl': P_dl,
        'h_l_N': h_l_N,
        'h_l_0': h_l_0,
        
        # Параметры 2-го-N-го этажей
        'h_2': h_2,
        'h_dl_2': h_dl_2,
        'floors_data': floors_list,
        'N': N
    }
    
#---------------------------------------------------------------------

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_9(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_r, кг/м³",
                    value=formatted_results.get('rho_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура воздуха в лифтовой шахте, К",
                    value=formatted_results.get('T_l', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_l, кг/м³",
                    value=formatted_results.get('rho_l', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            with col2:
                # Вывод параметров 1-го этажа
                st.subheader("2. Параметры 1-го этажа")
                st.number_input(
                    label="Коэффициент местного сопротивления узла «кабина-шахта» при открытых дверях кабины и шахты на основном посадочном этаже",
                    value=formatted_results.get('xi_l_1_new', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Площадь дверей лифтовой шахты на уровне 1-го этажа, м²",
                    value=formatted_results.get('F_dl_1', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Массовый расход воздуха на уровне 1-го этажа лифтовой шахты, кг/с",
                    value=formatted_results.get('G_l_1', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            # Вывод параметров 2-го-N-го этажей
            st.subheader("3. Параметры 2-го-N-го этажей")

            # Создаём пустой список для хранения данных
            floor_data = []

            # Список всех обязательных параметров для проверки
            required_params = [
                'P_l', 'S_dl', 'F_dl', 'S_dr', 'F_dr', 'S_lr', 'delta_G_l'
            ]

            for i in range(2, N + 1):
                try:
                    # Создаём словарь с данными для текущего этажа
                    row_data = {
                        'P_l, Па': results.get(f'P_l_{i}', 0),
                        'S_dl, м³/кг': results.get(f'S_dl_{i}_new', 0),
                        'F_dl, м²': results.get(f'F_dl_{i}', 0),
                        'S_dr, м³/кг': results.get(f'S_dr_{i}_new', 0),
                        'F_dr, м²': results.get(f'F_dr_{i}', 0),
                        'S_lr, м³/кг': results.get(f'S_lr_{i}', 0),
                        'ΔG_l, кг/с': results.get(f'delta_G_l_{i}', 0)
                    }

                    # Проверяем, есть ли хотя бы одно ненулевое значение
                    if all(value == 0 for value in row_data.values() if isinstance(value, (int, float))):
                        continue  # Пропускаем полностью нулевой этаж

                    # Добавляем строку в список
                    floor_data.append(row_data)

                except Exception as e:
                    st.error(f"Ошибка при обработке этажа {i}: {e}")

            # Создаём итоговый DataFrame
            floor_df = pd.DataFrame(floor_data, index=[f'Этаж {i}' for i in range(2, N + 1)])
            st.dataframe(floor_df)

            # Вывод итогового расчета
            st.subheader("4. Итоговый расчет")
            st.number_input(
                label="Массовый расход воздуха, подаваемый в лифтовую шахту, кг/с",
                value=formatted_results.get('G_l', 0.0),
                disabled=True,
                format="%.2f"
            )

            # Вывод параметров вентилятора
            st.subheader("5. Параметры вентилятора")
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

#---------------------------------------------------------------------

            # График зависимости массового расхода
            st.subheader("Зависимость массового расхода воздуха от этажа")

            # Создаем словарь для данных графика
            mass_flow_data = {
                'Этаж': [f'Этаж {i}' for i in range(2, N+1)],
                'Массовый расход, кг/с': [results.get(f'delta_G_l_{i}', np.nan) for i in range(2, N+1)]
            }

            mass_flow_df = pd.DataFrame(mass_flow_data)

            if mass_flow_df.isnull().values.any():
                st.warning("Не все данные для построения графика массового расхода доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую массового расхода
                ax.plot(
                    mass_flow_df['Этаж'],
                    mass_flow_df['Массовый расход, кг/с'],
                    marker='o',
                    color='blue',
                    linestyle='-',
                    label='Профиль массового расхода'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость массового расхода воздуха от этажа')
                ax.set_xlabel('Этаж')
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




#############################################################################################################################################################################################################################################
if scenario == 10:
    st.info("Выбран сценарий 10: приточная противодымная вентиляция в лифтовую шахту, имеющую следующие характеристики:")
    st.text("- расположена в центральном ядре здания;")
    st.text("- остановки лифта только на надземных этажах;")
    st.text("- имеет выгороженные лифтовые холлы на каждом этаже.")

#---------------------------------------------------------------------

    col1, col2 = st.columns(2)
    with col1:

        # Ввод параметров воздуха
        st.subheader("1. Параметры воздуха")
        t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
        t_r = st.number_input("Температура воздуха в помещении, °C", value=0, step=1)

        # Ввод параметров лифтовой шахты
        st.subheader("2. Параметры лифтовой шахты")
        F_lc = st.number_input("Площадь поперечного сечения кабины лифта, м²", value=1.0, step=0.1)                
        F_ls = st.number_input("Площадь поперечного сечения лифтовой шахты, м²", value=1.5, step=0.1)

        # Ввод параметров 1-го этажа
        st.subheader("3. Параметры 1-го этажа")
        n_1 = st.number_input("Количество дверей лифтовой шахты на уровне 1-го этажа", value=1, step=1)
        xi_l_1 = st.number_input("Коэффициент местного сопротивления узла «кабина-шахта» при открытых дверях кабины и шахты на уровне 1-го этажа (0 - нет данных)", value=0.0, step=0.1)        
        b_dl_1 = st.number_input("Ширина дверей лифтовой шахты на уровне 1-го этажа, м", value=1.00, step=0.01)
        h_dl_1 = st.number_input("Высота дверей лифтовой шахты на уровне 1-го этажа, м", value=2.00, step=0.01)
        m_1 = st.number_input("Количество дверей лифтового холла на уровне 1-го этажа", value=1, step=1)
        xi_d_1 = st.number_input("Коэффициент местного сопротивления дверей лифтового холла (ξd=2,44)", value=2.44, step=0.01)        
        b_dr_1 = st.number_input("Ширина дверей лифтового холла на уровне 1-го этажа, м", value=1.00, step=0.01)
        h_dr_1 = st.number_input("Высота дверей лифтового холла на уровне 1-го этажа, м", value=2.00, step=0.01)

    with col2:
        # Ввод параметров вентилятора
        st.subheader("4. Параметры вентилятора")
        P_dl = st.number_input("Суммарное сопротивление присоединительных воздуховодов, Па", value=1, step=1)
        h_l_N = st.number_input("Высота лифтовой шахты между уровнями нижнего и верхнего этажей, м", value=22.50, step=0.01)
        h_l_0 = st.number_input("Разность между уровнями расположения приемного устройства наружного воздуха и оголовка лифтовой шахты, м", value=0.50, step=0.01)

    # Ввод параметров 2-го-N-го этажей
    st.subheader("4. Параметры 2-го-N-го этажей")
    N = st.number_input("Количество этажей", value=10, step=1)
    # Создаем редактируемую таблицу
    floors_df = pd.DataFrame({
        'h': [2.5] * (N-1),
        'S_dl': [0] * (N-1),
        'n': [1.0] * (N-1),
        'b_dl': [1.0] * (N-1),
        'h_dl': [2.0] * (N-1),
        'S_dr': [0] * (N-1),
        'm': [1.0] * (N-1),
        'b_dr': [1.0] * (N-1),
        'h_dr': [2.0] * (N-1),
    }, index=[f'Этаж {i}' for i in range(2, N+1)])

    columns = {
        'h': st.column_config.NumberColumn("h, м", format="%.2f"),
        'S_dl': st.column_config.NumberColumn("S_dl, м³/кг", format="%.0f"),
        'n': st.column_config.NumberColumn("n", format="%.0f"),
        'b_dl': st.column_config.NumberColumn("b_dl, м", format="%.2f"),
        'h_dl': st.column_config.NumberColumn("h_dl, м", format="%.2f"),
        'S_dr': st.column_config.NumberColumn("S_dr, м³/кг", format="%.0f"),
        'm': st.column_config.NumberColumn("m", format="%.0f"),
        'b_dr': st.column_config.NumberColumn("b_dr, м", format="%.2f"),
        'h_dr': st.column_config.NumberColumn("h_dr, м", format="%.2f")
    }

    edited_floor = st.data_editor(
        floors_df,
        column_config=columns,
        key='floor_editor'
    )

    # Извлекаем параметры для 2-го этажа из отредактированной таблицы
    h_2 = edited_floor.loc['Этаж 2', 'h']
    h_dl_2 = edited_floor.loc['Этаж 2', 'h_dl']
    
    # Собираем все параметры в единый список словарей
    floors_list = []
    for i in range(2, N + 1):
        floor = {
            'h': edited_floor.loc[f'Этаж {i}', 'h'],
            'S_dl': edited_floor.loc[f'Этаж {i}', 'S_dl'],
            'n': edited_floor.loc[f'Этаж {i}', 'n'],
            'b_dl': edited_floor.loc[f'Этаж {i}', 'b_dl'],
            'h_dl': edited_floor.loc[f'Этаж {i}', 'h_dl'],
            'S_dr': edited_floor.loc[f'Этаж {i}', 'S_dr'],
            'm': edited_floor.loc[f'Этаж {i}', 'm'],
            'b_dr': edited_floor.loc[f'Этаж {i}', 'b_dr'],
            'h_dr': edited_floor.loc[f'Этаж {i}', 'h_dr']
        }
        floors_list.append(floor)

    # Собираем все входные данные
    input_data = {
        # Параметры воздуха
        't_a': t_a,
        't_r': t_r,

        # Параметры лифтовой шахты
        'F_lc': F_lc,
        'F_ls': F_ls,
    
        # Параметры 1-го этажа
        'n_1': n_1,
        'xi_l_1': xi_l_1,
        'b_dl_1': b_dl_1,
        'h_dl_1': h_dl_1,
        'm_1': m_1,
        'xi_d_1': xi_d_1,
        'b_dr_1': b_dr_1,
        'h_dr_1': h_dr_1,

        # Параметры вентилятора
        'P_dl': P_dl,
        'h_l_N': h_l_N,
        'h_l_0': h_l_0,
        
        # Параметры 2-го-N-го этажей
        'h_2': h_2,
        'h_dl_2': h_dl_2,
        'floors_data': floors_list,
        'N': N
    }
    
#---------------------------------------------------------------------

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_10(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_r, кг/м³",
                    value=formatted_results.get('rho_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура воздуха в лифтовой шахте, К",
                    value=formatted_results.get('T_l', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_l, кг/м³",
                    value=formatted_results.get('rho_l', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            with col2:
                # Вывод параметров 1-го этажа
                st.subheader("2. Параметры 1-го этажа")
                st.number_input(
                    label="Коэффициент местного сопротивления узла «кабина-шахта» при открытых дверях кабины и шахты на основном посадочном этаже",
                    value=formatted_results.get('xi_l_1_new', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Площадь дверей лифтовой шахты на уровне 1-го этажа, м²",
                    value=formatted_results.get('F_dl_1', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Площадь дверей лифтового холла на уровне 1-го этажа, м²",
                    value=formatted_results.get('F_dr_1', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Массовый расход воздуха на уровне 1-го этажа лифтовой шахты, кг/с",
                    value=formatted_results.get('G_l_1', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            # Вывод параметров 2-го-N-го этажей
            st.subheader("3. Параметры 2-го-N-го этажей")

            # Создаём пустой список для хранения данных
            floor_data = []

            # Список всех обязательных параметров для проверки
            required_params = [
                'P_l', 'S_dl', 'F_dl', 'S_dr', 'F_dr', 'S_lr', 'delta_G_l'
            ]

            for i in range(2, N + 1):
                try:
                    # Создаём словарь с данными для текущего этажа
                    row_data = {
                        'P_l, Па': results.get(f'P_l_{i}', 0),
                        'S_dl, м³/кг': results.get(f'S_dl_{i}_new', 0),
                        'F_dl, м²': results.get(f'F_dl_{i}', 0),
                        'S_dr, м³/кг': results.get(f'S_dr_{i}_new', 0),
                        'F_dr, м²': results.get(f'F_dr_{i}', 0),
                        'S_lr, м³/кг': results.get(f'S_lr_{i}', 0),
                        'ΔG_l, кг/с': results.get(f'delta_G_l_{i}', 0)
                    }

                    # Проверяем, есть ли хотя бы одно ненулевое значение
                    if all(value == 0 for value in row_data.values() if isinstance(value, (int, float))):
                        continue  # Пропускаем полностью нулевой этаж

                    # Добавляем строку в список
                    floor_data.append(row_data)

                except Exception as e:
                    st.error(f"Ошибка при обработке этажа {i}: {e}")

            # Создаём итоговый DataFrame
            floor_df = pd.DataFrame(floor_data, index=[f'Этаж {i}' for i in range(2, N + 1)])
            st.dataframe(floor_df)

            # Вывод итогового расчета
            st.subheader("4. Итоговый расчет")
            st.number_input(
                label="Массовый расход воздуха, подаваемый в лифтовую шахту, кг/с",
                value=formatted_results.get('G_l', 0.0),
                disabled=True,
                format="%.2f"
            )

            # Вывод параметров вентилятора
            st.subheader("5. Параметры вентилятора")
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

#---------------------------------------------------------------------

            # График зависимости массового расхода
            st.subheader("Зависимость массового расхода воздуха от этажа")

            # Создаем словарь для данных графика
            mass_flow_data = {
                'Этаж': [f'Этаж {i}' for i in range(2, N+1)],
                'Массовый расход, кг/с': [results.get(f'delta_G_l_{i}', np.nan) for i in range(2, N+1)]
            }

            mass_flow_df = pd.DataFrame(mass_flow_data)

            if mass_flow_df.isnull().values.any():
                st.warning("Не все данные для построения графика массового расхода доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую массового расхода
                ax.plot(
                    mass_flow_df['Этаж'],
                    mass_flow_df['Массовый расход, кг/с'],
                    marker='o',
                    color='blue',
                    linestyle='-',
                    label='Профиль массового расхода'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость массового расхода воздуха от этажа')
                ax.set_xlabel('Этаж')
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




#############################################################################################################################################################################################################################################
if scenario == 11:
    st.info("Выбран сценарий 11: приточная противодымная вентиляция в лифтовую шахту, имеющую следующие характеристики:")
    st.text("- расположена у наружных ограждающих конструкций здания;")
    st.text("- остановки лифта только на надземных этажах;")
    st.text("- имеет выгороженные лифтовые холлы на каждом этаже.")

#---------------------------------------------------------------------

    col1, col2 = st.columns(2)
    with col1:

        # Ввод параметров воздуха
        st.subheader("1. Параметры воздуха")
        nu_a = st.number_input("Скорость ветра, м/с", value=1.3, step=0.1)
        t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
        k_alpha_ww = st.number_input("Аэродинамический коэффициент ветрового напора для наветренной стороны", value=0.50, step=0.01)
        k_alpha_w0 = st.number_input("Аэродинамический коэффициент ветрового напора для заветренной стороны", value=-0.60, step=0.01)
        t_r = st.number_input("Температура воздуха в помещении, °C", value=0, step=1)

        # Ввод параметров лифтовой шахты
        st.subheader("2. Параметры лифтовой шахты")
        F_lc = st.number_input("Площадь поперечного сечения кабины лифта, м²", value=1.0, step=0.1)                
        F_ls = st.number_input("Площадь поперечного сечения лифтовой шахты, м²", value=1.5, step=0.1)

        # Ввод параметров 1-го этажа
        st.subheader("3. Параметры 1-го этажа")
        n_1 = st.number_input("Количество дверей лифтовой шахты на уровне 1-го этажа", value=1, step=1)
        xi_l_1 = st.number_input("Коэффициент местного сопротивления узла «кабина-шахта» при открытых дверях кабины и шахты на уровне 1-го этажа (0 - нет данных)", value=0.0, step=0.1)        
        b_dl_1 = st.number_input("Ширина дверей лифтовой шахты на уровне 1-го этажа, м", value=1.00, step=0.01)
        h_dl_1 = st.number_input("Высота дверей лифтовой шахты на уровне 1-го этажа, м", value=2.00, step=0.01)
        m_1 = st.number_input("Количество дверей лифтового холла на уровне 1-го этажа", value=1, step=1)
        xi_d_1 = st.number_input("Коэффициент местного сопротивления дверей лифтового холла (ξd=2,44)", value=2.44, step=0.01)        
        b_dr_1 = st.number_input("Ширина дверей лифтового холла на уровне 1-го этажа, м", value=1.00, step=0.01)
        h_dr_1 = st.number_input("Высота дверей лифтового холла на уровне 1-го этажа, м", value=2.00, step=0.01)

    with col2:
        # Ввод параметров вентилятора
        st.subheader("4. Параметры вентилятора")
        P_dl = st.number_input("Суммарное сопротивление присоединительных воздуховодов, Па", value=1, step=1)
        h_l_N = st.number_input("Высота лифтовой шахты между уровнями нижнего и верхнего этажей, м", value=22.50, step=0.01)
        h_l_0 = st.number_input("Разность между уровнями расположения приемного устройства наружного воздуха и оголовка лифтовой шахты, м", value=0.50, step=0.01)

    # Ввод параметров 2-го-N-го этажей
    st.subheader("4. Параметры 2-го-N-го этажей")
    N = st.number_input("Количество этажей", value=10, step=1)
    # Создаем редактируемую таблицу
    floors_df = pd.DataFrame({
        'h': [2.5] * (N-1),
        'S_dl': [0] * (N-1),
        'n': [1.0] * (N-1),
        'b_dl': [1.0] * (N-1),
        'h_dl': [2.0] * (N-1),
        'S_dr': [0] * (N-1),
        'm': [1.0] * (N-1),
        'b_dr': [1.0] * (N-1),
        'h_dr': [2.0] * (N-1),
    }, index=[f'Этаж {i}' for i in range(2, N+1)])

    columns = {
        'h': st.column_config.NumberColumn("h, м", format="%.2f"),
        'S_dl': st.column_config.NumberColumn("S_dl, м³/кг", format="%.0f"),
        'n': st.column_config.NumberColumn("n", format="%.0f"),
        'b_dl': st.column_config.NumberColumn("b_dl, м", format="%.2f"),
        'h_dl': st.column_config.NumberColumn("h_dl, м", format="%.2f"),
        'S_dr': st.column_config.NumberColumn("S_dr, м³/кг", format="%.0f"),
        'm': st.column_config.NumberColumn("m", format="%.0f"),
        'b_dr': st.column_config.NumberColumn("b_dr, м", format="%.2f"),
        'h_dr': st.column_config.NumberColumn("h_dr, м", format="%.2f")
    }

    edited_floor = st.data_editor(
        floors_df,
        column_config=columns,
        key='floor_editor'
    )

    # Извлекаем параметры для 2-го этажа из отредактированной таблицы
    h_2 = edited_floor.loc['Этаж 2', 'h']
    h_dl_2 = edited_floor.loc['Этаж 2', 'h_dl']
    
    # Собираем все параметры в единый список словарей
    floors_list = []
    for i in range(2, N + 1):
        floor = {
            'h': edited_floor.loc[f'Этаж {i}', 'h'],
            'S_dl': edited_floor.loc[f'Этаж {i}', 'S_dl'],
            'n': edited_floor.loc[f'Этаж {i}', 'n'],
            'b_dl': edited_floor.loc[f'Этаж {i}', 'b_dl'],
            'h_dl': edited_floor.loc[f'Этаж {i}', 'h_dl'],
            'S_dr': edited_floor.loc[f'Этаж {i}', 'S_dr'],
            'm': edited_floor.loc[f'Этаж {i}', 'm'],
            'b_dr': edited_floor.loc[f'Этаж {i}', 'b_dr'],
            'h_dr': edited_floor.loc[f'Этаж {i}', 'h_dr']
        }
        floors_list.append(floor)

    # Собираем все входные данные
    input_data = {
        # Параметры воздуха
        'nu_a': nu_a,
        't_a': t_a,
        'k_alpha_ww': k_alpha_ww,
        'k_alpha_w0': k_alpha_w0,
        't_r': t_r,

        # Параметры лифтовой шахты
        'F_lc': F_lc,
        'F_ls': F_ls,
    
        # Параметры 1-го этажа
        'n_1': n_1,
        'xi_l_1': xi_l_1,
        'b_dl_1': b_dl_1,
        'h_dl_1': h_dl_1,
        'm_1': m_1,
        'xi_d_1': xi_d_1,
        'b_dr_1': b_dr_1,
        'h_dr_1': h_dr_1,

        # Параметры вентилятора
        'P_dl': P_dl,
        'h_l_N': h_l_N,
        'h_l_0': h_l_0,
        
        # Параметры 2-го-N-го этажей
        'h_2': h_2,
        'h_dl_2': h_dl_2,
        'floors_data': floors_list,
        'N': N
    }
    
#---------------------------------------------------------------------

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_11(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_r, кг/м³",
                    value=formatted_results.get('rho_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура воздуха в лифтовой шахте, К",
                    value=formatted_results.get('T_l', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_l, кг/м³",
                    value=formatted_results.get('rho_l', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            with col2:
                # Вывод параметров 1-го этажа
                st.subheader("2. Параметры 1-го этажа")
                st.number_input(
                    label="Коэффициент местного сопротивления узла «кабина-шахта» при открытых дверях кабины и шахты на основном посадочном этаже",
                    value=formatted_results.get('xi_l_1_new', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Площадь дверей лифтовой шахты на уровне 1-го этажа, м²",
                    value=formatted_results.get('F_dl_1', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Площадь дверей лифтового холла на уровне 1-го этажа, м²",
                    value=formatted_results.get('F_dr_1', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Массовый расход воздуха на уровне 1-го этажа лифтовой шахты, кг/с",
                    value=formatted_results.get('G_l_1', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            # Вывод параметров 2-го-N-го этажей
            st.subheader("3. Параметры 2-го-N-го этажей")

            # Создаём пустой список для хранения данных
            floor_data = []

            # Список всех обязательных параметров для проверки
            required_params = [
                'P_l', 'S_dl', 'F_dl', 'S_dr', 'F_dr', 'S_lr', 'delta_G_l'
            ]

            for i in range(2, N + 1):
                try:
                    # Создаём словарь с данными для текущего этажа
                    row_data = {
                        'P_l, Па': results.get(f'P_l_{i}', 0),
                        'S_dl, м³/кг': results.get(f'S_dl_{i}_new', 0),
                        'F_dl, м²': results.get(f'F_dl_{i}', 0),
                        'S_dr, м³/кг': results.get(f'S_dr_{i}_new', 0),
                        'F_dr, м²': results.get(f'F_dr_{i}', 0),
                        'S_lr, м³/кг': results.get(f'S_lr_{i}', 0),
                        'ΔG_l, кг/с': results.get(f'delta_G_l_{i}', 0)
                    }

                    # Проверяем, есть ли хотя бы одно ненулевое значение
                    if all(value == 0 for value in row_data.values() if isinstance(value, (int, float))):
                        continue  # Пропускаем полностью нулевой этаж

                    # Добавляем строку в список
                    floor_data.append(row_data)

                except Exception as e:
                    st.error(f"Ошибка при обработке этажа {i}: {e}")

            # Создаём итоговый DataFrame
            floor_df = pd.DataFrame(floor_data, index=[f'Этаж {i}' for i in range(2, N + 1)])
            st.dataframe(floor_df)

            # Вывод итогового расчета
            st.subheader("4. Итоговый расчет")
            st.number_input(
                label="Массовый расход воздуха, подаваемый в лифтовую шахту, кг/с",
                value=formatted_results.get('G_l', 0.0),
                disabled=True,
                format="%.2f"
            )

            # Вывод параметров вентилятора
            st.subheader("5. Параметры вентилятора")
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

#---------------------------------------------------------------------

            # График зависимости массового расхода
            st.subheader("Зависимость массового расхода воздуха от этажа")

            # Создаем словарь для данных графика
            mass_flow_data = {
                'Этаж': [f'Этаж {i}' for i in range(2, N+1)],
                'Массовый расход, кг/с': [results.get(f'delta_G_l_{i}', np.nan) for i in range(2, N+1)]
            }

            mass_flow_df = pd.DataFrame(mass_flow_data)

            if mass_flow_df.isnull().values.any():
                st.warning("Не все данные для построения графика массового расхода доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую массового расхода
                ax.plot(
                    mass_flow_df['Этаж'],
                    mass_flow_df['Массовый расход, кг/с'],
                    marker='o',
                    color='blue',
                    linestyle='-',
                    label='Профиль массового расхода'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость массового расхода воздуха от этажа')
                ax.set_xlabel('Этаж')
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




#############################################################################################################################################################################################################################################
if scenario == 12:
    st.info("Выбран сценарий 12: приточная противодымная вентиляция в лифтовую шахту, имеющую следующие характеристики:")
    st.text("- расположена у наружных ограждающих конструкций здания;")
    st.text("- остановки лифта только на надземных этажах;")
    st.text("- имеет выгороженные лифтовые холлы на каждом этаже, кроме нижнего.")

#---------------------------------------------------------------------

    col1, col2 = st.columns(2)
    with col1:

        # Ввод параметров воздуха
        st.subheader("1. Параметры воздуха")
        nu_a = st.number_input("Скорость ветра, м/с", value=1.3, step=0.1)
        t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
        k_alpha_ww = st.number_input("Аэродинамический коэффициент ветрового напора для наветренной стороны", value=0.50, step=0.01)
        k_alpha_w0 = st.number_input("Аэродинамический коэффициент ветрового напора для заветренной стороны", value=-0.60, step=0.01)
        t_r = st.number_input("Температура воздуха в помещении, °C", value=0, step=1)

        # Ввод параметров лифтовой шахты
        st.subheader("2. Параметры лифтовой шахты")
        F_lc = st.number_input("Площадь поперечного сечения кабины лифта, м²", value=1.0, step=0.1)                
        F_ls = st.number_input("Площадь поперечного сечения лифтовой шахты, м²", value=1.5, step=0.1)

        # Ввод параметров 1-го этажа
        st.subheader("3. Параметры 1-го этажа")
        n_1 = st.number_input("Количество дверей лифтовой шахты на уровне 1-го этажа", value=1, step=1)
        xi_l_1 = st.number_input("Коэффициент местного сопротивления узла «кабина-шахта» при открытых дверях кабины и шахты на уровне 1-го этажа (0 - нет данных)", value=0.0, step=0.1)        
        b_dl_1 = st.number_input("Ширина дверей лифтовой шахты на уровне 1-го этажа, м", value=1.00, step=0.01)
        h_dl_1 = st.number_input("Высота дверей лифтовой шахты на уровне 1-го этажа, м", value=2.00, step=0.01)

    with col2:
        # Ввод параметров вентилятора
        st.subheader("4. Параметры вентилятора")
        P_dl = st.number_input("Суммарное сопротивление присоединительных воздуховодов, Па", value=1, step=1)
        h_l_N = st.number_input("Высота лифтовой шахты между уровнями нижнего и верхнего этажей, м", value=22.50, step=0.01)
        h_l_0 = st.number_input("Разность между уровнями расположения приемного устройства наружного воздуха и оголовка лифтовой шахты, м", value=0.50, step=0.01)

    # Ввод параметров 2-го-N-го этажей
    st.subheader("4. Параметры 2-го-N-го этажей")
    N = st.number_input("Количество этажей", value=10, step=1)
    # Создаем редактируемую таблицу
    floors_df = pd.DataFrame({
        'h': [2.5] * (N-1),
        'S_dl': [0] * (N-1),
        'n': [1.0] * (N-1),
        'b_dl': [1.0] * (N-1),
        'h_dl': [2.0] * (N-1),
        'S_dr': [0] * (N-1),
        'm': [1.0] * (N-1),
        'b_dr': [1.0] * (N-1),
        'h_dr': [2.0] * (N-1),
    }, index=[f'Этаж {i}' for i in range(2, N+1)])

    columns = {
        'h': st.column_config.NumberColumn("h, м", format="%.2f"),
        'S_dl': st.column_config.NumberColumn("S_dl, м³/кг", format="%.0f"),
        'n': st.column_config.NumberColumn("n", format="%.0f"),
        'b_dl': st.column_config.NumberColumn("b_dl, м", format="%.2f"),
        'h_dl': st.column_config.NumberColumn("h_dl, м", format="%.2f"),
        'S_dr': st.column_config.NumberColumn("S_dr, м³/кг", format="%.0f"),
        'm': st.column_config.NumberColumn("m", format="%.0f"),
        'b_dr': st.column_config.NumberColumn("b_dr, м", format="%.2f"),
        'h_dr': st.column_config.NumberColumn("h_dr, м", format="%.2f")
    }

    edited_floor = st.data_editor(
        floors_df,
        column_config=columns,
        key='floor_editor'
    )

    # Извлекаем параметры для 2-го этажа из отредактированной таблицы
    h_2 = edited_floor.loc['Этаж 2', 'h']
    h_dl_2 = edited_floor.loc['Этаж 2', 'h_dl']
    
    # Собираем все параметры в единый список словарей
    floors_list = []
    for i in range(2, N + 1):
        floor = {
            'h': edited_floor.loc[f'Этаж {i}', 'h'],
            'S_dl': edited_floor.loc[f'Этаж {i}', 'S_dl'],
            'n': edited_floor.loc[f'Этаж {i}', 'n'],
            'b_dl': edited_floor.loc[f'Этаж {i}', 'b_dl'],
            'h_dl': edited_floor.loc[f'Этаж {i}', 'h_dl'],
            'S_dr': edited_floor.loc[f'Этаж {i}', 'S_dr'],
            'm': edited_floor.loc[f'Этаж {i}', 'm'],
            'b_dr': edited_floor.loc[f'Этаж {i}', 'b_dr'],
            'h_dr': edited_floor.loc[f'Этаж {i}', 'h_dr']
        }
        floors_list.append(floor)

    # Собираем все входные данные
    input_data = {
        # Параметры воздуха
        'nu_a': nu_a,
        't_a': t_a,
        'k_alpha_ww': k_alpha_ww,
        'k_alpha_w0': k_alpha_w0,
        't_r': t_r,

        # Параметры лифтовой шахты
        'F_lc': F_lc,
        'F_ls': F_ls,
    
        # Параметры 1-го этажа
        'n_1': n_1,
        'xi_l_1': xi_l_1,
        'b_dl_1': b_dl_1,
        'h_dl_1': h_dl_1,

        # Параметры вентилятора
        'P_dl': P_dl,
        'h_l_N': h_l_N,
        'h_l_0': h_l_0,
        
        # Параметры 2-го-N-го этажей
        'h_2': h_2,
        'h_dl_2': h_dl_2,
        'floors_data': floors_list,
        'N': N
    }
    
#---------------------------------------------------------------------

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_12(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_r, кг/м³",
                    value=formatted_results.get('rho_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура воздуха в лифтовой шахте, К",
                    value=formatted_results.get('T_l', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_l, кг/м³",
                    value=formatted_results.get('rho_l', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            with col2:
                # Вывод параметров 1-го этажа
                st.subheader("2. Параметры 1-го этажа")
                st.number_input(
                    label="Коэффициент местного сопротивления узла «кабина-шахта» при открытых дверях кабины и шахты на основном посадочном этаже",
                    value=formatted_results.get('xi_l_1_new', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Площадь дверей лифтовой шахты на уровне 1-го этажа, м²",
                    value=formatted_results.get('F_dl_1', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Массовый расход воздуха на уровне 1-го этажа лифтовой шахты, кг/с",
                    value=formatted_results.get('G_l_1', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            # Вывод параметров 2-го-N-го этажей
            st.subheader("3. Параметры 2-го-N-го этажей")

            # Создаём пустой список для хранения данных
            floor_data = []

            # Список всех обязательных параметров для проверки
            required_params = [
                'P_l', 'S_dl', 'F_dl', 'S_dr', 'F_dr', 'S_lr', 'delta_G_l'
            ]

            for i in range(2, N + 1):
                try:
                    # Создаём словарь с данными для текущего этажа
                    row_data = {
                        'P_l, Па': results.get(f'P_l_{i}', 0),
                        'S_dl, м³/кг': results.get(f'S_dl_{i}_new', 0),
                        'F_dl, м²': results.get(f'F_dl_{i}', 0),
                        'S_dr, м³/кг': results.get(f'S_dr_{i}_new', 0),
                        'F_dr, м²': results.get(f'F_dr_{i}', 0),
                        'S_lr, м³/кг': results.get(f'S_lr_{i}', 0),
                        'ΔG_l, кг/с': results.get(f'delta_G_l_{i}', 0)
                    }

                    # Проверяем, есть ли хотя бы одно ненулевое значение
                    if all(value == 0 for value in row_data.values() if isinstance(value, (int, float))):
                        continue  # Пропускаем полностью нулевой этаж

                    # Добавляем строку в список
                    floor_data.append(row_data)

                except Exception as e:
                    st.error(f"Ошибка при обработке этажа {i}: {e}")

            # Создаём итоговый DataFrame
            floor_df = pd.DataFrame(floor_data, index=[f'Этаж {i}' for i in range(2, N + 1)])
            st.dataframe(floor_df)

            # Вывод итогового расчета
            st.subheader("4. Итоговый расчет")
            st.number_input(
                label="Массовый расход воздуха, подаваемый в лифтовую шахту, кг/с",
                value=formatted_results.get('G_l', 0.0),
                disabled=True,
                format="%.2f"
            )

            # Вывод параметров вентилятора
            st.subheader("5. Параметры вентилятора")
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

#---------------------------------------------------------------------

            # График зависимости массового расхода
            st.subheader("Зависимость массового расхода воздуха от этажа")

            # Создаем словарь для данных графика
            mass_flow_data = {
                'Этаж': [f'Этаж {i}' for i in range(2, N+1)],
                'Массовый расход, кг/с': [results.get(f'delta_G_l_{i}', np.nan) for i in range(2, N+1)]
            }

            mass_flow_df = pd.DataFrame(mass_flow_data)

            if mass_flow_df.isnull().values.any():
                st.warning("Не все данные для построения графика массового расхода доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую массового расхода
                ax.plot(
                    mass_flow_df['Этаж'],
                    mass_flow_df['Массовый расход, кг/с'],
                    marker='o',
                    color='blue',
                    linestyle='-',
                    label='Профиль массового расхода'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость массового расхода воздуха от этажа')
                ax.set_xlabel('Этаж')
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




#############################################################################################################################################################################################################################################
if scenario == 13:
    st.info("Выбран сценарий 13: приточная противодымная вентиляция в лифтовую шахту, имеющую следующие характеристики:")
    st.text("- расположена у наружных ограждающих конструкций здания;")
    st.text("- остановки лифта на нижнем надземном и подземных этажах;")
    st.text("- имеет выгороженные лифтовые холлы на каждом этаже.")

#---------------------------------------------------------------------

    col1, col2 = st.columns(2)
    with col1:

        # Ввод параметров воздуха
        st.subheader("1. Параметры воздуха")
        nu_a = st.number_input("Скорость ветра, м/с", value=1.3, step=0.1)
        t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
        k_alpha_ww = st.number_input("Аэродинамический коэффициент ветрового напора для наветренной стороны", value=0.50, step=0.01)
        k_alpha_w0 = st.number_input("Аэродинамический коэффициент ветрового напора для заветренной стороны", value=-0.60, step=0.01)
        t_r = st.number_input("Температура воздуха в помещении, °C", value=0, step=1)

        # Ввод параметров лифтовой шахты
        st.subheader("2. Параметры лифтовой шахты")
        F_lc = st.number_input("Площадь поперечного сечения кабины лифта, м²", value=1.0, step=0.1)                
        F_ls = st.number_input("Площадь поперечного сечения лифтовой шахты, м²", value=1.5, step=0.1)

        # Ввод параметров 1-го этажа
        st.subheader("3. Параметры 1-го этажа")
        n_1 = st.number_input("Количество дверей лифтовой шахты на уровне 1-го этажа", value=1, step=1)
        xi_l_1 = st.number_input("Коэффициент местного сопротивления узла «кабина-шахта» при открытых дверях кабины и шахты на уровне 1-го этажа (0 - нет данных)", value=0.0, step=0.1)        
        b_dl_1 = st.number_input("Ширина дверей лифтовой шахты на уровне 1-го этажа, м", value=1.00, step=0.01)
        h_dl_1 = st.number_input("Высота дверей лифтовой шахты на уровне 1-го этажа, м", value=2.00, step=0.01)
        m_1 = st.number_input("Количество дверей лифтового холла на уровне 1-го этажа", value=1, step=1)
        xi_d_1 = st.number_input("Коэффициент местного сопротивления дверей лифтового холла (ξd=2,44)", value=2.44, step=0.01)        
        b_dr_1 = st.number_input("Ширина дверей лифтового холла на уровне 1-го этажа, м", value=1.00, step=0.01)
        h_dr_1 = st.number_input("Высота дверей лифтового холла на уровне 1-го этажа, м", value=2.00, step=0.01)

    with col2:
        # Ввод параметров вентилятора
        st.subheader("4. Параметры вентилятора")
        P_dl = st.number_input("Суммарное сопротивление присоединительных воздуховодов, Па", value=1, step=1)
        h_l_N = st.number_input("Высота лифтовой шахты между уровнями нижнего и верхнего этажей, м", value=10.00, step=0.01)
        h_l_0 = st.number_input("Разность между уровнями расположения приемного устройства наружного воздуха и оголовка лифтовой шахты, м", value=0.50, step=0.01)

    # Ввод параметров (-1)-го-(-N)-го этажей
    st.subheader("4. Параметры (-1)-го-(-N)-го этажей")
    N = st.number_input("Количество этажей", value=5, step=1)
    h_minus_N = st.number_input("Уровень отметки пола нижнего подземного этажа, м", value=-12.5, step=0.1)
    h_dl_minus_N = st.number_input("Высота дверей лифтовой шахты на уровне нижнего подземного этажа, м", value=2.00, step=0.1)    
    
    # Создаем редактируемую таблицу
    floors_df = pd.DataFrame({
        'h': [-2.5] * N,
        'S_dl': [0] * N,
        'n': [1.0] * N,
        'b_dl': [1.0] * N,
        'h_dl': [2.0] * N,
        'S_dr': [0] * N,
        'm': [1.0] * N,
        'b_dr': [1.0] * N,
        'h_dr': [2.0] * N,
    }, index=[f'Этаж -{i}' for i in range(1, N+1)])

    columns = {
        'h': st.column_config.NumberColumn("h, м", format="%.2f"),
        'S_dl': st.column_config.NumberColumn("S_dl, м³/кг", format="%.0f"),
        'n': st.column_config.NumberColumn("n", format="%.0f"),
        'b_dl': st.column_config.NumberColumn("b_dl, м", format="%.2f"),
        'h_dl': st.column_config.NumberColumn("h_dl, м", format="%.2f"),
        'S_dr': st.column_config.NumberColumn("S_dr, м³/кг", format="%.0f"),
        'm': st.column_config.NumberColumn("m", format="%.0f"),
        'b_dr': st.column_config.NumberColumn("b_dr, м", format="%.2f"),
        'h_dr': st.column_config.NumberColumn("h_dr, м", format="%.2f")
    }

    edited_floor = st.data_editor(
        floors_df,
        column_config=columns,
        key='floor_editor'
    )
    
    # Собираем все параметры в единый список словарей
    floors_list = []
    for i in range(1, N + 1):
        floor = {
            'h': edited_floor.loc[f'Этаж -{i}', 'h'],
            'S_dl': edited_floor.loc[f'Этаж -{i}', 'S_dl'],
            'n': edited_floor.loc[f'Этаж -{i}', 'n'],
            'b_dl': edited_floor.loc[f'Этаж -{i}', 'b_dl'],
            'h_dl': edited_floor.loc[f'Этаж -{i}', 'h_dl'],
            'S_dr': edited_floor.loc[f'Этаж -{i}', 'S_dr'],
            'm': edited_floor.loc[f'Этаж -{i}', 'm'],
            'b_dr': edited_floor.loc[f'Этаж -{i}', 'b_dr'],
            'h_dr': edited_floor.loc[f'Этаж -{i}', 'h_dr']
        }
        floors_list.append(floor)

    # Собираем все входные данные
    input_data = {
        # Параметры воздуха
        'nu_a': nu_a,
        't_a': t_a,
        'k_alpha_ww': k_alpha_ww,
        'k_alpha_w0': k_alpha_w0,
        't_r': t_r,

        # Параметры лифтовой шахты
        'F_lc': F_lc,
        'F_ls': F_ls,
    
        # Параметры 1-го этажа
        'n_1': n_1,
        'xi_l_1': xi_l_1,
        'b_dl_1': b_dl_1,
        'h_dl_1': h_dl_1,
        'm_1': m_1,
        'xi_d_1': xi_d_1,
        'b_dr_1': b_dr_1,
        'h_dr_1': h_dr_1,

        # Параметры вентилятора
        'P_dl': P_dl,
        'h_l_N': h_l_N,
        'h_l_0': h_l_0,
        
        # Параметры (-1)-го-(-N)-го этажей
        'floors_data': floors_list,
        'N': N,
        'h_minus_N': h_minus_N,
        'h_dl_minus_N': h_dl_minus_N
    }
    
#---------------------------------------------------------------------

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_13(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_r, кг/м³",
                    value=formatted_results.get('rho_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура воздуха в лифтовой шахте, К",
                    value=formatted_results.get('T_l', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_l, кг/м³",
                    value=formatted_results.get('rho_l', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            with col2:
                # Вывод параметров 1-го этажа
                st.subheader("2. Параметры 1-го этажа")
                st.number_input(
                    label="Коэффициент местного сопротивления узла «кабина-шахта» при открытых дверях кабины и шахты на основном посадочном этаже",
                    value=formatted_results.get('xi_l_1_new', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Площадь дверей лифтовой шахты на уровне 1-го этажа, м²",
                    value=formatted_results.get('F_dl_1', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Площадь дверей лифтового холла на уровне 1-го этажа, м²",
                    value=formatted_results.get('F_dr_1', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Массовый расход воздуха на уровне 1-го этажа лифтовой шахты, кг/с",
                    value=formatted_results.get('G_l_1', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            # Вывод параметров (-1)-го-(-N)-го этажей
            st.subheader("3. Параметры (-1)-го-(-N)-го этажей")

            # Создаём пустой список для хранения данных
            floor_data = []

            # Список всех обязательных параметров для проверки
            required_params = [
                'P_l_minus', 'S_dl_minus', 'F_dl_minus', 'S_dr_minus', 'F_dr_minus', 'S_lr_minus', 'delta_G_l_minus'
            ]

            for i in range(1, N + 1):
                try:
                    # Создаём словарь с данными для текущего этажа
                    row_data = {
                        'P_l, Па': results.get(f'P_l_minus_{i}', 0),
                        'S_dl, м³/кг': results.get(f'S_dl_minus_{i}_new', 0),
                        'F_dl, м²': results.get(f'F_dl_minus_{i}', 0),
                        'S_dr, м³/кг': results.get(f'S_dr_minus_{i}_new', 0),
                        'F_dr, м²': results.get(f'F_dr_minus_{i}', 0),
                        'S_lr, м³/кг': results.get(f'S_lr_minus_{i}', 0),
                        'ΔG_l, кг/с': results.get(f'delta_G_l_minus_{i}', 0)
                    }

                    # Проверяем, есть ли хотя бы одно ненулевое значение
                    if all(value == 0 for value in row_data.values() if isinstance(value, (int, float))):
                        continue  # Пропускаем полностью нулевой этаж

                    # Добавляем строку в список
                    floor_data.append(row_data)

                except Exception as e:
                    st.error(f"Ошибка при обработке этажа -{i}: {e}")

            # Создаём итоговый DataFrame
            floor_df = pd.DataFrame(floor_data, index=[f'Этаж -{i}' for i in range(1, N + 1)])
            st.dataframe(floor_df)

            # Вывод итогового расчета
            st.subheader("4. Итоговый расчет")
            st.number_input(
                label="Массовый расход воздуха, подаваемый в лифтовую шахту, кг/с",
                value=formatted_results.get('G_l', 0.0),
                disabled=True,
                format="%.2f"
            )

            # Вывод параметров вентилятора
            st.subheader("5. Параметры вентилятора")
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

#---------------------------------------------------------------------

            # График зависимости массового расхода
            st.subheader("Зависимость массового расхода воздуха от этажа")

            # Создаем словарь для данных графика
            mass_flow_data = {
                'Этаж': [f'Этаж -{i}' for i in range(1, N+1)],
                'Массовый расход, кг/с': [results.get(f'delta_G_l_minus_{i}', np.nan) for i in range(1, N+1)]
            }

            mass_flow_df = pd.DataFrame(mass_flow_data)

            if mass_flow_df.isnull().values.any():
                st.warning("Не все данные для построения графика массового расхода доступны")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
    
                # Строим кривую массового расхода
                ax.plot(
                    mass_flow_df['Этаж'],
                    mass_flow_df['Массовый расход, кг/с'],
                    marker='o',
                    color='blue',
                    linestyle='-',
                    label='Профиль массового расхода'
                )
    
                # Оформляем график
                plt.xticks(rotation=45)
                ax.set_title('Зависимость массового расхода воздуха от этажа')
                ax.set_xlabel('Этаж')
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




#############################################################################################################################################################################################################################################
if scenario == 14:
    st.info("Выбран сценарий 14: приточная противодымная вентиляция:")
    st.text("- в тамбур-шлюзы, расположенные при выходах в незадымляемые лестничные клетки типа Н3 или Н2;")
    st.text("- во внутренние открытые лестницы 2-го типа;")
    st.text("- на входах в атриумы и пассажи с уровней подвальных и цокольных этажей;")
    st.text("- перед лифтовыми холлами подземных автостоянок;")
    st.text("- в тамбур-шлюзы при выходах в вестибюли из незадымляемых лестничных клеток типа Н2, сообщающихся с надземными этажами зданий различного назначения;")
    st.text("- в холлы лифтов, имеющие режим управления «перевозка пожарных подразделений», на цокольных, подвальных, подземных этажах зданий.")

    # Ввод параметров помещения
    st.subheader("1. Параметры воздуха")
    t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
    t_r = st.number_input("Температура воздуха в помещении, °C", value=0, step=1)

    # Ввод параметров тамбур-шлюза
    st.subheader("2. Параметры тамбур-шлюза")
    R = st.number_input("Расположение (0 - надземное, 1 - подземное)", value=0, step=1)
    h_i_minus_i = st.number_input("Уровень отметки пола i(-i)-го этажа относительно уровня отметки пола 1-го этажа, м", value=2.5, step=0.1)
    h_minus_N = st.number_input("Уровень отметки пола нижнего подземного этажа относительно уровня отметки пола 1-го этажа (0 - при надземном расположении), м", value=0.0, step=0.1)
    nu_r_i_minus_i = st.number_input("Минимально допустимая скорость истечения воздуха через одну открытую дверь тамбур-шлюза на уровне i(-i) этажа, м/с", value=1.3, step=0.1)
    b_dr_i_minus_i = st.number_input("Ширина двери тамбур-шлюза на уровне i(-i) этажа, м", value=1.00, step=0.01)
    h_dr_i_minus_i = st.number_input("Высота двери тамбур-шлюза на уровне i(-i) этажа, м", value=2.00, step=0.01)

    # Собираем все входные данные
    input_data = {
        # Параметры помещения
        't_a': t_a, 't_r': t_r,
        # Параметры тамбур-шлюза
        'R': R, 'h_i_minus_i': h_i_minus_i, 'h_minus_N': h_minus_N, 'nu_r_i_minus_i':  nu_r_i_minus_i, 'b_dr_i_minus_i': b_dr_i_minus_i, 'h_dr_i_minus_i': h_dr_i_minus_i 
    }

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_14(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_r, кг/м³",
                    value=formatted_results.get('rho_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            
            with col2:
                # Вывод параметров тамбур-шлюза
                st.subheader("2. Параметры тамбур-шлюза")
                st.number_input(
                    label="Площадь двери тамбур-шлюза на уровне i(-i)-го этажа, м²",
                    value=formatted_results.get('F_dr_i_minus_i', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Массовый расход воздуха, подаваемый в тамбур-шлюз на уровне i(-i)-го этажа, кг/с",
                    value=formatted_results.get('G_r_i_minus_i', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Давление в тамбур-шлюзе на уровне i(-i)-го этажа, Па",
                    value=formatted_results.get('P_r_i_minus_i', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                # Вывод параметров вентилятора
                st.subheader("3. Параметры вентилятора")
                st.number_input(
                    label="Подача вентилятора, м³/ч",
                    value=formatted_results.get('L_v', 0.0),
                    disabled=True,
                    format="%.2f"
                )
            
        except Exception as e:
            st.error(f"Произошла ошибка при расчете: {e}")




#############################################################################################################################################################################################################################################
if scenario == 15:
    st.info("Выбран сценарий 15: приточная противодымная вентиляция:")
    st.text("- в тамбур-шлюзы, отделяющие помещения для хранения автомобилей закрытых надземных и подземных автостоянок от помещений иного назначения;")
    st.text("- в тамбур-шлюзы, отделяющие помещения хранения автомобилей от изолированных рамп подземных автостоянок.")
    
    # Ввод параметров помещения
    st.subheader("1. Параметры воздуха")
    t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
    t_r = st.number_input("Температура воздуха в помещении, °C", value=0, step=1)

    # Ввод параметров тамбур-шлюза
    st.subheader("2. Параметры тамбур-шлюза")
    R = st.number_input("Расположение (0 - надземное, 1 - подземное)", value=0, step=1)
    h_i_minus_i = st.number_input("Уровень отметки пола i(-i)-го этажа относительно уровня отметки пола 1-го этажа, м", value=2.5, step=0.1)
    h_minus_N = st.number_input("Уровень отметки пола нижнего подземного этажа относительно уровня отметки пола 1-го этажа (0 - при надземном расположении), м", value=0.0, step=0.1)
    S_dr_i_minus_i = st.number_input("Характеристика удельного сопротивления воздухопроницанию дверей тамбур-шлюза на уровне i(-i)-го этажа (0 - нет данных), м³/кг", value=0, step=1)
    n_i_minus_i = st.number_input("Количество дверей тамбур-шлюза на уровне i(-i)-го этажа", value=1, step=1)
    b_dr_i_minus_i = st.number_input("Ширина двери тамбур-шлюза на уровне i(-i) этажа, м", value=1.00, step=0.01)
    h_dr_i_minus_i = st.number_input("Высота двери тамбур-шлюза на уровне i(-i) этажа, м", value=2.00, step=0.01)

    # Собираем все входные данные
    input_data = {
        # Параметры помещения
        't_a': t_a, 't_r': t_r,
        # Параметры тамбур-шлюза
        'R': R, 'h_i_minus_i': h_i_minus_i, 'h_minus_N': h_minus_N, 'S_dr_i_minus_i':  S_dr_i_minus_i, 'n_i_minus_i': n_i_minus_i, 'b_dr_i_minus_i': b_dr_i_minus_i, 'h_dr_i_minus_i': h_dr_i_minus_i 
    }

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_15(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_r, кг/м³",
                    value=formatted_results.get('rho_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            
            with col2:
                # Вывод параметров тамбур-шлюза
                st.subheader("2. Параметры тамбур-шлюза")
                st.number_input(
                    label="Площадь двери тамбур-шлюза на уровне i(-i)-го этажа, м²",
                    value=formatted_results.get('F_dr_i_minus_i', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                
                st.number_input(
                    label="Характеристика удельного сопротивления воздухопроницанию дверей тамбур-шлюза на уровне i(-i)-го этажа, м³/кг",
                    value=formatted_results.get('S_dr_i_minus_i_new', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                
                st.number_input(
                    label="Массовый расход воздуха, подаваемый в тамбур-шлюз на уровне i(-i)-го этажа, кг/с",
                    value=formatted_results.get('G_r_i_minus_i', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Давление в тамбур-шлюзе на уровне i(-i)-го этажа, Па",
                    value=formatted_results.get('P_r_i_minus_i', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                # Вывод параметров вентилятора
                st.subheader("3. Параметры вентилятора")
                st.number_input(
                    label="Подача вентилятора, м³/ч",
                    value=formatted_results.get('L_v', 0.0),
                    disabled=True,
                    format="%.2f"
                )
            
        except Exception as e:
            st.error(f"Произошла ошибка при расчете: {e}")




#############################################################################################################################################################################################################################################
if scenario == 16:
    st.info("Выбран сценарий 15: приточная противодымная вентиляция в виде воздушных завес, отделяющих помещения хранения автомобилей от изолированных рамп закрытых надземных и подземных автостоянок.")
    
    # Ввод параметров помещения
    st.subheader("1. Параметры воздуха")
    t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)

    # Ввод параметров воздушной завесы
    st.subheader("2. Параметры воздушной завесы")
    nu_a = st.number_input("Скорость истечения воздуха из соплового аппарата, м/с", value=10.0, step=0.1)
    b = st.number_input("Длина сопла в горизонтальной проекции, м", value=2.5, step=0.1)
    delta = st.number_input("Ширина сопла в горизонтальной проекции, м", value=0.03, step=0.01)

    # Собираем все входные данные
    input_data = {
        # Параметры помещения
        't_a': t_a,
        # Параметры тамбур-шлюза
        'nu_a': nu_a, 'b': b, 'delta': delta 
    }

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_16(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
            
            with col2:
                # Вывод параметров воздушной завесы
                st.subheader("2. Параметры воздушной завесы")
                st.number_input(
                    label="Массовый расход воздуха, подаваемого в сопловой аппарат воздушной завесы, кг/с",
                    value=formatted_results.get('G_a', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                # Вывод параметров вентилятора
                st.subheader("3. Параметры вентилятора")
                st.number_input(
                    label="Подача вентилятора, м³/ч",
                    value=formatted_results.get('L_v', 0.0),
                    disabled=True,
                    format="%.2f"
                )
            
        except Exception as e:
            st.error(f"Произошла ошибка при расчете: {e}")




#############################################################################################################################################################################################################################################
if scenario == 17:
    st.info("Выбран сценарий 17: приточная противодымная вентиляция в тамбур-шлюзы (лифтовые холлы) при выходах из лифтов с режимом управления «пожарная опасность» в цокольные, подвальные, подземные этажи зданий различного назначения.")
    
    # Ввод параметров помещения
    st.subheader("1. Параметры воздуха")
    t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
    t_r = st.number_input("Температура воздуха в помещении, °C", value=0, step=1)

    # Ввод параметров тамбур-шлюза
    st.subheader("2. Параметры тамбур-шлюза")
    R = st.number_input("Расположение (0 - надземное, 1 - подземное)", value=0, step=1)
    h_i_minus_i = st.number_input("Уровень отметки пола i(-i)-го этажа относительно уровня отметки пола 1-го этажа, м", value=2.5, step=0.1)
    h_minus_N = st.number_input("Уровень отметки пола нижнего подземного этажа относительно уровня отметки пола 1-го этажа (0 - при надземном расположении), м", value=0.0, step=0.1)
    S_dr_i_minus_i = st.number_input("Характеристика удельного сопротивления воздухопроницанию дверей тамбур-шлюза на уровне i(-i)-го этажа (0 - нет данных), м³/кг", value=0, step=1)
    n_i_minus_i = st.number_input("Количество дверей тамбур-шлюза на уровне i(-i)-го этажа", value=1, step=1)
    b_dr_i_minus_i = st.number_input("Ширина двери тамбур-шлюза на уровне i(-i) этажа, м", value=1.00, step=0.01)
    h_dr_i_minus_i = st.number_input("Высота двери тамбур-шлюза на уровне i(-i) этажа, м", value=2.00, step=0.01)
    S_dl_i_minus_i = st.number_input("Характеристика удельного сопротивления воздухопроницанию дверей лифтовой шахты на уровне i-го (минус i-го) (0 - нет данных), м³/кг", value=0, step=1)
    m_i_minus_i = st.number_input("Количество дверей лифтовой шахты на уровне i(-i)-го этажа", value=1, step=1)
    b_dl_i_minus_i = st.number_input("Ширина двери лифтовой шахты на уровне i(-i) этажа, м", value=1.00, step=0.01)
    h_dl_i_minus_i = st.number_input("Высота двери лифтовой шахты на уровне i(-i) этажа, м", value=2.00, step=0.01)    

    # Собираем все входные данные
    input_data = {
        # Параметры помещения
        't_a': t_a, 't_r': t_r,
        # Параметры тамбур-шлюза
        'R': R, 'h_i_minus_i': h_i_minus_i, 'h_minus_N': h_minus_N, 'S_dr_i_minus_i':  S_dr_i_minus_i, 'n_i_minus_i': n_i_minus_i, 'b_dr_i_minus_i': b_dr_i_minus_i, 'h_dr_i_minus_i': h_dr_i_minus_i,
        'S_dl_i_minus_i':  S_dl_i_minus_i, 'm_i_minus_i': m_i_minus_i, 'b_dl_i_minus_i': b_dl_i_minus_i, 'h_dl_i_minus_i': h_dl_i_minus_i
    }

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_17(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_r, кг/м³",
                    value=formatted_results.get('rho_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            
            with col2:
                # Вывод параметров тамбур-шлюза
                st.subheader("2. Параметры тамбур-шлюза")
                st.number_input(
                    label="Площадь двери тамбур-шлюза на уровне i(-i)-го этажа, м²",
                    value=formatted_results.get('F_dr_i_minus_i', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                
                st.number_input(
                    label="Характеристика удельного сопротивления воздухопроницанию дверей тамбур-шлюза на уровне i(-i)-го этажа, м³/кг",
                    value=formatted_results.get('S_dr_i_minus_i_new', 0.0),
                    disabled=True,
                    format="%.2f"
                )

                st.number_input(
                    label="Площадь двери лифтовой шахты на уровне i(-i)-го этажа, м²",
                    value=formatted_results.get('F_dl_i_minus_i', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                
                st.number_input(
                    label="Характеристика удельного сопротивления воздухопроницанию дверей лифтовой шахты на уровне i(-i)-го этажа, м³/кг",
                    value=formatted_results.get('S_dl_i_minus_i_new', 0.0),
                    disabled=True,
                    format="%.2f"
                )

                st.number_input(
                    label="Массовый расход воздуха, подаваемый в тамбур-шлюз на уровне i(-i)-го этажа, кг/с",
                    value=formatted_results.get('G_r_i_minus_i', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Давление в тамбур-шлюзе на уровне i(-i)-го этажа, Па",
                    value=formatted_results.get('P_r_i_minus_i', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                # Вывод параметров вентилятора
                st.subheader("3. Параметры вентилятора")
                st.number_input(
                    label="Подача вентилятора, м³/ч",
                    value=formatted_results.get('L_v', 0.0),
                    disabled=True,
                    format="%.2f"
                )
            
        except Exception as e:
            st.error(f"Произошла ошибка при расчете: {e}")




#############################################################################################################################################################################################################################################
if scenario == 18:
    st.info("Выбран сценарий 18: приточная противодымная вентиляция в помещения зон безопасности в количестве, достаточном для его истечения через одну открытую дверь с минимально допустимой скоростью.")

    # Ввод параметров помещения
    st.subheader("1. Параметры воздуха")
    t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
    t_r = st.number_input("Температура воздуха в помещении, °C", value=0, step=1)

    # Ввод параметров помещения зоны безопасности
    st.subheader("2. Параметры помещения зоны безопасности")
    R = st.number_input("Расположение (0 - надземное, 1 - подземное)", value=0, step=1)
    h_i_minus_i = st.number_input("Уровень отметки пола i(-i)-го этажа относительно уровня отметки пола 1-го этажа, м", value=2.5, step=0.1)
    h_minus_N = st.number_input("Уровень отметки пола нижнего подземного этажа относительно уровня отметки пола 1-го этажа (0 - при надземном расположении), м", value=0.0, step=0.1)
    nu_sf_i_minus_i = st.number_input("Минимально допустимая скорость истечения воздуха через одну открытую дверь помещения зоны безопасности на уровне i(-i) этажа, м/с", value=1.5, step=0.1)
    b_dsf_i_minus_i = st.number_input("Ширина двери помещения зоны безопасности на уровне i(-i) этажа, м", value=1.00, step=0.01)
    h_dsf_i_minus_i = st.number_input("Высота двери помещения зоны безопасности на уровне i(-i) этажа, м", value=2.00, step=0.01)

    # Собираем все входные данные
    input_data = {
        # Параметры помещения
        't_a': t_a, 't_r': t_r,
        # Параметры тамбур-шлюза
        'R': R, 'h_i_minus_i': h_i_minus_i, 'h_minus_N': h_minus_N, 'nu_sf_i_minus_i':  nu_sf_i_minus_i, 'b_dsf_i_minus_i': b_dsf_i_minus_i, 'h_dsf_i_minus_i': h_dsf_i_minus_i 
    }

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_18(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_r, кг/м³",
                    value=formatted_results.get('rho_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            
            with col2:
                # Вывод параметров помещения зоны безопасности
                st.subheader("2. Параметры помещения зоны безопасности")
                st.number_input(
                    label="Площадь двери помещения зоны безопасности на уровне i(-i)-го этажа, м²",
                    value=formatted_results.get('F_dsf_i_minus_i', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Массовый расход воздуха, подаваемый в помещение зоны безопасности на уровне i(-i)-го этажа, кг/с",
                    value=formatted_results.get('G_sf_i_minus_i', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Давление в помещении зоны безопасности на уровне i(-i)-го этажа, Па",
                    value=formatted_results.get('P_sf_i_minus_i', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                # Вывод параметров вентилятора
                st.subheader("3. Параметры вентилятора")
                st.number_input(
                    label="Подача вентилятора, м³/ч",
                    value=formatted_results.get('L_v', 0.0),
                    disabled=True,
                    format="%.2f"
                )
            
        except Exception as e:
            st.error(f"Произошла ошибка при расчете: {e}")




#############################################################################################################################################################################################################################################
if scenario == 19:
    st.info("Выбран сценарий 19: приточная противодымная вентиляция в помещения зон безопасности (подача дополнительно нагреваемого наружного воздуха в защищаемые помещения при их закрытых дверях).")
    
    # Ввод параметров воздуха
    st.subheader("1. Параметры воздуха")
    t_a = st.number_input("Температура наружного воздуха, °C", value=-58, step=1)
    t_r = st.number_input("Температура воздуха в помещении, °C", value=0, step=1)
    t_sf = st.number_input("Температура подогреваемого воздуха, °C", value=18, step=1)    

    # Ввод параметров тамбур-шлюза
    st.subheader("2. Параметры помещения зоны безопасности")
    R = st.number_input("Расположение (0 - надземное, 1 - подземное)", value=0, step=1)
    h_i_minus_i = st.number_input("Уровень отметки пола i(-i)-го этажа относительно уровня отметки пола 1-го этажа, м", value=2.5, step=0.1)
    h_minus_N = st.number_input("Уровень отметки пола нижнего подземного этажа относительно уровня отметки пола 1-го этажа (0 - при надземном расположении), м", value=0.0, step=0.1)
    S_dsf_i_minus_i = st.number_input("Характеристика удельного сопротивления воздухопроницанию дверей помещения зоны безопасности на уровне i(-i)-го этажа (0 - нет данных), м³/кг", value=0, step=1)
    n_i_minus_i = st.number_input("Количество дверей помещения зоны безопасности на уровне i(-i)-го этажа", value=1, step=1)
    b_dsf_i_minus_i = st.number_input("Ширина двери помещения зоны безопасности на уровне i(-i) этажа, м", value=1.00, step=0.01)
    h_dsf_i_minus_i = st.number_input("Высота двери помещения зоны безопасности на уровне i(-i) этажа, м", value=2.00, step=0.01)

    # Собираем все входные данные
    input_data = {
        # Параметры помещения
        't_a': t_a, 't_r': t_r, 't_sf': t_sf, 
        # Параметры тамбур-шлюза
        'R': R, 'h_i_minus_i': h_i_minus_i, 'h_minus_N': h_minus_N, 'S_dsf_i_minus_i':  S_dsf_i_minus_i, 'n_i_minus_i': n_i_minus_i, 'b_dsf_i_minus_i': b_dsf_i_minus_i, 'h_dsf_i_minus_i': h_dsf_i_minus_i
    }

    # Выполняем расчет
    if st.button("Выполнить расчет"):
        try:
            # Выполняем расчет и сохраняем результаты в состояние
            results_state.results = calculate_scenario_19(**input_data)
            results_state.calculated = True
            results = results_state.results
        
            # Вывод результатов расчета
            st.subheader("Результаты расчета")

            # Преобразуем все результаты в float
            formatted_results = {key: float(value) for key, value in results.items()}      

            col1, col2 = st.columns(2)
            with col1:
                # Вывод параметров воздуха
                st.subheader("1. Параметры воздуха")
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
                    label="Температура воздуха в помещении, К",
                    value=formatted_results.get('T_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_r, кг/м³",
                    value=formatted_results.get('rho_r', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура воздуха в лестнично-лифтовых узлах, К",
                    value=formatted_results.get('T_sl', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_sl, кг/м³",
                    value=formatted_results.get('rho_sl', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Температура подогреваемого воздуха, К",
                    value=formatted_results.get('T_sl', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Плотность воздуха при температуре T_sf, кг/м³",
                    value=formatted_results.get('rho_sf', 0.0),
                    disabled=True,
                    format="%.2f"
                )

            
            with col2:
                # Вывод параметров помещения зоны безопасности
                st.subheader("2. Параметры помещения зоны безопасности")
                st.number_input(
                    label="Площадь двери помещения зоны безопасности на уровне i(-i)-го этажа, м²",
                    value=formatted_results.get('F_dsf_i_minus_i', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                
                st.number_input(
                    label="Характеристика удельного сопротивления воздухопроницанию дверей помещения зоны безопасности на уровне i(-i)-го этажа, м³/кг",
                    value=formatted_results.get('S_dsf_i_minus_i_new', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                
                st.number_input(
                    label="Массовый расход воздуха, подаваемый в помещение зоны безопасности на уровне i(-i)-го этажа, кг/с",
                    value=formatted_results.get('G_sf_i_minus_i', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                st.number_input(
                    label="Давление в помещении зоны безопасности на уровне i(-i)-го этажа, Па",
                    value=formatted_results.get('P_sf_i_minus_i', 0.0),
                    disabled=True,
                    format="%.2f"
                )
                # Вывод параметров вентилятора
                st.subheader("3. Параметры вентилятора")
                st.number_input(
                    label="Подача вентилятора, м³/ч",
                    value=formatted_results.get('L_v', 0.0),
                    disabled=True,
                    format="%.2f"
                )
            
        except Exception as e:
            st.error(f"Произошла ошибка при расчете: {e}")









            

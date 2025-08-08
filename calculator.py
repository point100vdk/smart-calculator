import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# Настройки страницы
st.set_page_config(
    page_title="💰 Продвинутый калькулятор сложных процентов",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Адаптивные стили для светлой/темной темы
st.markdown("""
<style>
    /* Общие стили */
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* Адаптивные стили для светлой и темной темы */
    :root {
        --background-color: #ffffff;
        --text-color: #000000;
        --card-bg: #f8f9fa;
        --border-color: #e0e0e0;
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #0e1117;
            --text-color: #f0f2f6;
            --card-bg: #1e2130;
            --border-color: #2a2e3e;
        }
    }
    
    /* Стили компонентов */
    .stMetric {
        background-color: var(--card-bg);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid var(--border-color);
        color: var(--text-color);
    }
    
    .stMetric label {
        color: var(--text-color) !important;
    }
    
    .stNumberInput, .stSelectbox, .stTextInput {
        background-color: var(--card-bg);
        color: var(--text-color);
    }
    
    .st-bb {
        border-bottom: 1px solid var(--border-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: var(--card-bg) !important;
        color: var(--text-color) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4e79a7 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

class CompoundInterestCalculator:
    def __init__(self, params):
        self.params = params
        self.principal = params['initial_investment']
        self.monthly_contribution = params['monthly_contribution']
        self.yearly_contribution = params['yearly_contribution']
        self.interest_rate = params['interest_rate'] / 100
        self.years = params['investment_period']
        self.compounding_freq = params['compounding_freq']
        self.inflation_rate = params['inflation_rate'] / 100
        self.tax_rate = params['tax_rate'] / 100
        self.currency = params['currency']
        
    def calculate(self):
        periods = self.years * self.compounding_freq
        period_rate = self.interest_rate / self.compounding_freq
        balance_nominal = self.principal
        balance_real = self.principal
        results = []
        total_contributions = self.principal
        total_interest = 0
        total_taxes = 0
        
        for year in range(1, self.years + 1):
            yearly_contributions = self.yearly_contribution + self.monthly_contribution * 12
            year_start_balance = balance_nominal
            
            for period in range(self.compounding_freq):
                period_contribution = yearly_contributions / self.compounding_freq
                balance_nominal += period_contribution
                total_contributions += period_contribution
                
                interest = balance_nominal * period_rate
                tax = interest * self.tax_rate
                balance_nominal += interest - tax
                total_interest += interest
                total_taxes += tax
            
            inflation_factor = (1 + self.inflation_rate) ** year
            balance_real = balance_nominal / inflation_factor
            
            results.append({
                'Year': year,
                'Start Balance': year_start_balance,
                'Contributions': yearly_contributions,
                'Interest Earned': total_interest - sum(r.get('Interest Earned', 0) for r in results),
                'Taxes Paid': total_taxes - sum(r.get('Taxes Paid', 0) for r in results),
                'End Balance (Nominal)': balance_nominal,
                'End Balance (Real)': balance_real,
                'Inflation Factor': inflation_factor
            })
        
        df = pd.DataFrame(results)
        summary = {
            'Final Amount (Nominal)': balance_nominal,
            'Final Amount (Real)': balance_real,
            'Total Contributions': total_contributions,
            'Total Interest': total_interest,
            'Total Taxes': total_taxes,
            'CAGR': (balance_nominal / self.principal) ** (1 / self.years) - 1
        }
        
        return df, summary

def format_currency(value, currency):
    return f"{value:,.0f} {currency}"

def main():
    st.title("💰 Калькулятор сложных процентов")
    st.markdown("""
    <div style="background-color: var(--card-bg); padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid var(--border-color);">
        Рассчитайте рост ваших инвестиций с учетом пополнений, инфляции и налогов. 
        Просто введите параметры ниже и нажмите "Рассчитать".
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("⚙️ Параметры инвестирования", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            initial_investment = st.number_input(
                "Начальные инвестиции", 
                min_value=0, 
                value=100000,
                step=1000
            )
            
            monthly_contribution = st.number_input(
                "Ежемесячное пополнение", 
                min_value=0, 
                value=10000,
                step=1000
            )
            
            interest_rate = st.number_input(
                "Годовая процентная ставка (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=10.0,
                step=0.1,
                format="%.1f"
            )
            
        with col2:
            investment_period = st.number_input(
                "Срок инвестирования (лет)", 
                min_value=1, 
                max_value=100, 
                value=10,
                step=1
            )
            
            yearly_contribution = st.number_input(
                "Годовое пополнение", 
                min_value=0, 
                value=0,
                step=1000
            )
            
            inflation_rate = st.number_input(
                "Ожидаемая инфляция (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=5.0,
                step=0.1,
                format="%.1f"
            )
            
        with col3:
            compounding_freq = st.selectbox(
                "Частота начисления процентов",
                options=[12, 4, 1],
                format_func=lambda x: {
                    12: "Ежемесячно", 
                    4: "Ежеквартально", 
                    1: "Ежегодно"
                }[x],
                index=0
            )
            
            tax_rate = st.number_input(
                "Налоговая ставка на доход (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=13.0,
                step=0.1,
                format="%.1f"
            )
            
            currency = st.selectbox(
                "Валюта",
                options=["₽ Рубли", "$ Доллары", "€ Евро", "£ Фунты"],
                index=0
            )
    
    params = {
        'initial_investment': initial_investment,
        'monthly_contribution': monthly_contribution,
        'yearly_contribution': yearly_contribution,
        'interest_rate': interest_rate,
        'investment_period': investment_period,
        'compounding_freq': compounding_freq,
        'inflation_rate': inflation_rate,
        'tax_rate': tax_rate,
        'currency': currency.split()[0]
    }
    
    if st.button("Рассчитать", type="primary", use_container_width=True):
        calculator = CompoundInterestCalculator(params)
        results_df, summary = calculator.calculate()
        
        # Отображение результатов
        st.markdown("---")
        st.subheader("📊 Основные результаты")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Итоговая сумма (номинал)", 
                format_currency(summary['Final Amount (Nominal)'], params['currency'])
            )
            
        with col2:
            st.metric(
                "Итоговая сумма (реальная)", 
                format_currency(summary['Final Amount (Real)'], params['currency']),
                delta=f"{inflation_rate:.1f}% инфляция ежегодно"
            )
            
        with col3:
            st.metric(
                "Среднегодовой рост (CAGR)", 
                f"{summary['CAGR']*100:.1f}%"
            )
        
        # Вкладки с подробной информацией
        tab1, tab2, tab3 = st.tabs(["📈 График роста", "🧩 Состав суммы", "📋 Подробная таблица"])
        
        with tab1:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=results_df['Year'], 
                y=results_df['End Balance (Nominal)'],
                name='Номинальная стоимость',
                line=dict(color='#4e79a7', width=3),
                hovertemplate="Год %{x}<br>%{y:,.0f} " + params['currency']
            ))
            
            fig.add_trace(go.Scatter(
                x=results_df['Year'], 
                y=results_df['End Balance (Real)'],
                name='Реальная стоимость (с инфляцией)',
                line=dict(color='#e15759', width=3),
                hovertemplate="Год %{x}<br>%{y:,.0f} " + params['currency']
            ))
            
            fig.update_layout(
                title='Динамика роста инвестиций',
                xaxis_title='Годы',
                yaxis_title=f"Сумма, {params['currency']}",
                hovermode='x unified',
                template='plotly_white' if st._config.get_option("theme.base") == "light" else 'plotly_dark',
                height=500,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            labels = ['Начальные инвестиции', 'Пополнения', 'Проценты (после налогов)']
            values = [
                params['initial_investment'],
                summary['Total Contributions'] - params['initial_investment'],
                summary['Total Interest'] - summary['Total Taxes']
            ]
            
            fig = go.Figure(go.Pie(
                labels=labels,
                values=values,
                hole=.4,
                marker_colors=['#4e79a7','#59a14f','#f28e2b'],
                textinfo='percent+value',
                texttemplate="%{label}<br>%{value:,.0f} " + params['currency'] + " (%{percent})",
                hoverinfo='label+percent+value'
            ))
            
            fig.update_layout(
                title='Состав итоговой суммы',
                height=500,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            display_df = results_df.copy()
            display_df.columns = [
                'Год', 'Начало года', 'Пополнения', 'Начисленные проценты', 
                'Уплачено налогов', 'Конец года (ном.)', 'Конец года (реал.)', 'Фактор инфляции'
            ]
            
            # Форматирование чисел
            for col in display_df.columns[1:-1]:
                display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f} {params['currency']}")
            display_df['Фактор инфляции'] = display_df['Фактор инфляции'].apply(lambda x: f"{x:.2f}")
            
            st.dataframe(
                display_df,
                height=500,
                use_container_width=True
            )
            
            # Кнопка экспорта
            csv = results_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Экспорт в CSV",
                data=csv,
                file_name=f"investment_calculator_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv',
                use_container_width=True
            )
        
        # Дополнительная информация
        with st.expander("🔍 Детали расчета"):
            st.markdown("""
            **Формулы расчета:**
            - **Сложные проценты:** `Конечная сумма = P*(1 + r/n)^(n*t) + PMT*[((1 + r/n)^(n*t) - 1]/(r/n)`
            - **Реальная стоимость:** `Номинальная сумма / (1 + инфляция)^лет`
            - **CAGR:** `(Конечная сумма / Начальная сумма)^(1/лет) - 1`
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Общие пополнения", format_currency(
                    summary['Total Contributions'] - params['initial_investment'], 
                    params['currency']
                ))
                st.metric("Общие налоги", format_currency(
                    summary['Total Taxes'], 
                    params['currency']
                ))
                
            with col2:
                st.metric("Общий процентный доход", format_currency(
                    summary['Total Interest'], 
                    params['currency']
                ))
                st.metric("Чистый доход (после налогов)", format_currency(
                    summary['Total Interest'] - summary['Total Taxes'], 
                    params['currency']
                ))
    else:
        st.info("Введите параметры инвестирования и нажмите кнопку 'Рассчитать'")

if __name__ == "__main__":
    main()

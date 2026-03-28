import streamlit as st
import pandas as pd
import numpy as np

np.random.seed(42)

def generate_salary(level):
    ranges = {
        'Entry': (30000, 50000),
        'Junior': (45000, 75000),
        'Senior': (70000, 110000),
        'Manager': (100000, 150000),
        'Director': (140000, 220000)
    }
    low, high = ranges[level]
    return np.random.randint(low, high)

def generate_market_salary(level):
    ranges = {
        'Entry':    (35000, 55000),
        'Junior':   (44000, 80000),
        'Senior':   (75000, 115000),
        'Manager':  (105000, 155000),
        'Director': (145000, 225000)
    }
    low, high = ranges[level]
    return np.random.randint(low, high)

countries = ['Australia', 'Korea', 'Singapore', 'USA', 'UK']
levels = ['Entry', 'Junior', 'Senior', 'Manager', 'Director']
n = 625

internal_data = {
    'country': np.random.choice(countries, n),
    'level': np.random.choice(levels, n)
}
internal_data['salary'] = [generate_salary(l) for l in internal_data['level']]

market_data = {
    'country': np.random.choice(countries, n),
    'level': np.random.choice(levels, n)
}
market_data['salary'] = [generate_market_salary(l) for l in market_data['level']]

internal_df = pd.DataFrame(internal_data)
market_df = pd.DataFrame(market_data)

internal = (
    internal_df.groupby(['country', 'level'])['salary']
    .agg([
        ('in_p25', lambda x: x.quantile(0.25)),
        ('in_median', 'median'),
        ('in_p75', lambda x: x.quantile(0.75))
    ])
    .astype(int)
    .reindex(levels, level=1)
    .reset_index()
)

market = (
    market_df.groupby(['country', 'level'])['salary']
    .agg([
        ('mk_p25', lambda x: x.quantile(0.25)),
        ('mk_median', 'median'),
        ('mk_p75', lambda x: x.quantile(0.75))
    ])
    .astype(int)
    .reindex(levels, level=1)
    .reset_index()
)

combined = internal.merge(market, on=['country', 'level'])
combined['recommended'] = (
        (combined['in_median'] + combined['mk_median']) / 2
).round(-2).astype(int)

# Streamlit UI
st.title('Compensation Benchmarking Tool')
st.markdown('Compare internal and market salary data to get recommended compensation.')

col1, col2 = st.columns(2)
with col1:
    country = st.selectbox('Select Country', countries)
with col2:
    level = st.selectbox('Select Level', levels)

result = combined[(combined['country'] == country) & (combined['level'] == level)].copy()

if not result.empty:
    internal_median = result['in_median'].values[0]
    market_median = result['mk_median'].values[0]
    recommended = result['recommended'].values[0]
    source = 'Market' if market_median > internal_median else 'Internal'
    variance = market_median - internal_median
    variance_pct = variance / internal_median * 100

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label='Internal Median', value=f'${internal_median:,.0f}')
    with col2:
        st.metric(label='Market Median', value=f'${market_median:,.0f}',
                  delta=f'{variance_pct:+.1f}%')
    with col3:
        st.metric(label='Recommended', value=f'${recommended:,.0f}',
                  delta=source)

    st.divider()
    st.caption(f'Variance: ${variance:,.0f} ({variance_pct:+.1f}%) — Based on {source} data')


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
    internal_median = result['median'].values[0]
    market_median = result['market_median'].values[0]
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

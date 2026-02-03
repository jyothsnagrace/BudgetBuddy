import streamlit as st

def page_config():
    APP_TITLE = 'Budget Buddy'
    APP_SUB_TITLE = 'Authors: Leela Josna Kona, Alyssa Sharma'
    #st.set_option('deprecation.showPyplotGlobalUse', False)
    st.set_page_config(page_title=APP_TITLE, page_icon=":heavy_dollar_sign", layout="wide")
    st.title(f":calendar: {APP_TITLE} :heavy_dollar_sign:")
    st.markdown(f'<p style="text-align: right; color: gray; font-size: 12px;">{APP_SUB_TITLE}</p>', unsafe_allow_html=True)
    st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)



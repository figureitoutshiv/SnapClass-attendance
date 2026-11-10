import streamlit as st
def subject_card(name, section, code, stats=None, footer_callback=None):
    html = f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
        <h3>{name}</h3>
        <p><strong>Code:</strong> {code}</p>
        <p><strong>Section:</strong> {section}</p>
        {''.join(f'<p><strong>{icon} {label}:</strong> {value}</p>' for icon, label, value in stats) if stats else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()
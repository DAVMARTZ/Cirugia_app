import streamlit as st
import pandas as pd

def cargar_usuarios():
    return pd.read_csv("data/usuarios.csv")

def login():
    # Centering the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center; background-color: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);">
                <h1 style="margin-bottom: 10px;">🏥 CirugíaApp</h1>
                <p style="color: #64748b; margin-bottom: 30px;">Gestión Quirúrgica Profesional</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div style='background-color: white; padding: 30px; border-radius: 20px; margin-top: -20px;'>", unsafe_allow_html=True)
            usuario = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
            clave = st.text_input("🔑 Contraseña", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Ingresar al Sistema"):
                usuarios = cargar_usuarios()
                validado = usuarios[
                    (usuarios["usuario"] == usuario) &
                    (usuarios["clave"] == clave)
                ]

                if not validado.empty:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = usuario
                    st.session_state["rol"] = validado.iloc[0]["rol"]
                    st.success("Acceso concedido")
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas. Intente de nuevo.")
            st.markdown("</div>", unsafe_allow_html=True)

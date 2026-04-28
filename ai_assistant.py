import json
import pandas as pd
from typing import Dict, Any
import streamlit as st
from groq import Groq

class ClinicalAIAssistant:
    """
    Asistente AI para análisis de historias clínicas usando Groq (GRATIS)
    
    La API key NUNCA se hardcodea. Se obtiene de:
    1. st.secrets (desarrollo local con .streamlit/secrets.toml y Streamlit Cloud)
    2. Variable de entorno GROQ_API_KEY
    """
    
    def __init__(self, api_key: str = None):
        """
        Inicializa el asistente AI con Groq
        
        Args:
            api_key: API key de Groq (opcional). Si no se proporciona,
                    se busca en st.secrets o en variable de entorno.
        """
        # Si no se pasa como parámetro, buscar en secrets o variable de entorno
        if api_key is None:
            api_key = self._get_api_key()
        
        if not api_key:
            raise ValueError(
                "❌ API Key de Groq no configurada.\n\n"
                "🔧 Para configurarla:\n"
                "1. Crea el archivo .streamlit/secrets.toml con:\n"
                "   groq_api_key = 'gsk_tu_key_aqui'\n\n"
                "2. O configura la variable de entorno GROQ_API_KEY\n\n"
                "3. Obtén tu API key gratis en: https://console.groq.com"
            )
        
        self.client = Groq(api_key=api_key)
        
        # Modelos actualizados y disponibles (Julio 2024) - Todos GRATUITOS
        self.available_models = {
            "llama-3.1-8b-instant": "🟢 Llama 3.1 8B (Recomendado - Rápido y eficiente)",
            "llama-3.1-70b-versatile": "🟡 Llama 3.1 70B (Más potente, más lento)",
            "mixtral-8x7b-32768": "🟢 Mixtral 8x7B (Excelente en español)",
            "gemma2-9b-it": "🟢 Gemma 2 9B (Google, rápido)"
        }
    
    def _get_api_key(self) -> str:
        """
        Obtiene la API key desde diferentes fuentes de forma segura
        
        Returns:
            API key o None si no se encuentra
        """
        # Fuente 1: Streamlit secrets (local o cloud)
        try:
            return st.secrets["groq_api_key"]
        except:
            pass
        
        # Fuente 2: Variable de entorno del sistema
        import os
        env_key = os.environ.get("GROQ_API_KEY")
        if env_key:
            return env_key
        
        return None
    
    def prepare_clinical_context(self, paciente_info: Dict, cirugias: pd.DataFrame, 
                                 historia: pd.DataFrame) -> str:
        """
        Prepara el contexto clínico estructurado para enviar al modelo AI
        """
        context = f"""
┌─────────────────────────────────────────┐
│ DATOS DEL PACIENTE                       │
└─────────────────────────────────────────┘
• Nombre: {paciente_info.get('nombre_paciente', 'No disponible')}
• Documento: {paciente_info.get('tipo_documento', '')} {paciente_info.get('numero_documento', '')}
• Sexo: {paciente_info.get('sexo', 'No disponible')}
• Fecha nacimiento: {paciente_info.get('fecha_nacimiento', 'No disponible')}
• Institución: {paciente_info.get('institucion', 'No disponible')}
"""
        
        if not cirugias.empty:
            context += """
┌─────────────────────────────────────────┐
│ CIRUGÍAS REALIZADAS                     │
└─────────────────────────────────────────┘"""
            
            for idx, (_, row) in enumerate(cirugias.iterrows(), 1):
                checklist_status = "✅ COMPLETO" if self._checklist_completo(row) else "❌ INCOMPLETO"
                pdf_status = "✅" if str(row.get('pdf_checklist', '')).strip() else "❌"
                
                context += f"""

🔹 Cirugía #{int(row.get('id', idx))}
   📅 Fecha: {row.get('fecha_cirugia', 'No disponible')}
   🔪 Procedimiento: {row.get('procedimiento', 'No disponible')}
   📋 Checklist: {checklist_status}
   📄 PDF generado: {pdf_status}
"""
                
                # Datos preoperatorios
                preop_data = self._parse_json_safe(row.get('datos_preop'))
                if preop_data:
                    context += """
   ▸ PREOPERATORIO:
"""
                    context += f"     • Identidad confirmada: {'✅' if preop_data.get('identificacion_confirmada') else '❌'}\n"
                    context += f"     • Alergias: {preop_data.get('tiene_alergias', 'No especificado')}\n"
                    if preop_data.get('tiene_alergias') == 'Sí':
                        context += f"     • Detalle alergias: {preop_data.get('detalle_alergias', 'No detallado')}\n"
                    context += f"     • Sitio quirúrgico: {preop_data.get('sitio_quirurgico', 'No especificado')}\n"
                    context += f"     • Consentimiento informado: {'✅' if preop_data.get('consentimiento_informado') else '❌'}\n"
                    context += f"     • Historia clínica revisada: {'✅' if preop_data.get('historia_clinica_revisada') else '❌'}\n"
                    context += f"     • Ayuno adecuado: {'✅' if preop_data.get('ayuno_adecuado') else '❌'}\n"
                    context += f"     • Sitio preparado: {'✅' if preop_data.get('sitio_preparado') else '❌'}\n"
                    context += f"     • Instrumental verificado: {'✅' if preop_data.get('instrumental_verificado') else '❌'}\n"
                    context += f"     • Equipo utilizado: {preop_data.get('equipo_utilizado', 'No especificado')}\n"
                    context += f"     • Cantidad instrumentos: {preop_data.get('cantidad_instrumentos', 'No especificado')}\n"
                    context += f"     • Esterilización: {preop_data.get('fecha_esterilizacion', 'No disponible')}\n"
                    context += f"     • Vencimiento equipo: {preop_data.get('fecha_vencimiento', 'No disponible')}\n"
                
                # Datos intraoperatorios
                intraop_data = self._parse_json_safe(row.get('datos_intraop'))
                if intraop_data:
                    context += """
   ▸ INTRAOPERATORIO:
"""
                    context += f"     • Esterilidad del campo: {'✅' if intraop_data.get('esterilidad_campo') else '❌'}\n"
                    context += f"     • Posición paciente: {intraop_data.get('posicion_paciente', 'No especificada')}\n"
                    context += f"     • Horario: {intraop_data.get('hora_inicio', '?')} - {intraop_data.get('hora_fin', '?')}\n"
                    context += f"     • Medicación: {intraop_data.get('medicacion_tipo', 'No')} / Dosis: {intraop_data.get('medicacion_dosis', 'No')}\n"
                    context += f"     • Gasas: inicio={intraop_data.get('gasas_inicio', '?')}, cierre={intraop_data.get('gasas_cierre', '?')}\n"
                    context += f"     • Compresas: inicio={intraop_data.get('compresas_inicio', '?')}, cierre={intraop_data.get('compresas_cierre', '?')}\n"
                    context += f"     • Conteo correcto: {'✅' if intraop_data.get('conteo_correcto') else '❌'}\n"
                    context += f"     • Equipos funcionando: {'✅' if intraop_data.get('equipos_funcionando') else '❌'}\n"
                    if intraop_data.get('hubo_incidencias') == 'Sí':
                        context += f"     • ⚠️ INCIDENCIAS: {intraop_data.get('detalle_incidencias', 'No detalladas')}\n"
                
                # Datos postoperatorios
                postop_data = self._parse_json_safe(row.get('datos_postop'))
                if postop_data:
                    context += """
   ▸ POSTOPERATORIO:
"""
                    context += f"     • Indicaciones postop: {'✅' if postop_data.get('indicaciones_ok') else '❌'}\n"
                    context += f"     • Comunicación recuperación: {'✅' if postop_data.get('comunicacion_recuperacion_ok') else '❌'}\n"
                    context += f"     • Medicamentos registrados: {'✅' if postop_data.get('registro_medicamentos_ok') else '❌'}\n"
                    context += f"     • Drenajes/Sondas: {'✅' if postop_data.get('drenajes_ok') else '❌'}\n"
                    context += f"     • Control del dolor: {'✅' if postop_data.get('dolor_ok') else '❌'}\n"
                    context += f"     • Control conciencia: {'✅' if postop_data.get('conciencia_ok') else '❌'}\n"
                    context += f"     • Signos vitales: {postop_data.get('signos_vitales', 'No registrados')}\n"
        
        if not historia.empty:
            context += """
┌─────────────────────────────────────────┐
│ HISTORIAL CLÍNICO                       │
└─────────────────────────────────────────┘"""
            
            for idx, (_, row) in enumerate(historia.iterrows(), 1):
                context += f"""

📝 Registro #{int(row.get('id', idx))}
   📅 Fecha: {row.get('fecha_registro', 'No disponible')}
   📋 Tipo: {row.get('tipo_registro', 'No disponible')}
   🔍 Motivo: {row.get('motivo', 'No disponible')}
   💉 Diagnóstico: {row.get('diagnostico', 'No disponible')}
   📖 Antecedentes: {row.get('antecedentes', 'No especificados')}
   👀 Observaciones: {row.get('observaciones', 'No especificadas')}
"""
        
        context += "\n" + "─" * 50 + "\n"
        return context
    
    def _checklist_completo(self, row: pd.Series) -> bool:
        """Verifica si el checklist quirúrgico está completo"""
        return all([
            row.get('preop_completa', False),
            row.get('firmas_preop_completas', False),
            row.get('intraop_completa', False),
            row.get('postop_completa', False)
        ])
    
    def _parse_json_safe(self, value):
        """Parsea JSON de forma segura sin lanzar excepciones"""
        if pd.isna(value) or value == "":
            return None
        try:
            if isinstance(value, str):
                return json.loads(value)
            elif isinstance(value, dict):
                return value
            return None
        except:
            return None
    
    def ask_question(self, context: str, question: str, model: str = "llama-3.1-8b-instant") -> Dict[str, Any]:
        """
        Realiza una pregunta al modelo AI sobre el contexto clínico
        
        Args:
            context: Contexto clínico estructurado
            question: Pregunta del profesional de salud
            model: Modelo de Groq a utilizar
            
        Returns:
            Diccionario con respuesta, tokens usados, modelo y proveedor
        """
        if not self.client:
            return {"error": "Cliente no inicializado. Verifica tu API key.", "response": None}
        
        system_prompt = """Eres un asistente médico especializado en análisis de historias clínicas y checklists de cirugía segura.
Tu función es ayudar a profesionales de la salud a analizar información clínica de pacientes.

REGLAS IMPORTANTES:
1. Responde SIEMPRE en español con lenguaje médico profesional pero comprensible
2. NO des consejos médicos que sustituyan el juicio profesional
3. Si no encuentras información suficiente en el contexto, indícalo claramente
4. Sé conciso pero completo en tus respuestas
5. Cita datos específicos del contexto clínico al responder
6. Si detectas patrones anormales, señálalos pero NO hagas diagnósticos
7. Usa viñetas y estructura clara para organizar la información
8. Destaca cualquier alerta de seguridad del paciente (alergias no verificadas, consentimientos faltantes, incidentes)
9. Recuerda siempre que esta información debe ser verificada por un profesional"""

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"""CONTEXTO CLÍNICO:

{context}

PREGUNTA DEL PROFESIONAL DE SALUD:
{question}

Analiza detalladamente el contexto clínico proporcionado y responde de manera profesional."""}
                ],
                temperature=0.2,
                max_tokens=2000,
                top_p=0.9
            )
            
            return {
                "response": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "model": model,
                "provider": "Groq (Gratuito)"
            }
            
        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower():
                return {"error": "⏳ Límite de velocidad alcanzado. Espera unos segundos e intenta de nuevo.", "response": None}
            elif "401" in error_msg or "403" in error_msg:
                return {"error": "🔑 API Key inválida. Verifica tu clave en https://console.groq.com", "response": None}
            else:
                return {"error": f"Error al consultar Groq: {error_msg}", "response": None}
    
    def summarize_clinical_record(self, context: str) -> Dict[str, Any]:
        """
        Genera un resumen clínico estructurado automáticamente
        """
        if not self.client:
            return {"error": "Cliente no inicializado", "response": None}
        
        system_prompt = """Eres un asistente médico que genera resúmenes clínicos profesionales en español.
Genera un resumen ESTRUCTURADO con las siguientes secciones:

📋 1. DATOS DEL PACIENTE
   - Información demográfica relevante

🔪 2. PROCEDIMIENTOS QUIRÚRGICOS
   - Lista de cirugías con fechas y estado

⚠️ 3. ALERTAS IMPORTANTES
   - Alergias detectadas
   - Consentimientos faltantes
   - Incidentes reportados
   - Checklists incompletos
   - Equipos vencidos o por vencer

📊 4. ESTADO DE CHECKLISTS
   - Preoperatorios completados/pendientes
   - Intraoperatorios con/sin incidencias
   - Postoperatorios con seguimiento

📈 5. EVOLUCIÓN CLÍNICA
   - Últimos registros relevantes
   - Diagnósticos principales

🔍 6. PENDIENTES Y RECOMENDACIONES
   - Documentación faltante
   - Seguimientos necesarios
   - Próximos pasos sugeridos"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Genera un resumen clínico profesional del siguiente contexto:\n\n{context}"}
                ],
                temperature=0.3,
                max_tokens=2500
            )
            
            return {
                "response": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "provider": "Groq (Gratuito)"
            }
            
        except Exception as e:
            return {"error": f"Error al generar resumen: {str(e)}", "response": None}
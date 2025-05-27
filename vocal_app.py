import streamlit as st
import sys
from io import StringIO
import os

port = int(os.environ.get("PORT", 8501))


# Importar a classe VocalRangeCalculator
class VocalRangeCalculator:
    """Classe para calcular extensão vocal e transposição de tonalidades."""

    def __init__(self):
        # Mapeamento das notas para números (facilita cálculos)
        self.notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.note_names_pt = ['Dó', 'Dó#', 'Ré', 'Ré#', 'Mi', 'Fá', 'Fá#', 'Sol', 'Sol#', 'Lá', 'Lá#', 'Si']
        
        # Círculo das quintas para tonalidades maiores e menores
        self.major_keys = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']
        self.minor_keys = ['Am', 'Em', 'Bm', 'F#m', 'C#m', 'G#m', 'D#m', 'A#m', 'Dm', 'Gm', 'Cm', 'Fm', 'Bbm', 'Ebm', 'Abm']
        
        # Mapeamento de tonalidades para português
        self.keys_pt = {
            'C': 'Dó Maior', 'G': 'Sol Maior', 'D': 'Ré Maior', 'A': 'Lá Maior', 
            'E': 'Mi Maior', 'B': 'Si Maior', 'F#': 'Fá# Maior', 'C#': 'Dó# Maior',
            'F': 'Fá Maior', 'Bb': 'Sib Maior', 'Eb': 'Mib Maior', 'Ab': 'Láb Maior', 
            'Db': 'Réb Maior', 'Gb': 'Solb Maior', 'Cb': 'Dób Maior',
            'Am': 'Lá menor', 'Em': 'Mi menor', 'Bm': 'Si menor', 'F#m': 'Fá# menor',
            'C#m': 'Dó# menor', 'G#m': 'Sol# menor', 'D#m': 'Ré# menor', 'A#m': 'Lá# menor',
            'Dm': 'Ré menor', 'Gm': 'Sol menor', 'Cm': 'Dó menor', 'Fm': 'Fá menor',
            'Bbm': 'Sib menor', 'Ebm': 'Mib menor', 'Abm': 'Láb menor'
        }

    def note_to_number(self, note, octave):
        """Converte nota e oitava para número absoluto (Dó0 = 0)"""
        note_upper = note.upper().replace('Ó', 'O')  # Converte Dó para DO
        
        # Mapeamento de notas em português para inglês
        pt_to_en = {
            'DO': 'C', 'DÓ': 'C', 'C': 'C',
            'DO#': 'C#', 'DÓ#': 'C#', 'C#': 'C#',
            'RE': 'D', 'RÉ': 'D', 'D': 'D',
            'RE#': 'D#', 'RÉ#': 'D#', 'D#': 'D#',
            'MI': 'E', 'E': 'E',
            'FA': 'F', 'FÁ': 'F', 'F': 'F',
            'FA#': 'F#', 'FÁ#': 'F#', 'F#': 'F#',
            'SOL': 'G', 'G': 'G',
            'SOL#': 'G#', 'G#': 'G#',
            'LA': 'A', 'LÁ': 'A', 'A': 'A',
            'LA#': 'A#', 'LÁ#': 'A#', 'A#': 'A#',
            'SI': 'B', 'B': 'B'
        }
        
        note_en = pt_to_en.get(note_upper, note_upper)
        
        if note_en not in self.notes:
            raise ValueError(f"Nota inválida: {note}")
        
        note_index = self.notes.index(note_en)
        return octave * 12 + note_index

    def number_to_note(self, number):
        """Converte número absoluto para nota e oitava"""
        octave = number // 12
        note_index = number % 12
        note = self.note_names_pt[note_index]
        return note, octave

    def transpose_key(self, original_key, semitones):
        """Transpõe uma tonalidade por um número de semitons"""
        # Remove 'm' se for menor
        is_minor = original_key.endswith('m')
        base_key = original_key.replace('m', '') if is_minor else original_key
        
        # Converte a tonalidade base para número
        if base_key not in self.notes:
            # Tenta converter notações como Bb, Ab, etc.
            key_mapping = {'Bb': 'A#', 'Eb': 'D#', 'Ab': 'G#', 'Db': 'C#', 'Gb': 'F#'}
            base_key = key_mapping.get(base_key, base_key)
        
        if base_key in self.notes:
            key_index = self.notes.index(base_key)
            new_index = (key_index + semitones) % 12
            new_key = self.notes[new_index]
            
            # Escolhe a notação mais comum (bemóis vs sustenidos)
            common_keys = {
                'A#': 'Bb', 'C#': 'Db', 'D#': 'Eb', 'F#': 'Gb', 'G#': 'Ab'
            }
            
            # Para tonalidades menores, mantém sustenidos mais comumente
            if not is_minor and new_key in common_keys:
                new_key = common_keys[new_key]
            
            return new_key + ('m' if is_minor else '')
        
        return original_key  # Retorna original se não conseguir processar

    def define_vocal_range(self, lowest_note, lowest_octave, highest_note, highest_octave):
        """Define a extensão vocal do cantor"""
        lowest_num = self.note_to_number(lowest_note, lowest_octave)
        highest_num = self.note_to_number(highest_note, highest_octave)
        
        return {
            'lowest': lowest_num,
            'highest': highest_num,
            'range': highest_num - lowest_num,
            'lowest_note': f"{lowest_note}{lowest_octave}",
            'highest_note': f"{highest_note}{highest_octave}"
        }
    
    def define_song_range(self, lowest_note, lowest_octave, highest_note, highest_octave, original_key=None):
        """Define a extensão da música com tonalidade opcional"""
        lowest_num = self.note_to_number(lowest_note, lowest_octave)
        highest_num = self.note_to_number(highest_note, highest_octave)
        
        return {
            'lowest': lowest_num,
            'highest': highest_num,
            'range': highest_num - lowest_num,
            'lowest_note': f"{lowest_note}{lowest_octave}",
            'highest_note': f"{highest_note}{highest_octave}",
            'original_key': original_key
        }
    
    def check_compatibility(self, vocal_range, song_range):
        """Verifica se a música cabe na extensão vocal"""
        return song_range['range'] <= vocal_range['range']
    
    def calculate_transposition(self, vocal_range, song_range, comfort_margin=0):
        """Calcula a transposição ideal"""
        if not self.check_compatibility(vocal_range, song_range):
            return None, "A extensão da música é maior que a extensão vocal do cantor", None
        
        # Calcular possíveis transposições
        vocal_center = (vocal_range['lowest'] + vocal_range['highest']) / 2
        song_center = (song_range['lowest'] + song_range['highest']) / 2
        
        # Transposição baseada no centro das extensões
        center_transpose = round(vocal_center - song_center)
        
        # Verificar se a transposição cabe com margem de segurança
        transposed_lowest = song_range['lowest'] + center_transpose
        transposed_highest = song_range['highest'] + center_transpose
        
        # Ajustar se necessário para ficar dentro da extensão vocal
        if transposed_lowest < vocal_range['lowest'] + comfort_margin:
            adjustment = vocal_range['lowest'] + comfort_margin - transposed_lowest
            center_transpose += adjustment
        
        if transposed_highest > vocal_range['highest'] - comfort_margin:
            adjustment = transposed_highest - (vocal_range['highest'] - comfort_margin)
            center_transpose -= adjustment
        
        # Calcular nova tonalidade se fornecida
        new_key = None
        if song_range.get('original_key'):
            new_key = self.transpose_key(song_range['original_key'], center_transpose)
        
        return center_transpose, "Transposição calculada com sucesso", new_key

    def semitones_to_key(self, semitones):
        """Converte semitons de transposição para nome da tonalidade"""
        if semitones > 0:
            return f"+{semitones} semitons (mais agudo)"
        elif semitones < 0:
            return f"{semitones} semitons (mais grave)"
        else:
            return "Tom original (sem transposição)"

    def get_key_name_pt(self, key):
        """Retorna o nome da tonalidade em português"""
        return self.keys_pt.get(key, key)

    def calculate_transpositions(self, original_key, vocal_range, song_range, comfort_margin=0):
        """Calcula todas as possíveis transposições para uma música"""
        if not self.check_compatibility(vocal_range, song_range):
            return []
        
        # Calcular possíveis transposições
        vocal_center = (vocal_range['lowest'] + vocal_range['highest']) / 2
        song_center = (song_range['lowest'] + song_range['highest']) / 2
        
        # Transposição baseada no centro das extensões
        center_transpose = round(vocal_center - song_center)
        
        # Lista para armazenar todas as transposições válidas
        valid_transpositions = []
        
        # Tentar transposições próximas ao centro
        for offset in range(-6, 7):  # -6 a +6 semitons
            transpose = center_transpose + offset
            
            # Verificar se a transposição cabe com margem de segurança
            transposed_lowest = song_range['lowest'] + transpose
            transposed_highest = song_range['highest'] + transpose
            
            # Verificar se está dentro da extensão vocal com margem
            if (transposed_lowest >= vocal_range['lowest'] + comfort_margin and 
                transposed_highest <= vocal_range['highest'] - comfort_margin):
                
                # Calcular nova tonalidade
                new_key = self.transpose_key(original_key, transpose)
                
                # Adicionar à lista de transposições válidas
                valid_transpositions.append({
                    'transposition': transpose,
                    'new_key': new_key,
                    'margin_low': transposed_lowest - vocal_range['lowest'],
                    'margin_high': vocal_range['highest'] - transposed_highest
                })
        
        # Ordenar por margem total (soma das margens grave e aguda)
        valid_transpositions.sort(key=lambda x: x['margin_low'] + x['margin_high'], reverse=True)
        
        # Retornar as 3 melhores transposições
        return valid_transpositions[:3]


def main():
    # Configuração da página
    st.set_page_config(
        page_title="Calculadora de Extensão Vocal",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS personalizado
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
        color: #333333;
    }
    .success-card {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #155724;
    }
    .warning-card {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #856404;
    }
    .error-card {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #721c24;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🎵 Calculadora de Extensão Vocal</h1>
        <p>Analise sua extensão vocal e encontre a tonalidade ideal para suas músicas</p>
    </div>
    """, unsafe_allow_html=True)

    # Variáveis para exibir o card de tonalidade sugerida após o header
    suggested_key_card = None
    suggested_key_data = None

    # Criar instância da calculadora
    calc = VocalRangeCalculator()
    
    # Sidebar para entrada de dados
    st.sidebar.header("📊 Configurações")
    
    # Seção: Extensão Vocal do Cantor
    st.sidebar.subheader("🎤 Extensão Vocal do Cantor")
    
    # Notas disponíveis
    notes = ["Dó", "Dó#", "Ré", "Ré#", "Mi", "Fá", "Fá#", "Sol", "Sol#", "Lá", "Lá#", "Si"]
    octaves = list(range(0, 8))
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        singer_low_note = st.selectbox("Nota mais grave", notes, index=0, key="singer_low")
        singer_low_octave = st.selectbox("Oitava", octaves, index=2, key="singer_low_oct")
    
    with col2:
        singer_high_note = st.selectbox("Nota mais aguda", notes, index=7, key="singer_high")
        singer_high_octave = st.selectbox("Oitava ", octaves, index=4, key="singer_high_oct")
    
    # Seção: Extensão da Música
    st.sidebar.subheader("🎵 Extensão da Música")
    
    col3, col4 = st.sidebar.columns(2)
    with col3:
        song_low_note = st.selectbox("Nota mais grave", notes, index=5, key="song_low")
        song_low_octave = st.selectbox("Oitava", octaves, index=3, key="song_low_oct")
    
    with col4:
        song_high_note = st.selectbox("Nota mais aguda", notes, index=2, key="song_high")
        song_high_octave = st.selectbox("Oitava  ", octaves, index=5, key="song_high_oct")
    
    # Tonalidade da música (obrigatória)
    st.sidebar.subheader("🎼 Tonalidade da Música")
    
    all_keys = calc.major_keys + calc.minor_keys
    key_labels = [f"{key} ({calc.get_key_name_pt(key)})" for key in all_keys]
    
    selected_key_index = st.sidebar.selectbox("Tonalidade Original", range(len(key_labels)), 
                                             format_func=lambda x: key_labels[x])
    
    original_key = all_keys[selected_key_index]
    
    # Margem de conforto
    comfort_margin = st.sidebar.slider("Margem de Conforto (semitons)", 0, 5, 5)
    
    # Botão para calcular
    calculate_button = st.sidebar.button("🔍 Analisar", type="primary", use_container_width=True)
    
    # Área principal - Resultados
    if calculate_button:
        try:
            # Definir extensões
            vocal_range = calc.define_vocal_range(
                singer_low_note, singer_low_octave, 
                singer_high_note, singer_high_octave
            )
            
            song_range = calc.define_song_range(
                song_low_note, song_low_octave,
                song_high_note, song_high_octave,
                original_key
            )
            
            # Calcular transposição
            transpose, message, new_key = calc.calculate_transposition(
                vocal_range, song_range, comfort_margin
            )
            
            if transpose is not None:
                # Calcular música transposta e margens
                new_lowest = song_range["lowest"] + transpose
                new_highest = song_range["highest"] + transpose
                new_lowest_note, new_lowest_octave = calc.number_to_note(new_lowest)
                new_highest_note, new_highest_octave = calc.number_to_note(new_highest)
                margin_low = new_lowest - vocal_range["lowest"]
                margin_high = vocal_range["highest"] - new_highest

                # Card de tonalidade sugerida (logo após o header)
                suggested_key_card = f"""
                <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; padding: 2rem; margin-bottom: 2rem; text-align: center; width: 100%;'>
                    <h2 style='margin-bottom: 0.5rem;'>🎯 Tonalidade Sugerida</h2>
                    <div style='font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;'>{new_key} <span style='font-size:1.2rem;'>({calc.get_key_name_pt(new_key)})</span></div>
                    <div style='font-size: 1.2rem;'>Transposição: <b>{calc.semitones_to_key(transpose)}</b></div>
                    <div style='font-size: 1rem; margin-top: 0.5rem;'>Tonalidade original: <b>{original_key} ({calc.get_key_name_pt(original_key)})</b></div>
                </div>
                """
                suggested_key_data = {
                    "new_lowest_note": new_lowest_note,
                    "new_lowest_octave": new_lowest_octave,
                    "new_highest_note": new_highest_note,
                    "new_highest_octave": new_highest_octave,
                    "margin_low": margin_low,
                    "margin_high": margin_high
                }

            # Exibir o card de tonalidade sugerida logo após o header
            if suggested_key_card:
                st.markdown(suggested_key_card, unsafe_allow_html=True)

            # Agora exibir os demais resultados em cards menores
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 Extensão Vocal do Cantor")
                st.markdown(f"""
                <div class="metric-card">
                    <strong>Nota mais grave:</strong> {vocal_range['lowest_note']}<br>
                    <strong>Nota mais aguda:</strong> {vocal_range['highest_note']}<br>
                    <strong>Extensão total:</strong> {vocal_range['range']} semitons
                </div>
                """, unsafe_allow_html=True)
                st.subheader("🎵 Extensão da Música")
                st.markdown(f"""
                <div class="metric-card">
                    <strong>Nota mais grave:</strong> {song_range['lowest_note']}<br>
                    <strong>Nota mais aguda:</strong> {song_range['highest_note']}<br>
                    <strong>Extensão total:</strong> {song_range['range']} semitons
                    {f'<br><strong>Tonalidade original:</strong> {original_key} ({calc.get_key_name_pt(original_key)})' if original_key else ''}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.subheader("🔍 Análise de Compatibilidade")
                compatible = calc.check_compatibility(vocal_range, song_range)
                if compatible:
                    st.markdown("""
                    <div class="success-card">
                        <h4>✅ Música Compatível</h4>
                        <p>A música cabe na extensão vocal do cantor!</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="error-card">
                        <h4>❌ Música Incompatível</h4>
                        <p>A extensão da música é maior que a extensão vocal do cantor.</p>
                        <p><strong>Sugestão:</strong> Escolha uma música com extensão menor ou considere trabalhar para ampliar sua extensão vocal.</p>
                    </div>
                    """, unsafe_allow_html=True)

            # Segunda linha: Música transposta e margens
            colA, colB = st.columns(2)
            with colA:
                st.subheader("🎼 Música Transposta")
                if suggested_key_data:
                    st.markdown(f"""
                    <div class="metric-card">
                        <strong>Nova nota mais grave:</strong> {suggested_key_data['new_lowest_note']}{suggested_key_data['new_lowest_octave']}<br>
                        <strong>Nova nota mais aguda:</strong> {suggested_key_data['new_highest_note']}{suggested_key_data['new_highest_octave']}
                    </div>
                    """, unsafe_allow_html=True)
            with colB:
                st.subheader("📋 Análise das Margens")
                if suggested_key_data:
                    margin_low = suggested_key_data['margin_low']
                    margin_high = suggested_key_data['margin_high']
                    if margin_low >= 2 and margin_high >= 2:
                        st.markdown(f"""
                        <div class="success-card">
                            <h4>✅ Margens Adequadas</h4>
                            <p><strong>Margem grave:</strong> {margin_low} semitons<br>
                            <strong>Margem aguda:</strong> {margin_high} semitons<br>
                            <em>Execução confortável recomendada!</em></p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif margin_low >= 1 and margin_high >= 1:
                        st.markdown(f"""
                        <div class="warning-card">
                            <h4>⚠️ Margens Justas</h4>
                            <p><strong>Margem grave:</strong> {margin_low} semitons<br>
                            <strong>Margem aguda:</strong> {margin_high} semitons<br>
                            <em>Cantar com cuidado - margens limitadas</em></p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="error-card">
                            <h4>❌ Margens Insuficientes</h4>
                            <p><strong>Margem grave:</strong> {margin_low} semitons<br>
                            <strong>Margem aguda:</strong> {margin_high} semitons<br>
                            <em>Pode ser desconfortável - considere ajustar</em></p>
                        </div>
                        """, unsafe_allow_html=True)

            # Seção adicional: Debug e Teste
            if st.sidebar.button("🧪 Testar com valores do script"):
                # Valores exatos do script original
                test_vocal_range = calc.define_vocal_range("Dó", 2, "Sol", 4)
                test_song_range = calc.define_song_range("Fá", 3, "Ré", 5, "C")
                
                st.subheader("🧪 Teste de Comparação com Script Original")
                
                # Debug info
                st.write("**Extensão Vocal:**", test_vocal_range)
                st.write("**Extensão Música:**", test_song_range)
                
                # Teste de compatibilidade
                test_compatible = calc.check_compatibility(test_vocal_range, test_song_range)
                st.write("**Compatível:**", test_compatible)
                
                # Teste de transposição
                test_transpose, test_message, test_new_key = calc.calculate_transposition(test_vocal_range, test_song_range, 2)
                st.write("**Transposição:**", test_transpose)
                st.write("**Nova tonalidade:**", test_new_key)
                st.write("**Mensagem:**", test_message)
                
                # Teste individual da função transpose_key
                if test_transpose is not None:
                    manual_transpose = calc.transpose_key("C", test_transpose)
                    st.write("**Transposição manual de C com", test_transpose, "semitons:**", manual_transpose)
            
            # Seção adicional: Transposição de Tonalidades
            if original_key:
                st.markdown("---")
                st.subheader("🔄 Exemplos de Transposição")
                
                # Exemplos de transposição para tonalidades maiores e menores
                major_examples = ['C', 'G']
                minor_examples = ['Am']
                transpose_values = [2, -3]
                
                # Tonalidades maiores
                st.markdown("#### Tonalidades Maiores")
                col1, col2 = st.columns(2)
                for i, (col, key) in enumerate(zip([col1, col2], major_examples)):
                    with col:
                        for shift in transpose_values:
                            transposed = calc.transpose_key(key, shift)
                            direction = "mais agudo" if shift > 0 else "mais grave"
                            st.markdown(f"""
                            <div class="metric-card" style="text-align: center;">
                                <strong>{shift:+d} semitons ({direction})</strong><br>
                                <small>{calc.get_key_name_pt(key)}</small><br>
                                <strong>para</strong><br>
                                <strong>{transposed}</strong><br>
                                <small>{calc.get_key_name_pt(transposed)}</small>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Tonalidades menores
                st.markdown("#### Tonalidades Menores")
                col3, col4 = st.columns(2)
                for i, (col, key) in enumerate(zip([col3, col4], minor_examples)):
                    with col:
                        for shift in transpose_values:
                            transposed = calc.transpose_key(key, shift)
                            direction = "mais agudo" if shift > 0 else "mais grave"
                            st.markdown(f"""
                            <div class="metric-card" style="text-align: center;">
                                <strong>{shift:+d} semitons ({direction})</strong><br>
                                <small>{calc.get_key_name_pt(key)}</small><br>
                                <strong>para</strong><br>
                                <strong>{transposed}</strong><br>
                                <small>{calc.get_key_name_pt(transposed)}</small>
                            </div>
                            """, unsafe_allow_html=True)
            
            # Seção de transposição
            st.subheader("🎹 Transposição")
            
            # Mostrar a tonalidade original
            st.write(f"**Tonalidade Original:** {original_key} ({calc.get_key_name_pt(original_key)})")
            
            # Calcular e mostrar as transposições
            transpositions = calc.calculate_transpositions(original_key, vocal_range, song_range, comfort_margin)
            
            if transpositions:
                st.success("✅ Transposições encontradas!")
                
                # Criar colunas para as transposições
                cols = st.columns(3)
                
                for i, trans in enumerate(transpositions):
                    with cols[i % 3]:
                        st.metric(
                            label=f"Transposição {i+1}",
                            value=f"{trans['transposition']:+d} semitons",
                            delta=f"→ {trans['new_key']} ({calc.get_key_name_pt(trans['new_key'])})"
                        )
            else:
                st.error("❌ Não foi possível encontrar transposições adequadas para este intervalo.")
        except Exception as e:
            st.error(f"Erro ao calcular: {str(e)}")
    else:
        # Tela inicial com instruções
        st.markdown("""
        ## Como usar esta calculadora:
        
        ### 1. 📊 **Defina sua Extensão Vocal**
        - Selecione a nota mais grave que você consegue cantar confortavelmente
        - Selecione a nota mais aguda que você consegue cantar confortavelmente
        
        ### 2. 🎵 **Configure a Música**
        - Selecione a nota mais grave da música
        - Selecione a nota mais aguda da música
        - Escolha a tonalidade original da música
        
        ### 3. ⚙️ **Ajuste a Margem de Conforto**
        - Defina quantos semitons de margem você quer manter nas extremidades
        
        ### 4. 🔍 **Analise os Resultados**
        - Verifique se a música é compatível com sua extensão vocal
        - Veja as sugestões de transposição
        - Analise as margens de conforto
        """)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", "vocal_app.py", "--server.port", str(port), "--server.address", "0.0.0.0"]
        sys.exit(stcli.main())
    else:
        main()
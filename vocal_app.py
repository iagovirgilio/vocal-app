"""Módulo para cálculo de extensão vocal e transposição de tonalidades."""

import os
from typing import Dict, List, Optional, Tuple, Union
import streamlit as st
import numpy as np
from synthesizer import Player, Synthesizer, Waveform
import io
import base64
import wave


# Constantes
DEFAULT_PORT = 8080
NOTES_EN = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTES_PT = ['Dó', 'Dó#', 'Ré', 'Ré#', 'Mi', 'Fá', 'Fá#', 'Sol', 'Sol#', 'Lá', 'Lá#', 'Si']
MAJOR_KEYS = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']
MINOR_KEYS = ['Am', 'Em', 'Bm', 'F#m', 'C#m', 'G#m', 'D#m', 'A#m', 'Dm', 'Gm', 'Cm', 'Fm', 'Bbm', 'Ebm', 'Abm']

# Configuração da porta
port = int(os.environ.get("PORT", DEFAULT_PORT))


# Importar a classe VocalRangeCalculator
class VocalRangeCalculator:
    """Classe para calcular extensão vocal e transposição de tonalidades.
    
    Esta classe fornece métodos para:
    - Converter notas musicais entre diferentes representações
    - Calcular extensões vocais
    - Transpor tonalidades
    - Verificar compatibilidade entre extensões vocais e músicas
    """

    def __init__(self) -> None:
        """Inicializa a calculadora com os mapeamentos necessários."""
        self.notes = NOTES_EN
        self.note_names_pt = NOTES_PT
        self.major_keys = MAJOR_KEYS
        self.minor_keys = MINOR_KEYS

        # Mapeamento de tonalidades para português
        self.keys_pt: Dict[str, str] = {
            'C': 'Dó Maior', 'G': 'Sol Maior', 'D': 'Ré Maior', 'A': 'Lá Maior', 
            'E': 'Mi Maior', 'B': 'Si Maior', 'F#': 'Fá# Maior', 'C#': 'Dó# Maior',
            'F': 'Fá Maior', 'Bb': 'Sib Maior', 'Eb': 'Mib Maior', 'Ab': 'Láb Maior', 
            'Db': 'Réb Maior', 'Gb': 'Solb Maior', 'Cb': 'Dób Maior',
            'Am': 'Lá menor', 'Em': 'Mi menor', 'Bm': 'Si menor', 'F#m': 'Fá# menor',
            'C#m': 'Dó# menor', 'G#m': 'Sol# menor', 'D#m': 'Ré# menor', 'A#m': 'Lá# menor',
            'Dm': 'Ré menor', 'Gm': 'Sol menor', 'Cm': 'Dó menor', 'Fm': 'Fá menor',
            'Bbm': 'Sib menor', 'Ebm': 'Mib menor', 'Abm': 'Láb menor'
        }

    def note_to_number(self, note: str, octave: int) -> int:
        """Converte nota e oitava para número absoluto (Dó0 = 0).
        
        Args:
            note: Nota musical em português ou inglês
            octave: Número da oitava (0-7)

        Returns:
            Número absoluto da nota (Dó0 = 0)

        Raises:
            ValueError: Se a nota for inválida
        """
        note_upper = note.upper().replace('Ó', 'O')  # Converte Dó para DO

        # Mapeamento de notas em português para inglês
        pt_to_en: Dict[str, str] = {
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

    def number_to_note(self, number: int) -> Tuple[str, int]:
        """Converte número absoluto para nota e oitava.

        Args:
            number: Número absoluto da nota (Dó0 = 0)

        Returns:
            Tupla contendo (nota em português, oitava)
        """
        octave = number // 12
        note_index = number % 12
        note = self.note_names_pt[note_index]
        return note, octave

    def transpose_key(self, original_key: str, semitones: int) -> str:
        """Transpõe uma tonalidade por um número de semitons.

        Args:
            original_key: Tonalidade original (ex: 'C', 'Am')
            semitones: Número de semitons para transpor

        Returns:
            Nova tonalidade transposta
        """
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

    def define_vocal_range(self, lowest_note: str, lowest_octave: int,
                          highest_note: str, highest_octave: int) -> Dict[str, Union[int, str]]:
        """Define a extensão vocal do cantor.
        
        Args:
            lowest_note: Nota mais grave que o cantor consegue cantar
            lowest_octave: Oitava da nota mais grave
            highest_note: Nota mais aguda que o cantor consegue cantar
            highest_octave: Oitava da nota mais aguda

        Returns:
            Dicionário com informações da extensão vocal
        """
        lowest_num = self.note_to_number(lowest_note, lowest_octave)
        highest_num = self.note_to_number(highest_note, highest_octave)

        return {
            'lowest': lowest_num,
            'highest': highest_num,
            'range': highest_num - lowest_num,
            'lowest_note': f"{lowest_note}{lowest_octave}",
            'highest_note': f"{highest_note}{highest_octave}"
        }

    def define_song_range(self, lowest_note: str, lowest_octave: int,
                         highest_note: str, highest_octave: int,
                         original_key: Optional[str] = None) -> Dict[str, Union[int, str, None]]:
        """Define a extensão da música com tonalidade opcional.

        Args:
            lowest_note: Nota mais grave da música
            lowest_octave: Oitava da nota mais grave
            highest_note: Nota mais aguda da música
            highest_octave: Oitava da nota mais aguda
            original_key: Tonalidade original da música (opcional)

        Returns:
            Dicionário com informações da extensão da música
        """
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

    def check_compatibility(self, vocal_range: Dict[str, Union[int, str]],
                          song_range: Dict[str, Union[int, str]]) -> bool:
        """Verifica se a música cabe na extensão vocal.

        Args:
            vocal_range: Extensão vocal do cantor
            song_range: Extensão da música

        Returns:
            True se a música cabe na extensão vocal, False caso contrário
        """
        return song_range['range'] <= vocal_range['range']

    def calculate_transposition(self, vocal_range: Dict[str, Union[int, str]],
                              song_range: Dict[str, Union[int, str]],
                              comfort_margin: int = 0) -> Tuple[Optional[int], str, Optional[str]]:
        """Calcula a transposição ideal para uma música.

        Args:
            vocal_range: Extensão vocal do cantor
            song_range: Extensão da música
            comfort_margin: Margem de conforto em semitons
            
        Returns:
            Tupla contendo (transposição, mensagem, nova tonalidade)
        """
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

    def semitones_to_key(self, semitones: int) -> str:
        """Converte semitons de transposição para nome da tonalidade.

        Args:
            semitones: Número de semitons de transposição

        Returns:
            Descrição da transposição em português
        """
        if semitones > 0:
            return f"+{semitones} semitons (mais agudo)"
        elif semitones < 0:
            return f"{semitones} semitons (mais grave)"
        else:
            return "Tom original (sem transposição)"

    def get_key_name_pt(self, key: str) -> str:
        """Retorna o nome da tonalidade em português.

        Args:
            key: Tonalidade em inglês

        Returns:
            Nome da tonalidade em português
        """
        return self.keys_pt.get(key, key)

    def calculate_transpositions(self, original_key: str,
                               vocal_range: Dict[str, Union[int, str]],
                               song_range: Dict[str, Union[int, str]],
                               comfort_margin: int = 0) -> List[Dict[str, Union[int, str]]]:
        """Calcula todas as possíveis transposições para uma música.

        Args:
            original_key: Tonalidade original da música
            vocal_range: Extensão vocal do cantor
            song_range: Extensão da música
            comfort_margin: Margem de conforto em semitons

        Returns:
            Lista de dicionários com as melhores transposições encontradas
        """
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


def setup_page() -> None:
    """Configura a página do Streamlit com estilo e layout."""
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

def get_singer_inputs(default_low_note=None, default_low_octave=None, default_high_note=None, default_high_octave=None) -> Tuple[str, int, str, int]:
    """Obtém as entradas do usuário para a extensão vocal, com valores padrão opcionais."""
    st.sidebar.subheader("🎤 Extensão Vocal do Cantor")

    notes = NOTES_PT
    octaves = list(range(1, 9))  # Apenas da oitava 1 até a 8

    # Determinar índices padrão
    low_note_index = notes.index(default_low_note) if default_low_note in notes else 0
    low_octave_index = octaves.index(default_low_octave) if default_low_octave in octaves else 0
    high_note_index = notes.index(default_high_note) if default_high_note in notes else 7
    high_octave_index = octaves.index(default_high_octave) if default_high_octave in octaves else 3

    col1, col2 = st.sidebar.columns(2)
    with col1:
        singer_low_note = st.selectbox("Nota mais grave", notes, index=low_note_index, key="singer_low")
        singer_low_octave = st.selectbox("Oitava", octaves, index=low_octave_index, key="singer_low_oct")

    with col2:
        singer_high_note = st.selectbox("Nota mais aguda", notes, index=high_note_index, key="singer_high")
        singer_high_octave = st.selectbox("Oitava ", octaves, index=high_octave_index, key="singer_high_oct")

    return singer_low_note, singer_low_octave, singer_high_note, singer_high_octave

def get_song_inputs(calc: VocalRangeCalculator) -> Tuple[str, int, str, int, str]:
    """Obtém as entradas do usuário para a música.

    Args:
        calc: Instância da calculadora de extensão vocal

    Returns:
        Tupla contendo (nota mais grave, oitava mais grave, nota mais aguda, oitava mais aguda, tonalidade)
    """
    st.sidebar.subheader("🎵 Extensão da Música")

    notes = NOTES_PT
    octaves = list(range(1, 9))  # Apenas da oitava 1 até a 8

    col3, col4 = st.sidebar.columns(2)
    with col3:
        song_low_note = st.selectbox("Nota mais grave", notes, index=2, key="song_low")
        song_low_octave = st.selectbox("Oitava", octaves, index=2, key="song_low_oct")

    with col4:
        song_high_note = st.selectbox("Nota mais aguda", notes, index=7, key="song_high")
        song_high_octave = st.selectbox("Oitava  ", octaves, index=3, key="song_high_oct")

    # Tonalidade da música (obrigatória)
    st.sidebar.subheader("🎼 Tonalidade da Música")

    all_keys = calc.major_keys + calc.minor_keys
    key_labels = [f"{key} ({calc.get_key_name_pt(key)})" for key in all_keys]

    selected_key_index = st.sidebar.selectbox("Tonalidade Original", range(len(key_labels)), 
                                             format_func=lambda x: key_labels[x])

    original_key = all_keys[selected_key_index]

    return song_low_note, song_low_octave, song_high_note, song_high_octave, original_key

def display_results(calc: VocalRangeCalculator, vocal_range: Dict[str, Union[int, str]],
                   song_range: Dict[str, Union[int, str]], original_key: str,
                   transpose: Optional[int], new_key: Optional[str],
                   suggested_key_data: Optional[Dict[str, Union[str, int]]]) -> None:
    """Exibe os resultados da análise.

    Args:
        calc: Instância da calculadora de extensão vocal
        vocal_range: Extensão vocal do cantor
        song_range: Extensão da música
        original_key: Tonalidade original
        transpose: Transposição calculada
        new_key: Nova tonalidade
        suggested_key_data: Dados da tonalidade sugerida
    """
    # Exibir o card de tonalidade sugerida logo após o header
    if transpose is not None and new_key is not None:
        suggested_key_card = f"""
        <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; padding: 2rem; margin-bottom: 2rem; text-align: center; width: 100%;'>
            <h2 style='margin-bottom: 0.5rem;'>🎯 Tonalidade Sugerida</h2>
            <div style='font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;'>{new_key} <span style='font-size:1.2rem;'>({calc.get_key_name_pt(new_key)})</span></div>
            <div style='font-size: 1.2rem;'>Transposição: <b>{calc.semitones_to_key(transpose)}</b></div>
            <div style='font-size: 1rem; margin-top: 0.5rem;'>Tonalidade original: <b>{original_key} ({calc.get_key_name_pt(original_key)})</b></div>
        </div>
        """
        st.markdown(suggested_key_card, unsafe_allow_html=True)

    # Exibir os demais resultados em cards menores
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
    if suggested_key_data:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("🎼 Música Transposta")
            st.markdown(f"""
            <div class="metric-card">
                <strong>Nova nota mais grave:</strong> {suggested_key_data['new_lowest_note']}{suggested_key_data['new_lowest_octave']}<br>
                <strong>Nova nota mais aguda:</strong> {suggested_key_data['new_highest_note']}{suggested_key_data['new_highest_octave']}
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            st.subheader("📋 Análise das Margens")
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

def display_instructions() -> None:
    """Exibe as instruções de uso da calculadora."""
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

def get_voice_type(total_range: int, lowest_note: str, lowest_octave: int) -> str:
    """Determina o tipo de voz baseado na extensão e notas.
    
    Args:
        total_range: Extensão total em semitons
        lowest_note: Nota mais grave
        lowest_octave: Oitava da nota mais grave
        
    Returns:
        String com o tipo de voz
    """
    # Mapeamento de tipos de voz
    voice_types = {
        'Soprano': {'range': (12, 20), 'lowest': ('Dó', 4)},
        'Mezzo-soprano': {'range': (12, 18), 'lowest': ('Lá', 3)},
        'Contralto': {'range': (12, 16), 'lowest': ('Fá', 3)},
        'Tenor': {'range': (12, 18), 'lowest': ('Dó', 3)},
        'Barítono': {'range': (12, 16), 'lowest': ('Sol', 2)},
        'Baixo': {'range': (12, 16), 'lowest': ('Mi', 2)}
    }
    
    # Converter nota mais grave para número
    lowest_num = 0
    closest_type = 'Soprano'  # Valor padrão
    
    for voice_type, specs in voice_types.items():
        ref_lowest = specs['lowest']
        ref_lowest_num = ref_lowest[1] * 12 + NOTES_PT.index(ref_lowest[0])
        if lowest_num <= ref_lowest_num:
            lowest_num = ref_lowest_num
            closest_type = voice_type
    
    return closest_type

def get_voice_gender(voice_type: str) -> str:
    """Retorna se a voz é masculina ou feminina de acordo com o tipo de voz."""
    femininas = ['Soprano', 'Mezzo-soprano', 'Contralto']
    masculinas = ['Tenor', 'Barítono', 'Baixo']
    if voice_type in femininas:
        return 'Feminina'
    if voice_type in masculinas:
        return 'Masculina'
    return 'Indefinida'

def generate_note_audio(note: str, octave: int) -> str:
    """Gera um arquivo de áudio WAV válido para uma nota específica e retorna em base64."""
    pt_to_en = {
        'Dó': 'C', 'Dó#': 'C#', 'Ré': 'D', 'Ré#': 'D#', 'Mi': 'E',
        'Fá': 'F', 'Fá#': 'F#', 'Sol': 'G', 'Sol#': 'G#', 'Lá': 'A', 'Lá#': 'A#', 'Si': 'B'
    }
    note_en = pt_to_en.get(note, note)
    # Encontrar o número MIDI correto
    notes_en = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    if note_en == 'C' and octave == 8:
        midi_num = 108  # C8 é a última nota do piano
    else:
        # Para todas as outras notas
        midi_num = notes_en.index(note_en) + 12 * (octave + 1)
    # Calcular frequência
    frequency = 440 * (2 ** ((midi_num - 69) / 12))
    synthesizer = Synthesizer(osc1_waveform=Waveform.sine, osc1_volume=1.0, use_osc2=False)
    audio = synthesizer.generate_constant_wave(frequency, 2.0)
    audio = (audio * 32767).astype(np.int16)
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(audio.tobytes())
    audio_bytes = buffer.getvalue()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    return audio_base64

def get_audio_html(note: str, octave: int) -> str:
    """Gera o HTML para o player de áudio.
    
    Args:
        note: Nota musical
        octave: Número da oitava
        
    Returns:
        String com o HTML do player
    """
    audio_base64 = generate_note_audio(note, octave)
    return f"""
    <audio controls style="width: 100%;">
        <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
        Seu navegador não suporta o elemento de áudio.
    </audio>
    """

def get_all_piano_notes() -> list:
    """Gera uma lista de todas as notas do piano de Dó1 até Dó8 no padrão brasileiro, começando cada oitava em Dó."""
    notes_pt = ['Dó', 'Dó#', 'Ré', 'Ré#', 'Mi', 'Fá', 'Fá#', 'Sol', 'Sol#', 'Lá', 'Lá#', 'Si']
    notes = []
    for octave in range(1, 9):  # Dó1 até Dó8
        for note in notes_pt:
            # Não incluir notas acima de Dó8
            if octave == 8 and note != 'Dó':
                continue
            notes.append((note, octave))
    return notes

def get_voice_ranges_pt() -> list:
    """Retorna as faixas típicas de cada classificação vocal (notas em português, oitava 1-8), conforme padrão do usuário."""
    return [
        {"tipo": "Baixo", "faixa": ("Dó1", "Fá3"), "famosos": "Barry White", "genero": "Masculina"},
        {"tipo": "Barítono", "faixa": ("Sol1", "Lá3"), "famosos": "Anderson Freire", "genero": "Masculina"},
        {"tipo": "Tenor", "faixa": ("Dó2", "Ré4"), "famosos": "Luan Santana", "genero": "Masculina"},
        {"tipo": "Contralto", "faixa": ("Fá2", "Dó4"), "famosos": "Ivete Sangalo", "genero": "Feminina"},
        {"tipo": "Mezzo-soprano", "faixa": ("Lá2", "Dó5"), "famosos": "Christina Aguilera", "genero": "Feminina"},
        {"tipo": "Soprano", "faixa": ("Dó3", "Fá5"), "famosos": "Mariah Carey", "genero": "Feminina"},
    ]

def run_vocal_test(calc: VocalRangeCalculator) -> Tuple[str, int, str, int]:
    """Executa um teste interativo para descobrir a extensão vocal do usuário.
    
    Args:
        calc: Instância da calculadora de extensão vocal
        
    Returns:
        Tupla contendo (nota mais grave, oitava mais grave, nota mais aguda, oitava mais aguda)
    """
    st.markdown("""
    ## 🎤 Teste de Extensão Vocal
    
    Vamos descobrir sua extensão vocal! Siga os passos abaixo:
    
    1. **Preparação**:
       - Encontre um lugar silencioso
       - Aqueça sua voz por alguns minutos
       - Tenha um copo d'água por perto
    
    2. **Como fazer o teste**:
       - Cante cada nota por 2-3 segundos
       - Use a vogal "A" (como em "pai")
       - Pare se sentir desconforto
       - Faça pausas entre as notas
    """)
    
    # Gerar todas as notas do piano
    reference_notes = get_all_piano_notes()
    
    # Estado do teste
    if 'vocal_test_low' not in st.session_state:
        st.session_state['vocal_test_low'] = None
    if 'vocal_test_high' not in st.session_state:
        st.session_state['vocal_test_high'] = None

    # Passo 1: nota mais grave
    if st.session_state['vocal_test_low'] is None:
        st.subheader("🎯 Teste de Notas do Piano (Dó1 até Dó8)")
        st.markdown("Cante cada nota da mais grave para a mais aguda. Pare quando não conseguir mais cantar confortavelmente.")
        cols = st.columns(6)
        for i, (note, octave) in enumerate(reference_notes):
            with cols[i % 6]:
                st.markdown(f"""
                <div style='text-align: center; padding: 0.5rem; border: 1px solid #ddd; border-radius: 8px; margin: 0.2rem 0;'>
                    <h4 style='margin: 0;'>{note}{octave}</h4>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(get_audio_html(note, octave), unsafe_allow_html=True)
                if st.button("Posso cantar", key=f"low_{note}{octave}", use_container_width=True):
                    st.session_state['vocal_test_low'] = (note, octave)
                    st.rerun()
        st.warning("Por favor, tente cantar pelo menos uma nota para continuar.")
        return None, None, None, None

    # Passo 2: nota mais aguda
    lowest_note, lowest_octave = st.session_state['vocal_test_low']
    if st.session_state['vocal_test_high'] is None:
        st.progress(0.5)
        st.markdown("""
        <div style='text-align: center; margin: 1rem 0;'>
            <h3>✅ Nota mais grave encontrada!</h3>
            <p>Agora vamos testar as notas mais agudas.</p>
        </div>
        """, unsafe_allow_html=True)
        st.subheader("🎯 Teste de Notas Agudas (Dó1 até Dó8)")
        st.markdown("Agora vamos testar as notas mais agudas. Comece da nota mais aguda e vá descendo.")
        cols = st.columns(6)
        for i, (note, octave) in enumerate(reversed(reference_notes)):
            if (calc.note_to_number(note, octave) <= calc.note_to_number(lowest_note, lowest_octave)):
                continue
            with cols[i % 6]:
                st.markdown(f"""
                <div style='text-align: center; padding: 0.5rem; border: 1px solid #ddd; border-radius: 8px; margin: 0.2rem 0;'>
                    <h4 style='margin: 0;'>{note}{octave}</h4>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(get_audio_html(note, octave), unsafe_allow_html=True)
                if st.button("Posso cantar", key=f"high_{note}{octave}", use_container_width=True):
                    st.session_state['vocal_test_high'] = (note, octave)
                    st.rerun()
        st.warning("Por favor, tente cantar pelo menos uma nota aguda para continuar.")
        return None, None, None, None

    # Exibir resultado final
    lowest_note, lowest_octave = st.session_state['vocal_test_low']
    highest_note, highest_octave = st.session_state['vocal_test_high']
    total_range = calc.note_to_number(highest_note, highest_octave) - calc.note_to_number(lowest_note, lowest_octave)
    voice_type = get_voice_type(total_range, lowest_note, lowest_octave)
    voice_gender = get_voice_gender(voice_type)
    notas_alcancadas = []
    lowest_num = calc.note_to_number(lowest_note, lowest_octave)
    highest_num = calc.note_to_number(highest_note, highest_octave)
    for n in range(lowest_num, highest_num + 1):
        nota, oitava = calc.number_to_note(n)
        notas_alcancadas.append(f"{nota}{oitava}")

    # Encontrar todas as classificações compatíveis
    faixas_compat = []
    for v in get_voice_ranges_pt():
        faixa_low, faixa_high = v['faixa']
        faixa_low_note, faixa_low_oct = faixa_low[:-1], int(faixa_low[-1])
        faixa_high_note, faixa_high_oct = faixa_high[:-1], int(faixa_high[-1])
        faixa_low_num = calc.note_to_number(faixa_low_note, faixa_low_oct)
        faixa_high_num = calc.note_to_number(faixa_high_note, faixa_high_oct)
        # Se houver interseção entre a extensão do usuário e a faixa da classificação
        if not (highest_num < faixa_low_num or lowest_num > faixa_high_num):
            faixas_compat.append(v['tipo'])

    st.success(f"""
    🎉 Sua extensão vocal foi identificada!
    
    ### 📊 Resultados:
    - **Nota mais grave:** {lowest_note}{lowest_octave}
    - **Nota mais aguda:** {highest_note}{highest_octave}
    - **Extensão total:** {total_range} semitons
    - **Classificações vocais compatíveis:** {', '.join(faixas_compat)}
    """)
    st.markdown(f"Notas alcançadas: <span style='color:#667eea;font-weight:bold'>{' - '.join(notas_alcancadas)}</span>", unsafe_allow_html=True)

    # Tabela visual das classificações
    st.markdown("""
    <h4>Classificações vocais e exemplos:</h4>
    <table style='width:100%; border-collapse:collapse;'>
      <tr style='background:#f8f9fa;'>
        <th style='padding:6px; border:1px solid #ccc;'>Classificação</th>
        <th style='padding:6px; border:1px solid #ccc;'>Faixa típica</th>
        <th style='padding:6px; border:1px solid #ccc;'>Exemplo famoso</th>
      </tr>
    """, unsafe_allow_html=True)
    for v in get_voice_ranges_pt():
        faixa = f"{v['faixa'][0]} até {v['faixa'][1]}"
        destaque = "background:#d4edda;" if v["tipo"] in faixas_compat else ""
        st.markdown(f"""
        <tr style='{destaque}'>
          <td style='padding:6px; border:1px solid #ccc;'><b>{v['tipo']}</b></td>
          <td style='padding:6px; border:1px solid #ccc;'>{faixa}</td>
          <td style='padding:6px; border:1px solid #ccc;'>{v['famosos']}</td>
        </tr>
        """, unsafe_allow_html=True)
    st.markdown("</table>", unsafe_allow_html=True)

    st.markdown("""
    <b>O que é classificação vocal?</b><br>
    Classificar a voz é identificar a faixa de notas que você consegue cantar confortavelmente, considerando também sua tessitura (faixa confortável), timbre e características físicas. No canto erudito e coral, a classificação é fundamental para escolher repertório e posição no grupo. No canto popular, o mais importante é cantar com conforto e adaptar o tom das músicas para sua voz.
    <br><br>
    <b>Dica:</b> Sua classificação vocal é uma referência baseada na extensão, mas o mais importante é cantar onde você se sente confortável! Se sua voz cobre mais de uma faixa, escolha a região onde cantar é mais fácil e natural para você.<br>
    <b>Importante:</b> Para iniciantes e adolescentes, a voz pode mudar com o tempo. Só após a maturação vocal é possível uma classificação definitiva.<br>
    <b>Tessitura</b> é a faixa de notas onde sua voz soa melhor e com menos esforço. Não force para alcançar notas extremas!
    <br><br>
    Para uma avaliação precisa e orientações técnicas, procure um professor de canto.
    """, unsafe_allow_html=True)

    st.info("""
    **Anote suas notas mais grave e aguda!**
    
    Para usar o conversor de tonalidade, mude para o modo "Entrar manualmente" no menu lateral e preencha as notas que você descobriu aqui.
    """)
    if st.button("🔄 Refazer teste de extensão vocal"):
        st.session_state['vocal_test_low'] = None
        st.session_state['vocal_test_high'] = None
        st.rerun()
    return lowest_note, lowest_octave, highest_note, highest_octave

def main() -> None:
    """Função principal da aplicação."""
    # Configuração da página
    setup_page()

    # Criar instância da calculadora
    calc = VocalRangeCalculator()

    # Controle de tela: 'calculadora' ou 'teste'
    if 'tela' not in st.session_state:
        st.session_state['tela'] = 'calculadora'

    if st.session_state['tela'] == 'calculadora':
        st.sidebar.header("📊 Configurações")
        st.sidebar.markdown("---")
        if st.sidebar.button("🎤 Fazer teste de extensão vocal", use_container_width=True):
            st.session_state['tela'] = 'teste'
            st.rerun()
        # Calculadora modo manual
        singer_low_note, singer_low_octave, singer_high_note, singer_high_octave = get_singer_inputs()
        song_low_note, song_low_octave, song_high_note, song_high_octave, original_key = get_song_inputs(calc)
        comfort_margin = st.sidebar.slider("Margem de Conforto (semitons)", 0, 5, 5)
        calculate_button = st.sidebar.button("🔍 Analisar", type="primary", use_container_width=True)
        if calculate_button:
            try:
                vocal_range = calc.define_vocal_range(
                    singer_low_note, singer_low_octave, 
                    singer_high_note, singer_high_octave
                )
                song_range = calc.define_song_range(
                    song_low_note, song_low_octave,
                    song_high_note, song_high_octave,
                    original_key
                )
                transpose, message, new_key = calc.calculate_transposition(
                    vocal_range, song_range, comfort_margin
                )
                suggested_key_data = None
                if transpose is not None:
                    new_lowest = song_range["lowest"] + transpose
                    new_highest = song_range["highest"] + transpose
                    new_lowest_note, new_lowest_octave = calc.number_to_note(new_lowest)
                    new_highest_note, new_highest_octave = calc.number_to_note(new_highest)
                    margin_low = new_lowest - vocal_range["lowest"]
                    margin_high = vocal_range["highest"] - new_highest
                    suggested_key_data = {
                        "new_lowest_note": new_lowest_note,
                        "new_lowest_octave": new_lowest_octave,
                        "new_highest_note": new_highest_note,
                        "new_highest_octave": new_highest_octave,
                        "margin_low": margin_low,
                        "margin_high": margin_high
                    }
                display_results(calc, vocal_range, song_range, original_key, transpose, new_key, suggested_key_data)
            except Exception as e:
                st.error(f"Erro ao calcular: {str(e)}")
        else:
            display_instructions()
    elif st.session_state['tela'] == 'teste':
        st.sidebar.header("🔙 Voltar")
        if st.sidebar.button("⬅️ Voltar para a calculadora", use_container_width=True):
            st.session_state['tela'] = 'calculadora'
            st.rerun()
        run_vocal_test(calc)

if __name__ == "__main__":
    main()

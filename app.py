class VocalRangeCalculator:
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
    
    def analyze_singer_song(self, vocal_range, song_range, comfort_margin=2):
        """Análise completa: cantor + música"""
        print("=" * 60)
        print("ANÁLISE DE EXTENSÃO VOCAL E TRANSPOSIÇÃO")
        print("=" * 60)
        
        print(f"\n📊 EXTENSÃO VOCAL DO CANTOR:")
        print(f"   • Nota mais grave: {vocal_range['lowest_note']}")
        print(f"   • Nota mais aguda: {vocal_range['highest_note']}")
        print(f"   • Extensão: {vocal_range['range']} semitons")
        
        print(f"\n🎵 EXTENSÃO DA MÚSICA:")
        print(f"   • Nota mais grave: {song_range['lowest_note']}")
        print(f"   • Nota mais aguda: {song_range['highest_note']}")
        print(f"   • Extensão: {song_range['range']} semitons")
        
        if song_range.get('original_key'):
            print(f"   • Tonalidade original: {song_range['original_key']} ({self.get_key_name_pt(song_range['original_key'])})")
        
        print(f"\n🔍 COMPATIBILIDADE:")
        compatible = self.check_compatibility(vocal_range, song_range)
        if compatible:
            print("   ✅ A música cabe na extensão vocal do cantor")
        else:
            print("   ❌ A música NÃO cabe na extensão vocal do cantor")
            return
        
        print(f"\n🎯 CÁLCULO DE TRANSPOSIÇÃO:")
        transpose, message, new_key = self.calculate_transposition(vocal_range, song_range, comfort_margin)
        
        if transpose is not None:
            print(f"   • {message}")
            print(f"   • Transposição sugerida: {self.semitones_to_key(transpose)}")
            
            if new_key:
                print(f"   • Nova tonalidade: {new_key} ({self.get_key_name_pt(new_key)})")
            
            # Mostrar como ficará a música transposta
            new_lowest = song_range['lowest'] + transpose
            new_highest = song_range['highest'] + transpose
            new_lowest_note, new_lowest_octave = self.number_to_note(new_lowest)
            new_highest_note, new_highest_octave = self.number_to_note(new_highest)
            
            print(f"\n🎼 MÚSICA TRANSPOSTA:")
            print(f"   • Nova nota mais grave: {new_lowest_note}{new_lowest_octave}")
            print(f"   • Nova nota mais aguda: {new_highest_note}{new_highest_octave}")
            
            print(f"\n📋 MARGEM DE CONFORTO:")
            margin_low = new_lowest - vocal_range['lowest']
            margin_high = vocal_range['highest'] - new_highest
            print(f"   • Margem grave: {margin_low} semitons")
            print(f"   • Margem aguda: {margin_high} semitons")
            
            # Avaliação da margem
            if margin_low >= 2 and margin_high >= 2:
                print("   ✅ Margens adequadas para execução confortável")
            elif margin_low >= 1 and margin_high >= 1:
                print("   ⚠️  Margens justas - cantar com cuidado")
            else:
                print("   ❌ Margens insuficientes - pode ser desconfortável")
        else:
            print(f"   ❌ {message}")


# Exemplo de uso
if __name__ == "__main__":
    # Criar calculadora
    calc = VocalRangeCalculator()
    
    # Exemplo 1: Definir extensão vocal do cantor
    print("Exemplo 1: Cantor com extensão de Dó2 até Sol4")
    vocal_range = calc.define_vocal_range('Dó', 2, 'Sol', 4)
    
    # Exemplo 2: Definir extensão da música com tonalidade
    print("\nMúsica original: Fá3 até Ré5 em Dó Maior (C)")
    song_range = calc.define_song_range('Fá', 3, 'Ré', 5, 'C')
    
    # Análise completa
    calc.analyze_singer_song(vocal_range, song_range)
    
    print("\n" + "=" * 60)
    print("Teste com música em tonalidade menor:")
    print("=" * 60)
    
    # Exemplo de música em tonalidade menor
    song_range2 = calc.define_song_range('Ré', 3, 'Si', 4, 'Am')
    calc.analyze_singer_song(vocal_range, song_range2)
    
    print("\n" + "=" * 60)
    print("Teste de transposição de tonalidades:")
    print("=" * 60)
    
    # Teste direto de transposição de tonalidade
    original_keys = ['C', 'Am', 'G', 'Em', 'F', 'Dm']
    transpose_values = [2, -3, 5, -1]
    
    print("Exemplos de transposição de tonalidades:")
    for key in original_keys[:3]:
        for semitones in transpose_values[:2]:
            new_key = calc.transpose_key(key, semitones)
            print(f"   • {key} ({calc.get_key_name_pt(key)}) {semitones:+d} semitons → {new_key} ({calc.get_key_name_pt(new_key)})")
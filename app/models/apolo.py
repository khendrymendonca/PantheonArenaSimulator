from .personagem import Personagem
from .carta import Carta
from .alvos import TipoAlvo
import random

class Apolo(Personagem):
    def __init__(self):
        super().__init__("Apolo", atq=3, defesa=2, dom=4, res=2)
        # Benção: Energia Solar
        self.pes = 0 # Pontos de Energia Solar (Máx 1 ganho por turno)
        self.dano_causado_neste_turno = False
        self.passiva_selecionada = 0
        self.criar_baralho() 

    def escolher_passiva(self, id_passiva):
        self.passiva_selecionada = id_passiva
        
        if id_passiva == 1: # Calor Estelar
            self.defesa += 1
            
        elif id_passiva == 2: # Cabeça Quente
            self.vida_atual -= 5
            self.adicionar_efeito('immune_dot', 999) # Imunidade simulada
            
        elif id_passiva == 3: # Matador da Píton
            # Custo +2 tratado em obter_custo_carta
            # Efeitos on-hit tratados em jogo.py
            pass
            
        elif id_passiva == 4: # Punição de Niobe
            self.atq += 1

    def ao_iniciar_turno_personagem(self):
        self.dano_causado_neste_turno = False

    def ao_causar_dano(self):
        # Benção do Apolo: Ganha 1 PES se causar dano (1x por turno)
        if not self.dano_causado_neste_turno:
            self.pes += 1
            self.dano_causado_neste_turno = True
            return True # Retorna True se ganhou PES para logar
        return False

    def ativar_bencao_solar(self):
        # Gasta 3 PES para +1 Energia
        if self.pes >= 3:
            self.pes -= 3
            self.energia += 1
            return True
        return False

    def obter_custo_carta(self, carta):
        custo = carta.custo
        # Passiva 3: Matador da Píton (Habilidades com ATQ custam 2 a mais)
        if self.passiva_selecionada == 3 and carta.tipo == 'atq':
            custo += 2
        return custo

    def to_dict(self):
        data = super().to_dict()
        data['pes'] = self.pes
        data['passiva_selecionada'] = self.passiva_selecionada
        return data

    def criar_baralho(self):
        baralho = []
        # Mantendo baralho padrão por enquanto para focar na lógica das passivas
        # 3x Flecha de Ouro
        for _ in range(3):
            baralho.append(Carta(2, "Flecha de Ouro", "Causa 1d6 + ATQ.", "atq", 
                               efeitos=[{"id": "dano_fisico", "dano": "1d6", "atributo": "atq"}]))
        # 3x Luz Solar
        for _ in range(3):
            baralho.append(Carta(2, "Luz Solar", "Cura 1d6 + DOM.", "magia", 
                               efeitos=[{"id": "cura", "dano": "1d6", "atributo": "dom"}]))
        # 2x Disparo Preciso
        for _ in range(2):
            baralho.append(Carta(3, "Disparo Preciso", "Causa 1d4 + ATQ (Ignora DEF).", "atq", 
                               efeitos=[{"id": "dano_direto", "dano": "1d4", "atributo": "atq"}]))
        # 2x Égide Solar
        for _ in range(2):
            baralho.append(Carta(1, "Égide Solar", "Aumenta DEF +2 (2 Turnos).", "buff", 
                               efeitos=[{"id": "buff_defesa", "valor": 2, "turnos": 2}]))

        self.baralho = baralho
        random.shuffle(self.baralho)

    def obter_custo_carta(self, carta):
        """Retorna o custo da carta, aplicando modificadores de passiva."""
        custo = carta.custo
        # Passiva 3: Matador da Píton - Habilidades com ATQ custam 2 a mais
        if self.passiva_selecionada == 3 and carta.tipo == 'atq':
            custo += 2
        return custo

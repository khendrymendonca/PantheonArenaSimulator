import random

class Personagem:
    def __init__(self, nome, atq=2, defesa=2, dom=2, res=2):
        self.nome = nome
        self.vida_atual = 30 # Começa com 30, mas sobe sem limite
        
        # --- ATRIBUTOS ---
        # Você pode ajustar esses valores base para cada personagem
        self.atq = atq      # Ataque Físico (influencia dano de cartas de ATQ)
        self.defesa = defesa # Defesa Física (reduz dano físico recebido)
        self.dom = dom      # Domínio (influencia cura e dano mágico)
        self.res = res      # Resistência Mágica (reduz dano mágico recebido)
        
        # --- ENERGIA ---
        self.energia = 0 # Energia disponível para usar cartas no turno
        
        # --- CARTAS ---
        self.baralho = [] # Cartas que ainda serão compradas
        self.mao = []     # Cartas na mão do jogador
        self.descarte = [] # Cartas já usadas
        
        # --- STATUS ---
        self.efeitos_ativos = [] # Veneno, Queimadura, Imunidade, etc.

    def comprar_cartas(self, quantidade=4):
        # Override se precisar de lógica especial (ex: Oráculo)
        contador = 0
        while contador < quantidade and len(self.mao) < 10:
            if not self.baralho:
                if not self.descarte:
                    break
                self.baralho = self.descarte[:]
                self.descarte = []
                self.embaralhar()
            
            carta = self.baralho.pop(0)
            self.mao.append(carta)
            contador += 1

    def embaralhar(self):
        random.shuffle(self.baralho)

    def rolar_energia(self):
        # Energia inicial = 10 + 1d6
        dado = random.randint(1, 6)
        self.energia = 10 + dado
        return dado

    def receber_dano(self, quantidade):
        # Verifica imunidades
        # Ajuste para usar dicionário de efeitos corretamente se necessário
        if self.tem_efeito('immune_attack') or self.tem_efeito('imunidade_dano'):
            return 0
        
        dano_real = max(0, quantidade)
        self.vida_atual -= dano_real
        if self.vida_atual < 0:
            self.vida_atual = 0
        return dano_real

    def curar(self, quantidade):
        # Sem limite máximo de HP
        self.vida_atual += quantidade

    def adicionar_efeito(self, tipo, duracao, valor=0):
        # Verifica imunidade a efeitos malignos
        if tipo in ['poison', 'burn', 'debuff', 'stun']:
            if self.tem_efeito('immune_dot'):
                return # Ignora aplicação
        
        # Verifica se já existe para stackar ou renovar (simples: renova duração)
        for efeito in self.efeitos_ativos:
            if efeito['tipo'] == tipo:
                efeito['duracao'] = max(efeito['duracao'], duracao)
                efeito['valor'] = valor if valor != 0 else efeito['valor']
                return
        
        self.efeitos_ativos.append({'tipo': tipo, 'duracao': duracao, 'valor': valor})

    def atualizar_efeitos(self):
        # Decrementa duração e remove expirados
        novos_efeitos = []
        for efeito in self.efeitos_ativos:
            efeito['duracao'] -= 1
            if efeito['duracao'] > 0:
                novos_efeitos.append(efeito)
        self.efeitos_ativos = novos_efeitos

    def tem_efeito(self, tipo_efeito):
        return any(e['tipo'] == tipo_efeito for e in self.efeitos_ativos)

    def obter_valor_efeito(self, tipo_efeito):
        for efeito in self.efeitos_ativos:
            if efeito['tipo'] == tipo_efeito:
                return efeito['valor']
        return 0

    def to_dict(self):
        return {
            'nome': self.nome,
            'vida': self.vida_atual, # HP atual, sem limite máximo
            'atributos': {
                'atq': self.atq,
                'defesa': self.defesa,
                'dom': self.dom,
                'res': self.res
            },
            'energia': self.energia,
            'mao': [c.to_dict() for c in self.mao],
            'efeitos': self.efeitos_ativos
        }

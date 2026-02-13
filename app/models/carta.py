from .alvos import TipoAlvo

class Carta:
    def __init__(self, id, nome, custo, tipo, valor, descricao, efeitos=None, alvo=TipoAlvo.UNICO, turnos=0):
        self.id = id
        self.nome = nome
        self.custo = custo
        self.tipo = tipo # 'atq', 'dom', 'buff', 'debuff'
        self.valor = valor # Valor base (dano fixo, dado extra, etc)
        self.descricao = descricao
        
        # Novo Sistema
        self.efeitos = efeitos if efeitos else [] # Lista de dicipionários: [{'id': 'queimadura', 'valor': 0, 'turnos': 2}]
        self.alvo = alvo
        self.turnos = turnos # Duração padrão (se efeito não especificar)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'custo': self.custo,
            'tipo': self.tipo,
            'valor': self.valor,
            'descricao': self.descricao,
            'efeitos': self.efeitos,
            'alvo': self.alvo.value,
            'turnos': self.turnos
        }

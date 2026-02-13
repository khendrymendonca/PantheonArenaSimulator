# Definição Central de Efeitos
# Aqui você pode ajustar valores, descrições e tipos de todos os efeitos do jogo.

EFEITOS = {
    # --- Efeitos de Dano ---
    'dano_fisico': {
        'nome': 'Dano Físico',
        'tipo': 'dano',
        'atributo': 'atq', # Usa ATQ do atacante
        'descricao': 'Causa dano físico ao alvo.'
    },
    'dano_magico': {
        'nome': 'Dano Mágico',
        'tipo': 'dano',
        'atributo': 'dom',
        'descricao': 'Causa dano mágico ao alvo.'
    },
    'dano_perfurante': {
        'nome': 'Dano Perfurante',
        'tipo': 'dano_direto', # Ignora defesa
        'descricao': 'Causa dano ignorando defesa.'
    },
    'dano_verdadeiro': {
        'nome': 'Dano Verdadeiro',
        'tipo': 'dano_real', # Não escala com atributo, valor fixo ou dado puro
        'descricao': 'Causa dano fixo.'
    },

    # --- Efeitos de Cura ---
    'cura': {
        'nome': 'Cura',
        'tipo': 'cura',
        'atributo': 'dom',
        'descricao': 'Restaura pontos de vida.'
    },

    # --- Buffs e Debuffs (Status) ---
    'queimadura': {
        'nome': 'Queimadura',
        'tipo': 'dot', # Damage over Time
        'dado': '1d6',
        'descricao': 'O alvo sofre 1d6 de dano no início de cada turno.'
    },
    'veneno': {
        'nome': 'Veneno',
        'tipo': 'dot',
        'dado': '1d4',
        'descricao': 'O alvo sofre 1d4 de dano no início de cada turno.'
    },
    'imunidade_dano': {
        'nome': 'Imunidade à Dano',
        'tipo': 'imunidade',
        'subtipo': 'ataque', # Imune apenas a ataques (cartas de dano)
        'descricao': 'O alvo não recebe dano de ataques.'
    },
    'imunidade_efeitos': {
        'nome': 'Imunidade à Efeitos',
        'tipo': 'imunidade',
        'subtipo': 'dot', # Imune a veneno/queimadura
        'descricao': 'O alvo não pode receber novos efeitos malignos.'
    },
    'aumento_atq': {
        'nome': 'Aumento de Ataque',
        'tipo': 'buff_atributo',
        'atributo': 'atq',
        'descricao': 'Aumenta o Ataque do alvo.'
    },
    'reducao_defesa': {
        'nome': 'Quebrar Defesa',
        'tipo': 'debuff_atributo',
        'atributo': 'defesa',
        'descricao': 'Reduz a Defesa do alvo.'
    },
    
    # --- Efeitos Especiais ---
    'oraculo': {
        'nome': 'Oráculo',
        'tipo': 'especial',
        'funcao': 'ver_topo_deck',
        'descricao': 'Permite ver a carta do topo do baralho.'
    },
    'limpar_efeitos': {
        'nome': 'Purificação',
        'tipo': 'limpeza',
        'alvo_efeito': 'negativo', # Remove debuffs/dots
        'descricao': 'Remove todos os efeitos malignos do alvo.'
    }
}

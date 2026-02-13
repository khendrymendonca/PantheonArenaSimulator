from .efeitos import EFEITOS
from .alvos import TipoAlvo
import re
import random

class Jogo:
    def __init__(self):
        self.jogadores = {}  # {sid: personagem}
        self.ordem_turnos = [] # Lista de SIDs
        self.iniciativas = {}  # {sid: valor_d20}
        self.indice_turno = 0
        self.jogador_turno_sid = None
        self.fase = 'espera' # 'espera', 'energia', 'revelacao', 'acao', 'concluido'
        self.vencedor = None
        self.logs = []
        self.contador_turnos = 0
        self.max_jogadores = 20
        self.id_mestre = None

    def log(self, mensagem):
        self.logs.append(mensagem)
        if len(self.logs) > 50:
            self.logs.pop(0)

    def iniciar_jogo(self):
        if len(self.jogadores) < 2:
            return False
        
        self.log("Rando a iniciativa (1d20)...")
        # Rolar 1d20 para cada jogador
        self.iniciativas = {}
        for sid, p in self.jogadores.items():
            roll = random.randint(1, 20)
            self.iniciativas[sid] = roll
            self.log(f"{p.nome} rolou {roll} de iniciativa.")
            
        # Ordenar por iniciativa (maior para menor)
        sids_ordenados = sorted(self.jogadores.keys(), key=lambda s: self.iniciativas[s], reverse=True)
        
        self.ordem_turnos = sids_ordenados
        self.indice_turno = 0
        self.jogador_turno_sid = self.ordem_turnos[0]
        self.fase = 'energia'
        self.contador_turnos = 0
        self.log(f"Ordem de batalha: " + " -> ".join([self.jogadores[s].nome for s in self.ordem_turnos]))
        self.iniciar_turno()
        return True

    def adicionar_jogador(self, sid, nome, id_personagem='apolo', id_passiva=1):
        if self.fase != 'espera' and len(self.jogadores) >= 20:
             return False, "O jogo já começou ou está lotado."
             
        if len(self.jogadores) >= self.max_jogadores:
            return False, "Arena lotada (máx 20 jogadores)."
        
        if sid in self.jogadores:
            return False, "Você já está na arena."

        if not self.id_mestre:
            self.id_mestre = sid

        from .apolo import Apolo 
        
        CLASSES = {
            'apolo': Apolo,
        }
        
        classe_escolhida = CLASSES.get(id_personagem, Apolo)
        novo_jogador = classe_escolhida()
        novo_jogador.nome = nome # Garantir que o nome seja setado
        novo_jogador.sid = sid 
        
        try:
            if hasattr(novo_jogador, 'escolher_passiva'):
                novo_jogador.escolher_passiva(int(id_passiva))
                self.log(f"{nome} entrou na Arena.")
        except Exception as e:
            print(f"Erro ao aplicar passiva: {e}")

        self.jogadores[sid] = novo_jogador
        return True, "Entrou na arena."

    def obter_estado(self):
        return {
            'jogadores': {sid: p.to_dict() for sid, p in self.jogadores.items()},
            'turno_sid': self.jogador_turno_sid,
            'fase': self.fase,
            'logs': self.logs,
            'vencedor': self.vencedor,
            'id_mestre': self.id_mestre,
            'iniciativas': self.iniciativas
        }

    def calcular_dano(self, dano_base, atacante, defensor, tipo='fisico'):
        mitigacao = 0
        if tipo == 'fisico':
            mitigacao = defensor.defesa
        elif tipo == 'magico':
            mitigacao = defensor.res
            
        dano_final = max(0, dano_base - mitigacao)
        return dano_final

    def iniciar_turno(self):
        if not self.jogador_turno_sid: return
        
        self.contador_turnos += 1
        atual = self.obter_jogador_atual()
        if not atual: return
        
        # Fase 0: Atualização de Efeitos
        atual.atualizar_efeitos()
        if hasattr(atual, 'ao_iniciar_turno_personagem'):
            atual.ao_iniciar_turno_personagem()
        
        # Dots
        if atual.tem_efeito('veneno'):
            dano = random.randint(1, 4)
            atual.receber_dano(dano)
            self.log(f"{atual.nome} sofreu {dano} de dano por Veneno.")
            
        if atual.tem_efeito('queimadura'):
            dano = random.randint(1, 6)
            atual.receber_dano(dano)
            self.log(f"{atual.nome} sofreu {dano} de dano por Queimadura.")

        # Fase 1: Energia
        self.fase = 'energy'
        rolagem = atual.rolar_energia()
        
        if atual.tem_efeito('energia_proximo_turno'):
            extra = atual.obter_valor_efeito('energia_proximo_turno')
            atual.energia += extra
            self.log(f"[Passiva] {atual.nome} ganhou +{extra} de Energia extra.")

        self.log(f"[Turno {self.contador_turnos}] {atual.nome} rolou {rolagem} de energia. Total: {atual.energia}")
        
        # Fase 2: Revelação
        self.fase = 'revelacao'
        atual.comprar_cartas()
        
        # Fase 3: Ação
        self.fase = 'acao'

    def obter_jogador_atual(self):
        return self.jogadores.get(self.jogador_turno_sid)

    def jogar_carta(self, sid, indice_carta, alvo_sid=None):
        if self.fase != 'acao':
            return {'erro': 'Não é fase de ação.'}
        if sid != self.jogador_turno_sid:
            return {'erro': 'Não é seu turno.'}
        
        atacante = self.obter_jogador_atual()
        
        if indice_carta < 0 or indice_carta >= len(atacante.mao):
            return {'erro': 'Carta inválida.'}
            
        carta = atacante.mao[indice_carta]
        
        # Define Defensor
        if not alvo_sid and len(self.jogadores) > 1:
            # Se for cura/buff em si mesmo, ok. Se for dano, precisa de alvo.
            if carta.alvo != TipoAlvo.SI_MESMO:
                return {'erro': 'Alvo não selecionado.'}
        
        defensor = self.jogadores.get(alvo_sid) if alvo_sid else None
        
        custo = atacante.obter_custo_carta(carta) if hasattr(atacante, 'obter_custo_carta') else carta.custo
        
        if atacante.energia < custo:
            return {'erro': f'Energia insuficiente. Custo: {custo}'}
            
        atacante.energia -= custo
        atacante.mao.pop(indice_carta)
        atacante.descarte.append(carta)
        
        self.log(f"{atacante.nome} usou {carta.nome}.")

        self.processar_efeitos_carta(carta, atacante, defensor)
        
        # Verificar Mortes e Vitória
        # Remove jogadores com vida 0 e verifica se restou apenas 1
        sids_mortos = [s for s, p in self.jogadores.items() if p.vida_atual <= 0]
        for s in sids_mortos:
            p = self.jogadores[s]
            self.log(f"{p.nome} foi derrotado!")
            del self.jogadores[s]
            if s in self.ordem_turnos:
                self.ordem_turnos.remove(s)

        if len(self.jogadores) <= 1:
            self.fase = 'concluido'
            self.vencedor = list(self.jogadores.values())[0].nome if self.jogadores else "Ninguém"
            self.log(f"Fim de jogo! Vencedor: {self.vencedor}")

        return {'sucesso': True}

    def processar_efeitos_carta(self, carta, atacante, defensor):
        alvos = [defensor] # Default unico inimigo
        if carta.alvo == TipoAlvo.SI_MESMO:
            alvos = [atacante]
        # TODO: Implementar AREA quando tivermos arrays de jogadores
        
        dano_total_causado = 0
        
        for alvo in alvos:
            for efeito_config in carta.efeitos:
                id_efeito = efeito_config.get('id')
                definicao = EFEITOS.get(id_efeito)
                
                if not definicao:
                    self.log(f"ERRO: Efeito {id_efeito} não definido.")
                    continue
                
                # Lógica baseada no TIPO do efeito
                tipo = definicao.get('tipo')
                
                if tipo == 'dano':
                    dado = efeito_config.get('dado') or definicao.get('dado', '1d4')
                    # Rolar dado

                    match = re.match(r'(\d+)d(\d+)', dado)
                    valor_dano = 0
                    if match:
                        qtd_dados = int(match.group(1))
                        lados = int(match.group(2))
                        for _ in range(qtd_dados):
                            valor_dano += random.randint(1, lados)
                    
                    # Somar atributo
                    atributo_nome = definicao.get('atributo')
                    bonus = getattr(atacante, atributo_nome, 0)
                    valor_dano += bonus
                    
                    # Mitigação
                    if definicao.get('nome') == 'Dano Físico':
                        dano_final = self.calcular_dano(valor_dano, atacante, alvo, 'fisico')
                    elif definicao.get('nome') == 'Dano Mágico':
                        dano_final = self.calcular_dano(valor_dano, atacante, alvo, 'magico')
                    else:
                        dano_final = valor_dano
                        
                    realizado = alvo.receber_dano(dano_final)
                    dano_total_causado += realizado
                    self.log(f"Causou {realizado} de {definicao['nome']} em {alvo.nome}.")
                    
                    # Hook de causar dano para Benção (PES) e passivas
                    if realizado > 0:
                        if hasattr(atacante, 'ao_causar_dano'):
                            if atacante.ao_causar_dano():
                                self.log(f"[Benção] {atacante.nome} ganhou 1 Ponto de Energia Solar (PES).")
                                
                        # Passiva 3 de Apolo (Matador da Píton): Energia extra no próximo turno
                        if hasattr(atacante, 'passiva_selecionada') and atacante.passiva_selecionada == 3:
                            if alvo.tem_efeito('veneno') or alvo.tem_efeito('poison'):
                                # Usamos um efeito para dar energia no próximo turno
                                if not atacante.tem_efeito('energia_proximo_turno'):
                                    atacante.adicionar_efeito('energia_proximo_turno', 1, valor=1)
                                    self.log(f"[Passiva] {atacante.nome} ganhará +1 Energia no próximo turno por atacar alvo envenenado.")

                elif tipo == 'dano_direto': # Perfurante / Ignora Defesa
                    dado = efeito_config.get('dado', '1d4')
                    match = re.match(r'(\d+)d(\d+)', dado)
                    valor_dano = 0
                    if match:
                        qtd_dados = int(match.group(1))
                        lados = int(match.group(2))
                        for _ in range(qtd_dados):
                            valor_dano += random.randint(1, lados)
                    
                    bonus = getattr(atacante, 'atq', 0) # Geralmente escala com ATQ
                    valor_dano += bonus
                    
                    realizado = alvo.receber_dano(valor_dano)
                    dano_total_causado += realizado
                    self.log(f"Causou {realizado} de {definicao['nome']} (Ignora Defesa).")
                    
                    # Hook de causar dano
                    if realizado > 0:
                        if hasattr(atacante, 'ao_causar_dano'):
                            if atacante.ao_causar_dano():
                                self.log(f"[Benção] {atacante.nome} ganhou 1 Ponto de Energia Solar (PES).")

                elif tipo == 'cura':
                    dado = efeito_config.get('dado', '1d6')
                    match = re.match(r'(\d+)d(\d+)', dado)
                    valor_cura = 0
                    if match:
                        qtd_dados = int(match.group(1))
                        lados = int(match.group(2))
                        for _ in range(qtd_dados):
                            valor_cura += random.randint(1, lados)
                            
                    atributo_nome = definicao.get('atributo')
                    bonus = getattr(atacante, atributo_nome, 0)
                    valor_cura += bonus
                    
                    alvo.curar(valor_cura)
                    self.log(f"Curou {valor_cura} pontos de vida.")

                elif tipo == 'dot' or tipo == 'imunidade':
                    turnos = efeito_config.get('turnos') or carta.turnos or 1
                    alvo.adicionar_efeito(id_efeito, turnos)
                    self.log(f"Aplicou {definicao['nome']} por {turnos} turnos.")

                elif tipo == 'especial':
                    if definicao.get('funcao') == 'ver_topo_deck':
                        if len(atacante.baralho) > 0:
                            carta_topo = atacante.baralho[0]
                            self.log(f"{definicao['nome']}: Topo do deck é {carta_topo.nome}")
                        else:
                            self.log("Baralho vazio.")
                            
        # Hook Final da Carta: Passiva 3 de Apolo (Matador da Píton)
        # Se for carta de ATQ, aplica Veneno se não tiver.
        if hasattr(atacante, 'passiva_selecionada') and atacante.passiva_selecionada == 3:
            if carta.tipo == 'atq':
                # Só aplica se a carta já não aplicou (para não duplicar efeitos sem necessidade)
                # Na verdade a regra diz "todas causam envenenamento", então garantimos aqui.
                defensor.adicionar_efeito('veneno', 3) # Duração padrão 3 turnos
                self.log(f"[Passiva] {carta.nome} aplicou Veneno (Matador da Píton).")

    def passar_turno(self):
        if not self.ordem_turnos: return
        
        self.indice_turno = (self.indice_turno + 1) % len(self.ordem_turnos)
        self.jogador_turno_sid = self.ordem_turnos[self.indice_turno]
        self.iniciar_turno()

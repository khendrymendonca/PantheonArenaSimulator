import unittest
from app.models.apolo import Apolo
from app.models.jogo import Jogo

class TestApoloAdjustments(unittest.TestCase):
    def setUp(self):
        self.apolo = Apolo()
        self.jogo = Jogo()
        self.jogo.iniciar_jogo(self.apolo, Apolo())

    def test_composicao_baralho(self):
        # Apolo começa comprando 4 cartas no setUp -> iniciar_jogo -> iniciar_turno
        todas_cartas = self.apolo.baralho + self.apolo.mao
        self.assertEqual(len(todas_cartas), 16)
        
        contagem = {}
        for carta in todas_cartas:
            contagem[carta.nome] = contagem.get(carta.nome, 0) + 1
            
        self.assertEqual(contagem["Acorde de Cura"], 2, "Acorde de Cura deve ter 2 cópias")
        self.assertEqual(contagem["Flecha de Ouro"], 3, "Flecha de Ouro deve ter 3 cópias")
        self.assertEqual(contagem["Luz Milagrosa"], 1, "Luz Milagrosa deve ter 1 cópia")
        self.assertEqual(contagem["Flecha da Peste"], 2, "Flecha da Peste deve ter 2 cópias")
        self.assertEqual(contagem["Escudo de Hélio"], 2, "Escudo de Hélio deve ter 2 cópias")
        self.assertEqual(contagem["Oráculo de Delfos"], 1, "Oráculo de Delfos deve ter 1 cópia")
        self.assertEqual(contagem["Supernova"], 2, "Supernova deve ter 2 cópias")
        self.assertEqual(contagem["Disparo Certeiro"], 3, "Disparo Certeiro deve ter 3 cópias")

    def test_passiva_matador_piton_custo(self):
        self.apolo.escolher_passiva(3) # Matador da Píton
        
        # Carta de ATQ (Flecha de Ouro, custo 3)
        carta_atq = next(c for c in self.apolo.baralho if c.tipo == 'atq')
        custo = self.apolo.obter_custo_carta(carta_atq)
        self.assertEqual(custo, carta_atq.custo + 2)
        
        # Carta de BUFF (Escudo de Hélio, custo 7)
        carta_buff = next(c for c in self.apolo.baralho if c.tipo == 'buff')
        custo_buff = self.apolo.obter_custo_carta(carta_buff)
        self.assertEqual(custo_buff, carta_buff.custo)

    def test_passiva_matador_piton_aplicar_veneno(self):
        self.apolo.escolher_passiva(3)
        # Flecha de Ouro não tem veneno nativo
        carta_atq = next(c for c in self.apolo.baralho if c.nome == "Flecha de Ouro")
        
        oponente = self.jogo.jogador2
        # Mock log para não poluir
        self.jogo.log = lambda x: None
        
        # self.apolo.aplicar_efeito_carta(carta_atq, oponente, self.jogo) -> ANTIGO
        self.jogo.processar_efeitos_carta(carta_atq, self.apolo, oponente)
        
        self.assertTrue(oponente.tem_efeito('veneno'), "Deve aplicar veneno pela passiva")

    def test_passiva_matador_piton_ganho_energia(self):
        self.apolo.escolher_passiva(3)
        oponente = self.jogo.jogador2
        oponente.adicionar_efeito('veneno', 1) # Já envenenado
        
        carta_atq = next(c for c in self.apolo.baralho if c.nome == "Flecha de Ouro")
        
        # Mock calculation
        # self.jogo.calcular_dano = lambda d, a, df, t: 10 # Não precisa mockar se a lógica nova funciona
        self.jogo.log = lambda x: None
        
        # Simula hit
        # self.apolo.aplicar_efeito_carta(carta_atq, oponente, self.jogo) -> ANTIGO
        self.jogo.processar_efeitos_carta(carta_atq, self.apolo, oponente)
        
        self.assertTrue(self.apolo.tem_efeito('energia_proximo_turno'), "Deve ganhar flag de energia extra")
        self.assertEqual(self.apolo.obter_valor_efeito('energia_proximo_turno'), 1)

if __name__ == '__main__':
    unittest.main()

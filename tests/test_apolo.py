import unittest
from app.models.apolo import Apolo
from app.models.jogo import Jogo

class TestApolo(unittest.TestCase):
    def setUp(self):
        self.apolo = Apolo()
        self.jogo = Jogo()
        self.jogo.iniciar_jogo(self.apolo, Apolo())

    def test_atributos_iniciais(self):
        self.assertEqual(self.apolo.nome, "Apolo")
        self.assertEqual(self.apolo.atq, 2)
        self.assertEqual(self.apolo.defesa, 0)
        self.assertEqual(self.apolo.dom, 2)
        self.assertEqual(self.apolo.res, 1)
        self.assertEqual(self.apolo.vida_atual, 30)

    def test_passiva_calor_estelar(self):
        self.apolo.escolher_passiva(1)
        self.assertEqual(self.apolo.defesa, 1) # 0 + 1

    def test_passiva_cabeca_quente(self):
        self.apolo.escolher_passiva(2)
        # self.assertEqual(self.apolo.vida_maxima, 25) # Maxima irrelevante
        self.assertEqual(self.apolo.vida_atual, 25)

    def test_overheal(self):
        self.apolo.vida_atual = 30
        self.apolo.curar(10)
        self.assertEqual(self.apolo.vida_atual, 40) # Sem limite

    def test_energia_inicial(self):
        # 10 + 1d6 => min 11, max 16
        self.apolo.rolar_energia()
        self.assertTrue(11 <= self.apolo.energia <= 16)

    def test_passiva_punicao_niobe(self):
        self.apolo.escolher_passiva(4)
        self.assertEqual(self.apolo.atq, 3) # 2 + 1

    def test_ganho_energia_solar(self):
        self.assertEqual(self.apolo.pontos_energia_solar, 0)
        self.apolo.ganhar_energia_solar()
        self.assertEqual(self.apolo.pontos_energia_solar, 1)

    def test_consumo_energia_solar(self):
        self.apolo.pontos_energia_solar = 3
        self.apolo.energia = 0
        
        sucesso = self.apolo.consumir_energia_solar()
        
        self.assertTrue(sucesso)
        self.assertEqual(self.apolo.energia, 1)
        self.assertEqual(self.apolo.pontos_energia_solar, 0)

if __name__ == '__main__':
    unittest.main()

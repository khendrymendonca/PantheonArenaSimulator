import unittest
from tests.test_apolo_adjustments import TestApoloAdjustments

def run_test(name):
    print(f"Running {name}...")
    suite = unittest.TestSuite()
    suite.addTest(TestApoloAdjustments(name))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        print(f"FAILED: {name}")
    else:
        print(f"PASSED: {name}")

run_test('test_composicao_baralho')
run_test('test_passiva_matador_piton_custo')
run_test('test_passiva_matador_piton_aplicar_veneno')
run_test('test_passiva_matador_piton_ganho_energia')

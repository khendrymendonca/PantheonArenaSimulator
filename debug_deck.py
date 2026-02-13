from app.models.apolo import Apolo
a = Apolo()
c = {}
for card in a.baralho:
    c[card.nome] = c.get(card.nome, 0) + 1
for k, v in sorted(c.items()):
    print(f"{k}: {v}")

from flask import request
from flask_socketio import emit
from . import socketio
from .models.jogo import Jogo

# Instância global do jogo
instancia_jogo = Jogo()

@socketio.on('connect')
def handle_connect():
    emit('estado_jogo', instancia_jogo.obter_estado())

@socketio.on('entrar_jogo')
def handle_join(data):
    nome = data.get('nome')
    id_personagem = data.get('personagem', 'apolo')
    id_passiva = data.get('passiva', 1)
    
    # Reinicia se estava concluído
    if instancia_jogo.fase == 'concluido':
        instancia_jogo.__init__()

    sucesso, msg = instancia_jogo.adicionar_jogador(request.sid, nome, id_personagem, id_passiva)
    
    if not sucesso:
        emit('erro', msg)
    else:
        emit('estado_jogo', instancia_jogo.obter_estado(), broadcast=True)

@socketio.on('jogar_carta')
def handle_play_card(data):
    indice_carta = data.get('indice_carta')
    alvo_sid = data.get('alvo_sid')
    
    resultado = instancia_jogo.jogar_carta(request.sid, indice_carta, alvo_sid)
    
    if resultado.get('erro'):
        emit('erro', resultado['erro'])
    else:
        emit('estado_jogo', instancia_jogo.obter_estado(), broadcast=True)

@socketio.on('passar_turno')
def handle_end_turn(data):
    if instancia_jogo.jogador_turno_sid == request.sid:
        instancia_jogo.passar_turno()
        emit('estado_jogo', instancia_jogo.obter_estado(), broadcast=True)
    else:
        emit('erro', "Não é o seu turno.")

@socketio.on('reiniciar')
def handle_restart():
    global instancia_jogo
    instancia_jogo = Jogo()
    emit('estado_jogo', instancia_jogo.obter_estado(), broadcast=True)

@socketio.on('ativar_bencao')
def handle_activate_blessing(data):
    jogador = instancia_jogo.jogadores.get(request.sid)
    if jogador and hasattr(jogador, 'ativar_bencao_solar'):
        if jogador.ativar_bencao_solar():
            instancia_jogo.log(f"{jogador.nome} ativou Efeito de Passiva (+1 Energia)!")
            emit('estado_jogo', instancia_jogo.obter_estado(), broadcast=True)
        else:
            emit('erro', 'PES insuficientes!')

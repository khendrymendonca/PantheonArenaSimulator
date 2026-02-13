import socketio
import sys
import threading
import time
import os

# Configurações do Cliente
sio = socketio.Client()
SERVER_URL = "http://localhost:5000"
estado_jogo = None
minha_vez = False
meu_sid = None

# Utilitários de Interface
def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print("###########################################")
    print("#       PANTHEON ARENA - NATIVA CLI       #")
    print("#    Operação de Terminal Direta v1.1.0   #")
    print("###########################################\n")

# Eventos do SocketIO
@sio.event
def connect():
    global meu_sid
    meu_sid = sio.sid
    print(f"[SISTEMA] Conexão estabelecida. ID: {meu_sid}")

@sio.on('estado_jogo')
def on_state(data):
    global estado_jogo, minha_vez
    estado_jogo = data
    minha_vez = (data.get('turno_sid') == meu_sid)
    # Não vamos limpar a tela a cada update para manter o histórico tipo script
    renderizar_estado()

@sio.on('erro')
def on_error(msg):
    print(f"\n[ERRO] {msg}")

# Lógica de Renderização
def renderizar_estado():
    if not estado_jogo:
        return

    eu = estado_jogo['jogadores'].get(meu_sid)
    fase = estado_jogo.get('fase')

    if fase == 'espera':
        jogadores = [p['nome'] for p in estado_jogo['jogadores'].values()]
        print(f"\r> SALA DE ESPERA: [ {' , '.join(jogadores)} ]", end="")
        if estado_jogo.get('id_mestre') == meu_sid:
            print("\n> VOCÊ É O MESTRE. Digite 'iniciar' para começar.")
        return

    # Se estiver em batalha, mostrar status compacto
    if fase != 'espera' and eu:
        print("\n" + "-"*45)
        print(f"PORTADOR: {eu['nome']} | HP: {eu['vida']} | ENERGIA: {eu['energia']} | PES: {eu.get('pes', 0)}")
        
        # Oponentes
        oponentes = []
        for sid, p in estado_jogo['jogadores'].items():
            if sid != meu_sid:
                oponentes.append(f"{p['nome']}({p['vida']} HP)")
        print(f"OPONENTES: {' | '.join(oponentes)}")
        
        # Mão (se for meu turno)
        if minha_vez:
            print("\nSUA VEZ! COMANDOS DISPONÍVEIS:")
            for i, carta in enumerate(eu['mao']):
                print(f"  [{i+1}] {carta['nome']} ({carta['custo']} EN) - {carta['descricao']}")
            print("-"*45)
            print("Digite: jogar [N] [ALVO], passar, status, iniciar, help")

# Loop de Entrada
def loop_comandos():
    while True:
        try:
            prompt = "\rC:\\PANTHEON\\ARENA> "
            cmd_full = input(prompt).strip().lower()
            if not cmd_full:
                continue
            
            partes = cmd_full.split()
            acao = partes[0]

            if acao == 'iniciar':
                sio.emit('iniciar_partida')
            elif acao in ['jogar', 'usar']:
                if len(partes) < 2:
                    print("[AVISO] Use: jogar [N] [OPONENTE_NUM]")
                    continue
                
                idx_carta = int(partes[1]) - 1
                alvo_num = int(partes[2]) - 1 if len(partes) > 2 else None
                
                # Mapear alvo_num para SID
                sids_oponentes = [s for s in estado_jogo['jogadores'].keys() if s != meu_sid]
                alvo_sid = sids_oponentes[alvo_num] if alvo_num is not None and alvo_num < len(sids_oponentes) else None
                
                sio.emit('jogar_carta', {'indice_carta': idx_carta, 'alvo_sid': alvo_sid})
            elif acao in ['passar', 'fim']:
                sio.emit('passar_turno')
            elif acao == 'status':
                renderizar_estado()
            elif acao == 'help':
                print("\nLISTA DE COMANDOS:")
                print("  iniciar          - Começa a partida (se for mestre)")
                print("  jogar [N] [A]    - Usa a carta N no alvo A")
                print("  passar           - Encerra seu turno")
                print("  status           - Mostra o estado atual")
                print("  sair             - Fecha o cliente")
            elif acao == 'sair':
                sio.disconnect()
                sys.exit()
            else:
                print(f"[AVISO] Comando '{acao}' desconhecido. Use 'help'.")
        except Exception as e:
            print(f"[ERRO DE ENTRADA] {e}")

# Main
if __name__ == "__main__":
    limpar_tela()
    print_banner()

    nome = input("DIGITE SEU NOME DE PORTADOR: ").strip()
    print("\nCLASSES DISPONÍVEIS:\n[1] APOLO - ARQUEIRO SOLAR")
    classe_input = input("ESCOLHA SUA CLASSE [1]: ").strip()
    classe = "apolo" if classe_input == "1" else "apolo"

    print("\nVONTADES DISPONÍVEIS:\n[1] CALOR ESTELAR | [2] CABEÇA QUENTE | [3] MATADOR PÍTON | [4] NIOBE")
    passiva = input("ESCOLHA SUA PASSIVA [1-4]: ").strip() or "1"

    try:
        sio.connect(SERVER_URL)
        sio.emit('entrar_jogo', {
            'nome': nome,
            'personagem': classe,
            'passiva': int(passiva)
        })

        # Rodar loop de entrada em thread para não travar o socket
        thread = threading.Thread(target=loop_comandos, daemon=True)
        thread.start()

        # Manter main vivo
        while sio.connected:
            time.sleep(1)
    except Exception as e:
        print(f"\n[FALHA] Não foi possível conectar ao servidor: {e}")

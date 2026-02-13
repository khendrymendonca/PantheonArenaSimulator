const socket = io();
const output = document.getElementById('terminal-output');
const input = document.getElementById('command-input');

let estadoAtual = null;
let faseLocal = 'login'; // login, personagem, passiva, lobby, batalha
let tempDadosLogin = { nome: '', personagem: 'apolo' };

// --- FUNÇÕES DE INTERFACE CLI ---
function print(msg, className = '') {
    const div = document.createElement('div');
    if (className) div.className = className;
    div.innerHTML = msg;
    output.appendChild(div);
    output.scrollTop = output.scrollHeight;
}

function clear() {
    output.innerHTML = '';
}

// --- BOOT UP ---
window.onload = () => {
    print('###########################################', 'line-amber');
    print('#       PANTHEON ARENA - OS v1.0.5        #', 'line-amber line-bold');
    print('#    (c) 2026 Elísia Corp. System Root    #', 'line-amber');
    print('###########################################', 'line-amber');
    print('');
    print('INICIALIZANDO PROTOCOLOS DE REDE...');
    print('CONECTADO AO NÓ: GRANDE_ÉDEN_CENTRAL', 'line-green');
    print('');
    print('AUTENTICAÇÃO NECESSÁRIA.', 'line-bold');
    print('DIGITE SEU NOME DE PORTADOR:');
    input.focus();
};

// --- INTERPRETADOR DE COMANDOS ---
input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const cmd = input.value.trim();
        input.value = '';
        processarComando(cmd);
    }
});

function processarComando(cmd) {
    if (!cmd) return;
    print(`> ${cmd}`, 'line-green');

    if (faseLocal === 'login') {
        tempDadosLogin.nome = cmd;
        faseLocal = 'personagem';
        print('');
        print('CLASSES DISPONÍVEIS:');
        print('[1] APOLO - ARQUEIRO SOLAR');
        print('DIGITE O NÚMERO DA CLASSE:');
        return;
    }

    if (faseLocal === 'personagem') {
        if (cmd === '1' || cmd.toLowerCase() === 'apolo') {
            tempDadosLogin.personagem = 'apolo';
            faseLocal = 'passiva';
            print('');
            print('SELECIONE A VONTADE (PASSIVA):');
            print('[1] CALOR ESTELAR (DEF +1)');
            print('[2] CABEÇA QUENTE (IMUNE DOT, HP -5)');
            print('[3] MATADOR DA PÍTON (ENERGIA AO ATACAR ENVENENADOS)');
            print('[4] PUNIÇÃO DE NIOBE (ATQ +1)');
            print('DIGITE O NÚMERO DA PASSIVA:');
        } else {
            print('CLASSE INVÁLIDA. TENTE "1" PARA APOLO.', 'line-red');
        }
        return;
    }

    if (faseLocal === 'passiva') {
        const p = parseInt(cmd);
        if (p >= 1 && p <= 4) {
            socket.emit('entrar_jogo', {
                nome: tempDadosLogin.nome,
                personagem: tempDadosLogin.personagem,
                passiva: p
            });
            faseLocal = 'espera_servidor';
            print('');
            print('SOLICITANDO ENTRADA NA ARENA...', 'line-amber');
        } else {
            print('PASSIVA INVÁLIDA. TENTE 1, 2, 3 OU 4.', 'line-red');
        }
        return;
    }

    if (faseLocal === 'lobby' || faseLocal === 'batalha') {
        const partes = cmd.toLowerCase().split(' ');
        const acao = partes[0];

        if (acao === 'iniciar' && estadoAtual.id_mestre === socket.id) {
            socket.emit('iniciar_partida');
        } else if (acao === 'jogar' || acao === 'usar') {
            const index = parseInt(partes[1]) - 1;
            const alvo = partes[2] ? parseInt(partes[2]) - 1 : null;
            jogarCartaCLI(index, alvo);
        } else if (acao === 'passar' || acao === 'fim') {
            socket.emit('passar_turno');
        } else if (acao === 'status') {
            mostrarStatusCLI();
        } else if (acao === 'bencao' || acao === 'pes') {
            socket.emit('ativar_bencao');
        } else if (acao === 'help' || acao === '?') {
            print('COMANDOS DISPONÍVEIS:');
            print('  jogar [N] [ALVO] - Usa uma carta da sua mão');
            print('  passar           - Encerra seu turno');
            print('  status           - Mostra o estado da arena');
            print('  bencao           - Ativa o efeito de passiva (3 PES)');
            print('  iniciar          - (Mestre) Começa a partida');
        } else {
            print(`COMANDO DESCONHECIDO: ${acao}. DIGITE "help" PARA LISTAR.`, 'line-red');
        }
    }
}

// --- NETWORK EVENTS ---
socket.on('estado_jogo', (estado) => {
    const antigaFase = estadoAtual ? estadoAtual.fase : 'nenhuma';
    estadoAtual = estado;

    // Se mudou de espera para jogo
    if (antigaFase === 'espera' && estado.fase !== 'espera') {
        clear();
        print('--- ARENA INICIALIZADA ---', 'line-header');
        faseLocal = 'batalha';
    } else if (faseLocal === 'espera_servidor' && estado.fase === 'espera') {
        faseLocal = 'lobby';
        clear();
        print('--- SALA DE ESPERA ---', 'line-header');
    }

    renderizarEstadoCLI(estado);
});

socket.on('erro', (msg) => {
    print(`[ERROR] ${msg}`, 'line-red');
});

// --- RENDERIZAÇÃO CLI ---
function renderizarEstadoCLI(estado) {
    const meuSid = socket.id;
    const eu = estado.jogadores[meuSid];
    if (!eu) return;

    if (estado.fase === 'espera') {
        const lista = Object.values(estado.jogadores).map(p => p.nome).join(', ');
        print(`JOGADORES CONECTADOS: [ ${lista} ]`);
        if (estado.id_mestre === meuSid) {
            print('VOCÊ É O MESTRE. DIGITE "iniciar" PARA COMEÇAR.', 'line-green');
        } else {
            print('AGUARDANDO O MESTRE INICIAR...');
        }
        return;
    }

    // Se houver novos logs, imprimir apenas os últimos
    const ultimosLogs = estado.logs;
    if (ultimosLogs.length > 0) {
        print(`[LOG] ${ultimosLogs[ultimosLogs.length - 1]}`, 'line-green');
    }

    if (estado.turno_sid === meuSid) {
        print('');
        print('>>> SEU TURNO <<<', 'line-green line-bold');
        mostrarStatusCLI();
    } else {
        const nomeTurno = estado.jogadores[estado.turno_sid]?.nome || 'DESCONHECIDO';
        print(`AGUARDANDO TURNO DE: ${nomeTurno}...`);
    }
}

function mostrarStatusCLI() {
    if (!estadoAtual) return;
    const eu = estadoAtual.jogadores[socket.id];

    print('-------------------------------------------');
    print(`PORTADOR: ${eu.nome} | HP: ${eu.vida} | ENERGIA: ${eu.energia} | PES: ${eu.pes || 0}`, 'line-amber');
    print(`STATS: ATQ ${eu.atributos.atq} | DEF ${eu.atributos.defesa} | DOM ${eu.atributos.dom} | RES ${eu.atributos.res}`);

    print('');
    print('OPONENTES:');
    Object.entries(estadoAtual.jogadores).forEach(([sid, p], index) => {
        if (sid !== socket.id) {
            print(`  [${index + 1}] ${p.nome} - HP: ${p.vida} | EN: ${p.energia}`);
        }
    });

    print('');
    print('SUA MÃO:');
    eu.mao.forEach((c, i) => {
        const pode = eu.energia >= c.custo;
        print(`  [${i + 1}] ${c.nome} (Custo: ${c.custo}) - ${c.descricao}`, pode ? '' : 'line-red');
    });
    print('-------------------------------------------');
}

function jogarCartaCLI(index, alvoIndex) {
    const eu = estadoAtual.jogadores[socket.id];
    const carta = eu.mao[index];
    if (!carta) {
        print('CARTA INVÁLIDA.', 'line-red');
        return;
    }

    let alvo_sid = null;
    if (carta.tipo === 'atq' || carta.tipo === 'debuff') {
        const keys = Object.keys(estadoAtual.jogadores);
        const sidAlvo = keys[alvoIndex];
        if (!sidAlvo) {
            print('ALVO INVÁLIDO. USE: jogar [numero_carta] [numero_alvo]', 'line-red');
            return;
        }
        alvo_sid = sidAlvo;
    }

    socket.emit('jogar_carta', {
        indice_carta: index,
        alvo_sid: alvo_sid
    });
}

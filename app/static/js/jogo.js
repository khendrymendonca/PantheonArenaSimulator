const socket = io();
let estadoAtual = null;

// --- ELEMENTOS ---
const overlayLogin = document.getElementById('overlay-login');
const tabuleiro = document.getElementById('tabuleiro');
const indicadorTurno = document.getElementById('indicador-turno');
const logCorpo = document.getElementById('log-corpo');
const containerMao = document.getElementById('mao-cartas');
const btnPassarTurno = document.getElementById('btn-passar-turno');
const btnAtivarBencao = document.getElementById('btn-ativar-bencao');

// --- CONEXÃO ---
socket.on('connect', () => {
    console.log('CON_SUCCESS: PANTHEON_OS_ONLINE');
});

// --- LOBBY ---
function atualizarPassivas() {
    const sel = document.getElementById('select-personagem');
    const secao = document.getElementById('secao-passiva');
    secao.style.display = sel.value ? 'block' : 'none';
}

function entrarNaArena() {
    const nome = document.getElementById('input-nome').value.trim();
    if (!nome) {
        alert('AUTH_ERROR: IDENT_REQUIRED');
        return;
    }

    const idPersonagem = document.getElementById('select-personagem').value;
    const passivaSelecionada = document.getElementById('select-passiva').value;

    socket.emit('entrar_jogo', {
        nome: nome,
        personagem: idPersonagem,
        passiva: passivaSelecionada
    });
}

// --- CORE ---
socket.on('estado_jogo', (estado) => {
    estadoAtual = estado;
    renderizarTerminal(estado);
});

socket.on('erro', (msg) => {
    console.error('CRITICAL_ERR:', msg);
    alert('SYSTEM_ALERT: ' + msg);
});

function renderizarTerminal(estado) {
    if (!estado) return;

    const meuSid = socket.id;
    const eu = estado.jogadores[meuSid];

    // Gerenciar Telas
    if (estado.fase === 'espera') {
        overlayLogin.style.display = eu ? 'none' : 'flex';
        document.getElementById('sala-espera').style.display = eu ? 'flex' : 'none';
        tabuleiro.style.display = 'none';
        atualizarSalaEspera(estado);
        return;
    }

    overlayLogin.style.display = 'none';
    document.getElementById('sala-espera').style.display = 'none';
    tabuleiro.style.display = 'flex';

    // HUD JOGADOR
    if (eu) {
        document.getElementById('meu-nome').innerText = eu.nome.toUpperCase();
        document.getElementById('meu-hp').innerText = eu.vida;
        document.getElementById('meu-energia').innerText = eu.energia;
        document.getElementById('meu-pes').innerText = eu.pes || 0;

        document.getElementById('meu-atq').innerText = eu.atributos.atq;
        document.getElementById('meu-def').innerText = eu.atributos.defesa;
        document.getElementById('meu-dom').innerText = eu.atributos.dom;
        document.getElementById('meu-res').innerText = eu.atributos.res;

        // Barra ASCII HP
        const pct = Math.min(10, Math.ceil((eu.vida / 30) * 10));
        const barra = "[" + "||||||||||".substring(0, pct).padEnd(10, "·") + "]";
        document.getElementById('meu-hp-barra-ascii').innerText = barra;

        // Mods Ativos
        const mods = eu.efeitos && eu.efeitos.length > 0
            ? eu.efeitos.map(e => `${e.id.toUpperCase()}(${e.turnos})`).join(', ')
            : 'NONE';
        document.getElementById('meu-status-container').innerText = 'ACTIVE_MODS: ' + mods;

        // Botão Bencão
        btnAtivarBencao.style.display = eu.pes >= 3 ? 'block' : 'none';
        btnAtivarBencao.disabled = estado.turno_sid !== meuSid;
    }

    // OPONENTES
    const containerOpp = document.getElementById('container-oponentes');
    containerOpp.innerHTML = '';

    Object.entries(estado.jogadores).forEach(([sid, p]) => {
        if (sid === meuSid) return;
        const div = document.createElement('div');
        div.className = `opp-mini ${sid === estado.turno_sid ? 'ativo' : ''} ${sid === alvoSelecionadoSid ? 'alvo' : ''}`;
        div.innerHTML = `
            <div>ID: ${p.nome.toUpperCase()}</div>
            <div style="color: var(--cmd-red)">HP: ${p.vida}</div>
            <div style="font-size: 0.6rem; color: #666">EN: ${p.energia}</div>
        `;
        div.onclick = () => {
            alvoSelecionadoSid = sid;
            renderizarTerminal(estadoAtual);
        };
        containerOpp.appendChild(div);
    });

    // TURNO
    const meuTurno = estado.turno_sid === meuSid;
    btnPassarTurno.disabled = !meuTurno;

    if (estado.vencedor) {
        indicadorTurno.innerText = `WINNER_DETECTED: ${estado.vencedor.toUpperCase()}`;
    } else {
        indicadorTurno.innerText = meuTurno ? "YOUR_PROCESS_ACTIVE" : "WAITING_PROCESS_IDLE...";
    }

    // LOGS
    logCorpo.innerHTML = estado.logs.slice(-10).map(msg => `<div>${msg.toUpperCase()}</div>`).join('');
    logCorpo.scrollTop = logCorpo.scrollHeight;

    // MÃO
    renderizarMao(eu ? eu.mao : [], eu ? eu.energia : 0, meuTurno);
}

function atualizarSalaEspera(estado) {
    const lista = document.getElementById('lista-jogadores');
    lista.innerHTML = Object.values(estado.jogadores).map(p => `
        <div style="color: #666">> PLAYER_CONNECTED: ${p.nome.toUpperCase()} [READY]</div>
    `).join('');

    const btnIniciar = document.getElementById('btn-iniciar-jogo');
    if (estado.id_mestre === socket.id) {
        btnIniciar.style.display = 'block';
    }
}

let alvoSelecionadoSid = null;

function renderizarMao(cartas, energia, meuTurno) {
    containerMao.innerHTML = '';
    cartas.forEach((carta, index) => {
        const pode = meuTurno && energia >= carta.custo;
        const div = document.createElement('div');
        div.className = `carta-cmd ${pode ? '' : 'desabilitada'}`;
        div.innerHTML = `
            <div class="carta-cmd-title">${carta.nome.toUpperCase()}</div>
            <div class="carta-cmd-body">${carta.descricao.toUpperCase()}</div>
            <div class="carta-cmd-footer">COST: ${carta.custo}</div>
        `;
        if (pode) div.onclick = () => jogarCarta(index);
        containerMao.appendChild(div);
    });
}

function jogarCarta(index) {
    const carta = estadoAtual.jogadores[socket.id].mao[index];
    let alvo_sid = null;

    if (carta.tipo === 'atq' || carta.tipo === 'debuff') {
        const oponentes = Object.keys(estadoAtual.jogadores).filter(s => s !== socket.id);
        if (oponentes.length === 1) alvo_sid = oponentes[0];
        else if (!alvoSelecionadoSid) {
            alert("SELECT_TARGET_FIRST");
            return;
        } else alvo_sid = alvoSelecionadoSid;
    }

    socket.emit('jogar_carta', { indice_carta: index, alvo_sid: alvo_sid });
    alvoSelecionadoSid = null;
}

function passarTurno() { socket.emit('passar_turno'); }
function ativarBencao() { socket.emit('ativar_bencao'); }

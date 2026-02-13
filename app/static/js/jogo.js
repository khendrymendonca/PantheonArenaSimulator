const socket = io();
let meuPapel = ''; // 'jogador1' ou 'jogador2'
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
    document.querySelector('.bola-status').classList.add('on');
    console.log('Conectado ao Panteão de Elísia');
});

socket.on('disconnect', () => {
    document.querySelector('.bola-status').classList.remove('on');
    console.log('Conexão perdida com Elísia');
});

// --- LOBBY DINÂMICO ---
function atualizarPassivas() {
    const sel = document.getElementById('select-personagem');
    const secao = document.getElementById('secao-passiva');
    if (sel.value === 'apolo') {
        secao.style.display = 'block';
    } else {
        secao.style.display = 'none';
    }
}

// --- ENTRAR NO JOGO ---
function entrarNaArena() {
    const nome = document.getElementById('input-nome').value.trim();
    if (!nome) {
        alert('Identifique-se, Portador!');
        return;
    }

    const idPersonagem = document.getElementById('select-personagem').value;
    const passivaSelecionada = document.querySelector('input[name="passiva"]:checked').value;

    if (!idPersonagem) {
        alert('Selecione seu campeão!');
        return;
    }

    socket.emit('entrar_jogo', {
        nome: nome,
        personagem: idPersonagem,
        passiva: passivaSelecionada
    });

    overlayLogin.style.opacity = '0';
    setTimeout(() => {
        overlayLogin.style.display = 'none';
        tabuleiro.style.display = 'flex';
    }, 300);
}

// --- ATUALIZAÇÃO DO ESTADO ---
socket.on('estado_jogo', (estado) => {
    console.log('Estado recebido:', estado);
    estadoAtual = estado;
    atualizarTodaInterface(estado);
});

socket.on('erro', (msg) => {
    console.error('Erro:', msg);
    alert('Atenção: ' + msg);
});

// --- RENDERIZAÇÃO ---
function atualizarTodaInterface(estado) {
    if (!estado) return;

    const meuSid = socket.id;
    const eu = estado.jogadores[meuSid];

    // Gerenciar Telas
    if (estado.fase === 'espera') {
        overlayLogin.style.display = eu ? 'none' : 'flex';
        document.getElementById('sala-espera').style.display = eu ? 'flex' : 'none';
        tabuleiro.style.display = 'none';
        atualizarSalaEspera(estado);
    } else {
        overlayLogin.style.display = 'none';
        document.getElementById('sala-espera').style.display = 'none';
        tabuleiro.style.display = 'flex';

        // Outros jogadores são oponentes
        const oponentes = Object.entries(estado.jogadores).filter(([sid, p]) => sid !== meuSid);

        // Atualiza Meu Painel
        if (eu) {
            atualizarPainelPremium(eu, 'meu', estado.turno_sid === meuSid);

            // Botão de Efeito de Passiva (Apolo)
            if (eu.pes !== undefined) {
                btnAtivarBencao.style.display = 'block';
                btnAtivarBencao.disabled = (estado.turno_sid !== meuSid) || eu.pes < 3;
            } else {
                btnAtivarBencao.style.display = 'none';
            }
        }

        // Renderizar lista de Oponentes
        const containerOpp = document.getElementById('container-oponentes');
        containerOpp.innerHTML = '';

        oponentes.forEach(([sid, opp]) => {
            const div = renderizarPainelOponente(opp, sid, sid === estado.turno_sid);
            containerOpp.appendChild(div);
        });

        // Turno
        const meuTurno = estado.turno_sid === meuSid;
        btnPassarTurno.disabled = !meuTurno;

        if (estado.vencedor) {
            indicadorTurno.innerHTML = `<span style="color: gold; text-shadow: 0 0 10px gold">VENCEDOR: ${estado.vencedor}</span>`;
            btnPassarTurno.disabled = true;
        } else {
            indicadorTurno.innerText = meuTurno ? "SEU TURNO" : `AGUARDANDO...`;
        }

        // Logs
        atualizarLogs(estado.logs);

        // Mão
        renderizarMao(eu ? eu.mao : [], eu ? eu.energia : 0, meuTurno);
    }
}

function atualizarSalaEspera(estado) {
    const lista = document.getElementById('lista-jogadores');
    lista.innerHTML = Object.values(estado.jogadores).map(p => `
        <div class="vidro" style="padding: 10px; margin-bottom: 5px; display: flex; justify-content: space-between; border-left: 4px solid var(--ouro)">
            <span>${p.nome}</span>
            <span style="font-size: 0.7rem; color: var(--texto-mutado)">PRONTO</span>
        </div>
    `).join('');

    const btnIniciar = document.getElementById('btn-iniciar-jogo');
    const msgEspera = document.getElementById('msg-espera');

    if (estado.id_mestre === socket.id) {
        btnIniciar.style.display = 'block';
        msgEspera.innerText = "Você é o Mestre da Arena!";
    } else {
        btnIniciar.style.display = 'none';
        msgEspera.innerText = "Aguardando o mestre iniciar a batalha...";
    }
}

function atualizarPainelPremium(player, prefixo, ehTurno) {
    // Corrigir Nome
    const elNome = document.getElementById(`${prefixo}-nome`);
    if (elNome) elNome.innerText = player.nome;

    // HP e Energia em Círculos (Badges)
    const elHp = document.getElementById(`${prefixo}-hp`);
    if (elHp) elHp.innerText = player.vida;

    const elEnergia = document.getElementById(`${prefixo}-energia`);
    if (elEnergia) elEnergia.innerText = player.energia;

    const elPes = document.getElementById(`${prefixo}-pes`);
    if (elPes) elPes.innerText = player.pes || 0;

    // Atributos
    document.getElementById(`${prefixo}-atq`).innerText = player.atributos.atq;
    document.getElementById(`${prefixo}-def`).innerText = player.atributos.defesa;
    document.getElementById(`${prefixo}-dom`).innerText = player.atributos.dom;
    document.getElementById(`${prefixo}-res`).innerText = player.atributos.res;

    // Barra de Vida
    const porcentagem = Math.min(100, (player.vida / 30) * 100);
    const barra = document.getElementById(`${prefixo}-hp-barra`);
    if (barra) barra.style.width = `${porcentagem}%`;

    // Painel Ativo
    const painel = document.getElementById('painel-jogador');
    if (painel) {
        if (ehTurno) painel.classList.add('destaque-turno');
        else painel.classList.remove('destaque-turno');
    }
}

function renderizarPainelOponente(player, sid, ehTurnoDele) {
    const div = document.createElement('div');
    div.className = `area-jogador vidro ${ehTurnoDele ? 'destaque-turno' : ''}`;
    div.style.minWidth = '300px';
    div.id = `painel-opp-${sid}`;

    const porcentagem = Math.min(100, (player.vida / 30) * 100);

    div.innerHTML = `
        <div class="info-hero">
            <h3>${player.nome} ${ehTurnoDele ? '⚔️' : ''}</h3>
            <div class="atributos-mini">
                ATQ: ${player.atributos.atq} | DEF: ${player.atributos.defesa}
            </div>
        </div>
        <div class="stats-container">
            <div class="stat-item">
                <span class="stat-label">Vida</span>
                <span class="stat-valor">${player.vida}</span>
                <div class="barra-vida-bg">
                    <div class="barra-vida-fill" style="width: ${porcentagem}%"></div>
                </div>
            </div>
            <div class="stat-item">
                <span class="stat-label">Energia</span>
                <span class="stat-valor">${player.energia}</span>
            </div>
        </div>
        <div id="status-container-${sid}" class="status-icons"></div>
    `;

    // Botão de seleção de alvo (Se for meu turno)
    if (estadoAtual && estadoAtual.turno_sid === socket.id && player.vida > 0) {
        div.style.cursor = 'pointer';
        div.onclick = () => {
            // Remover destaque de outros
            document.querySelectorAll('#container-oponentes .area-jogador').forEach(el => el.classList.remove('alvo-selecionado'));
            div.classList.add('alvo-selecionado');
            alvoSelecionadoSid = sid;
        };
    }

    return div;
}

let alvoSelecionadoSid = null;

function atualizarPainel(player, prefixo) {
    document.getElementById(`${prefixo}-nome`).innerText = player.nome;
    document.getElementById(`${prefixo}-hp`).innerText = player.vida;
    document.getElementById(`${prefixo}-energia`).innerText = player.energia;

    // PES (Pontos de Energia Solar)
    const elPes = document.getElementById(`${prefixo}-pes`);
    if (elPes) elPes.innerText = player.pes || 0;

    // Atributos
    document.getElementById(`${prefixo}-atq`).innerText = player.atributos.atq;
    document.getElementById(`${prefixo}-def`).innerText = player.atributos.defesa;
    document.getElementById(`${prefixo}-dom`).innerText = player.atributos.dom;
    document.getElementById(`${prefixo}-res`).innerText = player.atributos.res;

    // Barra de Vida
    const porcentagem = Math.min(100, (player.vida / 30) * 100);
    document.getElementById(`${prefixo}-hp-barra`).style.width = `${porcentagem}%`;

    // Renderizar Status/Buffs (Novo)
    const containerStatus = document.getElementById(`${prefixo}-status-container`) || criarContainerStatus(prefixo);
    containerStatus.innerHTML = '';

    if (player.efeitos) {
        player.efeitos.forEach(efeito => {
            const el = document.createElement('div');
            el.className = 'icone-status';

            // Mapeamento de Ícones
            let icone = '❓';
            if (efeito.id === 'veneno') icone = '🩸';
            if (efeito.id === 'queimadura') icone = '🔥';
            if (efeito.id === 'immune_dot') icone = '🛡️';
            if (efeito.id === 'energia_proximo_turno') icone = '⚡';

            el.innerText = icone;
            el.title = `${efeito.id} (${efeito.turnos} turnos)`;
            containerStatus.appendChild(el);
        });
    }
}

function criarContainerStatus(prefixo) {
    const pai = document.getElementById(`${prefixo}-hp`).parentElement;
    const div = document.createElement('div');
    div.id = `${prefixo}-status-container`;
    div.className = 'status-icons';
    pai.appendChild(div);
    return div;
}

function atualizarLogs(logs) {
    logCorpo.innerHTML = logs.map((msg, i) => {
        const classe = i === logs.length - 1 ? 'log-msg destaque' : 'log-msg';
        return `<div class="${classe}">${msg}</div>`;
    }).join('');
    logCorpo.scrollTop = logCorpo.scrollHeight;
}

function renderizarMao(cartas, minhaEnergia, meuTurno) {
    containerMao.innerHTML = '';

    cartas.forEach((carta, index) => {
        const podeJogar = meuTurno && minhaEnergia >= carta.custo;
        const div = document.createElement('div');
        div.className = `carta vidro ${podeJogar ? '' : 'desabilitada'}`;

        // Ícone por tipo
        let icone = '⚔️';
        if (carta.tipo === 'dom') icone = '✨';
        if (carta.tipo === 'buff') icone = '🛡️';
        if (carta.tipo === 'debuff') icone = '💀';

        div.innerHTML = `
            <div class="carta-custo">${carta.custo}</div>
            <div class="carta-header">
                <div class="carta-nome">${carta.nome}</div>
                <div class="carta-tipo">${carta.tipo}</div>
            </div>
            <div class="carta-arte">${icone}</div>
            <div class="carta-corpo">
                ${carta.descricao}
            </div>
        `;

        if (podeJogar) {
            div.onclick = () => jogarCarta(index);
        }

        containerMao.appendChild(div);
    });
}

// --- AÇÕES ---
function jogarCarta(index) {
    const carta = estadoAtual.jogadores[socket.id].mao[index];

    // Se a carta precisar de alvo e houver múltiplos oponentes
    let alvo_sid = null;
    const oponentesIds = Object.keys(estadoAtual.jogadores).filter(s => s !== socket.id);

    if (carta.tipo === 'atq' || carta.tipo === 'debuff') {
        if (oponentesIds.length === 1) {
            alvo_sid = oponentesIds[0];
        } else {
            if (!alvoSelecionadoSid) {
                alert("Selecione um alvo clicando no painel do oponente!");
                return;
            }
            alvo_sid = alvoSelecionadoSid;
        }
    }

    socket.emit('jogar_carta', {
        indice_carta: index,
        alvo_sid: alvo_sid
    });

    alvoSelecionadoSid = null; // Reset
}

function passarTurno() {
    socket.emit('passar_turno', {});
}

function ativarBencao() {
    socket.emit('ativar_bencao', {});
}

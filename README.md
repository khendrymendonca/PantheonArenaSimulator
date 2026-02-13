# Pantheon Arena - Python Edition

Um jogo de batalha estratégico em turnos desenvolvido com Python (Flask), Socket.IO e Frontend moderno.

## 🚀 Como Rodar

### Pré-requisitos
- Python 3.8+
- Pip (gerenciador de pacotes)

### Passos
1. **Clone/Abra a pasta do projeto**:
   ```bash
   cd pantheon_arena
   ```

2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Inicie o Servidor**:
   ```bash
   python run.py
   ```

4. **Acesse o Jogo**:
   - Abra o navegador em: `http://127.0.0.1:5000`
   - Abra uma **segunda aba** (ou janela anônima) no mesmo endereço para simular o segundo jogador.

## ⚔️ Mecânicas de Jogo

### Atributos
Cada Gladiador possui:
- **HP (Vida)**: Começa com 30. Chegou a 0, perdeu.
- **Energia**: Reinicia a cada turno (10 base + 1d6 rolado).
- **ATQ (Ataque Físico)**: Soma ao dano de cartas físicas.
- **DEF (Defesa Física)**: Reduz dano físico recebido (junto com 1d4).
- **DOM (Domínio Mágico)**: Soma ao dano de cartas mágicas.
- **RES (Resistência Mágica)**: Reduz dano mágico recebido (junto com 1d4).

### Estrutura do Turno
1. **Fase de Energia**:
   - O jogo rola 1d6 automaticamente.
   - Sua energia total será `10 + Resultado do Dado`.

2. **Fase de Revelação (Compra)**:
   - Você compra 4 cartas do seu deck.
   - Elas aparecem na sua mão.

3. **Fase de Ação**:
   - Jogue quantas cartas quiser, desde que tenha Energia suficiente.
   - Tipos de Cartas:
     - **Físico**: Dano Base + ATQ vs (1d4 + DEF Inimiga).
     - **Mágico**: Dano Base + DOM vs (1d4 + RES Inimiga).
     - **Buff**: Cura ou melhoria de atributos (WIP).

4. **Fim do Turno**:
   - Ao clicar em "Encerrar Turno", todas as cartas da sua mão são descartadas.
   - A vez passa para o oponente.

## 🛠️ Tecnologias
- **Backend**: Python 3, Flask, Flask-SocketIO.
- **Frontend**: HTML5, CSS3 (Glassmorphism), JavaScript (Socket.IO Client).
- **Comunicação**: WebSocket em tempo real.

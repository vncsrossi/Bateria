import pygame
import time
import re

pygame.init()

token_map = {
    "K": ("B", "Bumbo"),
    "S": ("C", "Caixa"),
    "T1": ("T1", "Tom 1"),
    "T2": ("T2", "Tom 2"),
    "R": ("S", "Surdo"),
    "H": ("H", "Hi-hat fechado"),
    "O": ("A", "Hi-hat aberto"),
    "C": ("PA", "Prato de Ataque"),
    "D": ("PC", "Prato de Condução"),
}

def lexer(code):
    return [line.strip() for line in code.strip().splitlines() if line.strip()]

def parser(tokens):
    bpm = 120
    events = []
    beat_duration = 60 / bpm

    for line in tokens:
        tempo_match = re.match(r"\[tempo=(\d+)\]", line, re.IGNORECASE)
        if tempo_match:
            bpm = int(tempo_match.group(1))
            if bpm > 200:
                raise ValueError("BPM não pode ser maior que 200.")
            beat_duration = 60 / bpm
            continue

        beat_groups = re.split(r'\s*\|\s*', line)
        current_time = 0.0
        for group in beat_groups:
            simult_tokens = [t.strip().upper() for t in group.split() if t.strip() and t != "-"]
            if len(simult_tokens) > 3:
                raise ValueError(f"Mais de 3 sons simultâneos no tempo {current_time:.2f}s")
            if len(simult_tokens) > 2 and "K" not in simult_tokens:
                raise ValueError(f"Até 2 sons simultâneos sem bumbo (K) no tempo {current_time:.2f}s")

            for token in simult_tokens:
                if token not in token_map:
                    raise ValueError(f"Token inválido: {token}")
                events.append((current_time, token))
            current_time += beat_duration

    return events, bpm

def gerar_partitura_texto(events, bpm):
    instrumentos = {
        "K": "Bumbo",
        "S": "Caixa",
        "T1": "Tom 1",
        "T2": "Tom 2",
        "R": "Surdo",
        "H": "Hi-hat fechado",
        "O": "Hi-hat aberto",
        "C": "Prato de Ataque",
        "D": "Prato de Condução"
    }

    tempos = sorted(set([round(t, 2) for t, _ in events]))
    eventos_por_tempo = {round(t, 2): [] for t in tempos}
    
    for tempo, token in events:
        tempo_rounded = round(tempo, 2)
        eventos_por_tempo[tempo_rounded].append(token)

    linhas = []
    header = "Tempo:   |" + "|".join(f"{t:>7.2f}s" for t in tempos) + "|"
    linhas.append(header)
    linhas.append("-" * len(header))

    for token, nome in instrumentos.items():
        linha_instr = f"{nome:<15}|"
        for t in tempos:
            linha_instr += f"{token if token in eventos_por_tempo[t] else '':^9}|"
        linhas.append(linha_instr)

    return linhas

# Configuração da janela e fontes
WIDTH, HEIGHT = 800, 550
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visualizador de Bateria")
font = pygame.font.SysFont(None, 24)
label_font = pygame.font.SysFont(None, 22)
bpm_font = pygame.font.SysFont(None, 26)
partitura_font = pygame.font.SysFont('Courier New', 20)

colors = {
    "K": (100, 255, 100),
    "S": (255, 255, 255),
    "T1": (100, 200, 255),
    "T2": (100, 200, 255),
    "R": (100, 200, 255),
    "H": (255, 255, 100),
    "O": (255, 200, 100),
    "C": (255, 100, 100),
    "D": (255, 150, 50),
}

pos_map = {
    "K":  (400, 390),
    "S":  (340, 270),
    "R":  (460, 270),
    "T1": (355, 180),
    "T2": (445, 180),
    "H":  (265, 295),
    "O":  (265, 240),
    "C":  (190, 150),
    "D":  (610, 150),
}

def draw_interface(active_tokens=None, bpm_value=120):
    if active_tokens is None:
        active_tokens = []

    screen.fill((15, 15, 15))
    for token, (x, y) in pos_map.items():
        letra, nome = token_map[token]
        ativo = token in active_tokens
        cor = (255, 50, 50) if ativo else colors.get(token, (200, 200, 200))
        raio = 65 if token == "K" else 45
        pygame.draw.circle(screen, cor, (x, y), raio)

        letra_render = font.render(letra, True, (0, 0, 0))
        nome_render = label_font.render(nome, True, (200, 200, 200))
        screen.blit(letra_render, (x - letra_render.get_width() // 2, y - letra_render.get_height() // 2))
        screen.blit(nome_render, (x - nome_render.get_width() // 2, y + raio + 5))

    bpm_label = bpm_font.render(f"BPM: {bpm_value}", True, (255, 255, 255))
    screen.blit(bpm_label, (10, 10))
    pygame.display.flip()

def desenhar_partitura(linhas):
    screen.fill((10, 10, 10))
    y = 20
    for linha in linhas:
        texto = partitura_font.render(linha, True, (200, 200, 200))
        screen.blit(texto, (20, y))
        y += 25
    pygame.display.flip()

# Código de entrada
codigo = """
[tempo=100]
- - - -|T1 T2 K| C D | H K R| K| H T1| S O| S O|
"""

tokens = lexer(codigo)
events, tempo = parser(tokens)
partitura_linhas = gerar_partitura_texto(events, tempo)
duracao_total = max(t for t, _ in events) + 0.3  # tempo total da sequência

# Loop principal
running = True
clock = pygame.time.Clock()
start_ticks = pygame.time.get_ticks()
modo_partitura = False  # false = modo gráfico

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            modo_partitura = not modo_partitura

    if modo_partitura:
        desenhar_partitura(partitura_linhas)
    else:
        now = (pygame.time.get_ticks() - start_ticks) / 1000.0

        # ✅ Toca só uma vez e para depois
        if now > duracao_total:
            current_tokens = []
        else:
            current_tokens = [token for t, token in events if 0 <= now - t < 0.3]

        draw_interface(current_tokens, tempo)

    clock.tick(60)

pygame.quit()

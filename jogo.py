import pygame
import sys
import os
import random

# Inicialização
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Jogo de Espada")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)

# Caminhos
caminho_base = os.path.dirname(__file__)
caminho_fundo = os.path.join(caminho_base, "assets", "fundos", "fundo_floresta.png")
caminho_personagem = os.path.join(caminho_base, "assets", "personagem")
caminho_inimigo = os.path.join(caminho_base, "assets", "inimigo")
caminho_faca = os.path.join(caminho_base, "assets", "faca", "faca.png")

# Função para carregar frames
def carregar_frames(pasta, prefixo, quantidade, usar_zeros=False, tamanho=None, iniciar_em=1):
    frames = []
    for i in range(iniciar_em, iniciar_em + quantidade):
        nome = f"{prefixo}{str(i).zfill(3) if usar_zeros else i}.png"
        caminho = os.path.join(pasta, nome)
        try:
            img = pygame.image.load(caminho).convert_alpha()
            if tamanho:
                img = pygame.transform.smoothscale(img, tamanho)
            frames.append(img)
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {caminho}")
    return frames

# Carregando fundos e assets
try:
    fundo_original = pygame.image.load(caminho_fundo).convert()
    fundo = pygame.transform.scale(fundo_original, (800, 600))
except:
    print("Erro ao carregar fundo. Verifique o caminho.")
    fundo = pygame.Surface((800, 600))
    fundo.fill((0, 0, 0))

try:
    imagem_faca = pygame.image.load(caminho_faca).convert_alpha()
    imagem_faca = pygame.transform.scale(imagem_faca, (40, 10))
except:
    print("Erro ao carregar imagem da faca.")
    imagem_faca = pygame.Surface((40, 10))
    imagem_faca.fill((255, 255, 0))

# Animações personagem
andar_frames = carregar_frames(caminho_personagem, "andar", 8, iniciar_em=1)
correr_frames = carregar_frames(caminho_personagem, "correr", 8, iniciar_em=1)
ataque_frames = carregar_frames(caminho_personagem, "ataque", 7, iniciar_em=1)
morte_frames = carregar_frames(caminho_personagem, "morte", 3, iniciar_em=1)
pulo_frames = carregar_frames(caminho_personagem, "pulo", 6, iniciar_em=1)

# Animações inseto
tamanho_inseto = (50, 50)
voar_inseto_frames = carregar_frames(caminho_inimigo, "0_Monster_Fly_", 18, usar_zeros=True, tamanho=tamanho_inseto, iniciar_em=0)
ataque_inseto_frames = carregar_frames(caminho_inimigo, "0_Monster_Attack_", 17, usar_zeros=True, tamanho=tamanho_inseto, iniciar_em=0)
morte_inseto_frames = carregar_frames(caminho_inimigo, "0_Monster_Dying_", 17, usar_zeros=True, tamanho=tamanho_inseto, iniciar_em=0)
queda_inseto_frames = carregar_frames(caminho_inimigo, "0_Monster_Fall_", 17, usar_zeros=True, tamanho=tamanho_inseto, iniciar_em=0)

ALTURA_CHAO = 450

class InsetoVoador:
    def __init__(self, x):
        self.rect = pygame.Rect(x, random.randint(300, 450), 50, 50)
        self.velocidade = 2
        self.atacando = False
        self.morrendo = False
        self.caindo = False
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_interval = 4

    def mover(self, alvo_rect):
        if self.morrendo or self.caindo: return
        if not self.atacando and random.random() < 0.01:
            self.atacando = True
            self.velocidade = 6
        dx = alvo_rect.x - self.rect.x
        direcao = dx / max(1, abs(dx))
        self.rect.x += int(self.velocidade * direcao)
        self.rect.y += random.randint(-2, 2)
        self.rect.y = max(300, min(self.rect.y, 450))
        if self.atacando and abs(self.rect.x - alvo_rect.x) < 10:
            self.atacando = False
            self.velocidade = 2

    def atualizar_animacao(self):
        self.frame_timer += 1
        if self.frame_timer >= self.frame_interval:
            self.frame_timer = 0
            self.frame_index += 1
            if self.caindo:
                if self.frame_index >= len(queda_inseto_frames): return "remover"
            elif self.morrendo:
                if self.frame_index >= len(morte_inseto_frames):
                    self.caindo = True
                    self.frame_index = 0
            elif self.atacando:
                self.frame_index %= len(ataque_inseto_frames)
            else:
                self.frame_index %= len(voar_inseto_frames)

    def desenhar(self, tela):
        if self.caindo:
            idx = min(self.frame_index, len(queda_inseto_frames)-1)
            tela.blit(queda_inseto_frames[idx], self.rect.topleft)
        elif self.morrendo:
            idx = min(self.frame_index, len(morte_inseto_frames)-1)
            tela.blit(morte_inseto_frames[idx], self.rect.topleft)
        elif self.atacando:
            idx = self.frame_index % len(ataque_inseto_frames)
            tela.blit(ataque_inseto_frames[idx], self.rect.topleft)
        else:
            idx = self.frame_index % len(voar_inseto_frames)
            tela.blit(voar_inseto_frames[idx], self.rect.topleft)

    def morrer(self):
        self.morrendo = True
        self.frame_index = 0
        self.frame_timer = 0
        self.velocidade = 0

class Faca:
    def __init__(self, x, y, alvo_x, alvo_y):
        self.rect = pygame.Rect(x, y + 25, 40, 10)
        self.speed = 15
        self.viva = True
        # Calcula vetor direção normalizado para o alvo
        dx = alvo_x - x
        dy = alvo_y - y
        dist = max((dx ** 2 + dy ** 2) ** 0.5, 1)
        self.vel_x = (dx / dist) * self.speed
        self.vel_y = (dy / dist) * self.speed

    def mover(self):
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)
        # Remove se sair da tela
        if (self.rect.right < 0 or self.rect.left > 800 or
            self.rect.bottom < 0 or self.rect.top > 600):
            self.viva = False

    def desenhar(self, tela):
        # Rotacionar faca na direção do movimento
        angle = -pygame.math.Vector2(self.vel_x, self.vel_y).angle_to((1, 0))
        faca_rotacionada = pygame.transform.rotate(imagem_faca, angle)
        tela.blit(faca_rotacionada, self.rect.topleft)

# Variáveis globais
player = pygame.Rect(100, ALTURA_CHAO, 50, 50)
vidas, morrendo = 3, False
morte_index, morte_timer, atacando = 0, 0, False
ataque_index, ataque_timer = 0, 0
frame_index, frame_timer = 0, 0
insetos = [InsetoVoador(random.randint(800, 1200)) for _ in range(5)]
facas = []
direcao = "direita"  # Guarda a direção atual do personagem

# Parâmetros do jogo
vel_normal, vel_correndo = 5, 10
frame_interval = 5
ataque_intervalo = 5
morte_intervalo = 10

def reiniciar_jogo():
    global player, vidas, morrendo, morte_index, morte_timer, atacando, ataque_index, ataque_timer
    global frame_index, frame_timer, insetos, facas, direcao
    player = pygame.Rect(100, ALTURA_CHAO, 50, 50)
    vidas = 3
    morrendo = False
    morte_index = morte_timer = ataque_index = ataque_timer = 0
    atacando = False
    frame_index = frame_timer = 0
    insetos = [InsetoVoador(random.randint(800, 1200)) for _ in range(5)]
    facas = []
    direcao = "direita"

def morrer():
    global morrendo, morte_index, morte_timer, atacando
    morrendo = True
    morte_index = morte_timer = 0
    atacando = False

reiniciar_jogo()

# Funções de desenho de tela
def desenhar_menu():
    screen.fill((0, 0, 0))
    texto = font.render("New Game - Pressione ENTER", True, (255, 255, 255))
    screen.blit(texto, (250, 280))

def desenhar_restart():
    screen.fill((0, 0, 0))
    texto = font.render("Você morreu! Pressione R para reiniciar", True, (255, 0, 0))
    screen.blit(texto, (200, 280))

# Loop principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse click: esquerdo = ataque, direito = lança faca
        if event.type == pygame.MOUSEBUTTONDOWN and not morrendo:
            if event.button == 1:  # Botão esquerdo: ataque espada
                if not atacando:
                    atacando = True
                    ataque_index = 0
                    ataque_timer = 0
            elif event.button == 3:  # Botão direito: lança faca para o clique
                if len(facas) < 5:
                    mx, my = pygame.mouse.get_pos()
                    # lança faca da frente do player (ajuste para frente dependendo da direção)
                    if direcao == "direita":
                        facas.append(Faca(player.right, player.y, mx, my))
                    else:
                        facas.append(Faca(player.left, player.y, mx, my))

    keys = pygame.key.get_pressed()

    # Movimentação A (para trás/esquerda) e D (para frente/direita)
    velocidade = vel_correndo if keys[pygame.K_LSHIFT] else vel_normal
    movendo = False
    if not morrendo and not atacando:
        if keys[pygame.K_a]:
            player.x -= velocidade
            direcao = "esquerda"
            movendo = True
        if keys[pygame.K_d]:
            player.x += velocidade
            direcao = "direita"
            movendo = True

    # Limite do chão e tela
    player.y = ALTURA_CHAO
    if player.x < 0:
        player.x = 0
    elif player.x > 750:
        player.x = 750

    if not morrendo:
        # Atualiza facas
        for faca in facas[:]:
            faca.mover()
            for inseto in insetos:
                if faca.viva and not inseto.morrendo and not inseto.caindo and faca.rect.colliderect(inseto.rect):
                    inseto.morrer()
                    faca.viva = False
            if not faca.viva:
                facas.remove(faca)

        # Atualiza insetos
        insetos_ativos = []
        for inseto in insetos:
            res = inseto.atualizar_animacao()
            if res != "remover":
                inseto.mover(player)
                if hasattr(inseto, "ataque_timer"):
                    inseto.ataque_timer += 1
                else:
                    inseto.ataque_timer = 0
                if inseto.ataque_timer >= 20:
                    if player.colliderect(inseto.rect) and not morrendo and not inseto.morrendo and not inseto.caindo:
                        vidas -= 1
                        inseto.ataque_timer = 0
                        if vidas <= 0:
                            morrer()
                insetos_ativos.append(inseto)
        insetos = insetos_ativos

    # Tela fundo
    screen.blit(fundo, (0, 0))

    # Ataque corpo a corpo
    if atacando:
        ataque_timer += 1
        if ataque_timer >= ataque_intervalo:
            ataque_index += 1
            ataque_timer = 0
            # Área de ataque (frente ou trás)
            if direcao == "direita":
                ataque_area = pygame.Rect(player.right, player.y, 40, 50)
            else:
                ataque_area = pygame.Rect(player.left - 40, player.y, 40, 50)
            for inseto in insetos:
                if not inseto.morrendo and not inseto.caindo and ataque_area.colliderect(inseto.rect):
                    inseto.morrer()
            if ataque_index >= len(ataque_frames):
                atacando = False
                ataque_index = 0
        # Renderizar ataque com flip dependendo da direção
        frame_ataque = ataque_frames[ataque_index]
        if direcao == "esquerda":
            frame_ataque = pygame.transform.flip(frame_ataque, True, False)
        screen.blit(frame_ataque, (player.x, player.y))
    else:
        # Animação de movimento ou parado
        if movendo:
            frame_timer += 1
            if frame_timer >= frame_interval:
                frame_index = (frame_index + 1) % len(andar_frames)
                frame_timer = 0
        else:
            frame_index = 0

        frame_andar = andar_frames[frame_index]
        if direcao == "esquerda":
            frame_andar = pygame.transform.flip(frame_andar, True, False)
        screen.blit(frame_andar, (player.x, player.y))

    # Desenhar facas
    for faca in facas:
        faca.desenhar(screen)

    # Desenhar insetos
    for inseto in insetos:
        inseto.desenhar(screen)

    # HUD vidas
    texto = font.render(f"Vidas: {vidas}", True, (255, 255, 255))
    screen.blit(texto, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

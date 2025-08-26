import pygame
import sys
import os
import random

estado_jogo = "menu"  # Pode ser "menu", "jogando", "morto"

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

def desenhar_menu():
    screen.fill((0, 0, 0))
    texto = font.render("New Game - Pressione ENTER", True, (255, 255, 255))
    screen.blit(texto, (250, 280))

def desenhar_restart():
    screen.fill((0, 0, 0))
    texto = font.render("Você morreu! Pressione R para reiniciar", True, (255, 0, 0))
    screen.blit(texto, (200, 280))

# Carregar fundo
try:
    fundo_original = pygame.image.load(caminho_fundo).convert()
    fundo = pygame.transform.scale(fundo_original, (800, 600))
except pygame.error:
    print("Erro ao carregar fundo. Verifique o caminho.")
    fundo = pygame.Surface((800, 600))
    fundo.fill((0, 0, 0))

def reiniciar_jogo():
    global estado_jogo
    estado_jogo = "jogando"
    # Aqui você pode resetar vidas, jogador, inimigos etc.

# Função para carregar frames
def carregar_frames(pasta, prefixo, quantidade, usar_zeros=False, tamanho=None, iniciar_em=1):
    frames = []
    for i in range(iniciar_em, iniciar_em + quantidade):
        nome_arquivo = f"{prefixo}{str(i).zfill(3) if usar_zeros else i}.png"
        caminho = os.path.join(pasta, nome_arquivo)
        try:
            imagem = pygame.image.load(caminho).convert_alpha()
            if tamanho:
                imagem = pygame.transform.smoothscale(imagem, tamanho)
            frames.append(imagem)
        except FileNotFoundError:
            print(f"⚠️ Arquivo não encontrado: {caminho}")
    return frames

# Carregar animações do personagem (iniciando em 1)
andar_frames = carregar_frames(caminho_personagem, "andar", 8, iniciar_em=1)
correr_frames = carregar_frames(caminho_personagem, "correr", 8, iniciar_em=1)
ataque_frames = carregar_frames(caminho_personagem, "ataque", 7, iniciar_em=1)
morte_frames = carregar_frames(caminho_personagem, "morte", 3, iniciar_em=1)
pulo_frames = carregar_frames(caminho_personagem, "pulo", 6, iniciar_em=1)

# Carregar animações dos insetos
tamanho_inseto = (50, 50)
voar_inseto_frames   = carregar_frames(caminho_inimigo, "0_Monster_Fly_",   18, usar_zeros=True, tamanho=tamanho_inseto, iniciar_em=0)
ataque_inseto_frames = carregar_frames(caminho_inimigo, "0_Monster_Attack_", 17, usar_zeros=True, tamanho=tamanho_inseto, iniciar_em=0)
morte_inseto_frames  = carregar_frames(caminho_inimigo, "0_Monster_Dying_",  17, usar_zeros=True, tamanho=tamanho_inseto, iniciar_em=0)
queda_inseto_frames  = carregar_frames(caminho_inimigo, "0_Monster_Fall_",   17, usar_zeros=True, tamanho=tamanho_inseto, iniciar_em=0)

# Altura do chão
ALTURA_CHAO = 450

# Classe de inseto voador
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
        if self.morrendo or self.caindo:
            return
        if not self.atacando and random.random() < 0.01:
            self.atacando = True
            self.velocidade = 6
        dx = alvo_rect.x - self.rect.x
        distancia = max(1, abs(dx))
        direcao = dx / distancia
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
                if self.frame_index >= len(queda_inseto_frames):
                    return "remover"
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
            if self.frame_index < len(queda_inseto_frames):
                tela.blit(queda_inseto_frames[self.frame_index], self.rect.topleft)
        elif self.morrendo:
            if self.frame_index < len(morte_inseto_frames):
                tela.blit(morte_inseto_frames[self.frame_index], self.rect.topleft)
        elif self.atacando:
            tela.blit(ataque_inseto_frames[self.frame_index], self.rect.topleft)
        else:
            tela.blit(voar_inseto_frames[self.frame_index], self.rect.topleft)

    def morrer(self):
        self.morrendo = True
        self.frame_index = 0
        self.frame_timer = 0
        self.velocidade = 0

# Personagem
player = pygame.Rect(100, ALTURA_CHAO, 50, 50)
velocidade_normal = 5
velocidade_correndo = 10

# Controle de animação
frame_index = 0
frame_timer = 0
frame_interval = 5

# Ataque
atacando = False
ataque_index = 0
ataque_timer = 0
ataque_intervalo = 5

# Morte do personagem
morrendo = False
morte_index = 0
morte_timer = 0
morte_intervalo = 10

# Pulo
pulando = False
velocidade_pulo = -15
gravidade = 1
velocidade_vertical = 0
pulo_index = 0
pulo_timer = 0
pulo_intervalo = 5


# Lista de insetos
insetos = [InsetoVoador(random.randint(800, 1200)) for _ in range(5)]

# HUD
vidas = 3
font = pygame.font.SysFont(None, 36)

# Função de morte
def morrer():
    global morrendo, morte_index, morte_timer, atacando
    morrendo = True
    morte_index = 0
    morte_timer = 0
    atacando = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if estado_jogo == "menu":
        if keys[pygame.K_RETURN]:
            estado_jogo = "jogando"
            vidas = 3
            morrendo = False
            morte_index = 0
            ataque_index = 0
            ataque_timer = 0
            insetos = [InsetoVoador(random.randint(800, 1200)) for _ in range(5)]
            player.x = 100
            player.y = ALTURA_CHAO
        desenhar_menu()

    elif estado_jogo == "morto":
        desenhar_restart()
        if keys[pygame.K_r]:
            estado_jogo = "menu"

    elif estado_jogo == "jogando":
        # Atualizar insetos
        import random

        insetos_ativos = []
        for inseto in insetos:
            resultado = inseto.atualizar_animacao()
            if resultado != "remover":
                # Movimento normal
                inseto.mover(player)

                # Esquiva rápida aleatória
                if random.randint(0, 100) < 10:  # 10% de chance por frame
                    direcao = random.choice([-1, 1])
                    inseto.rect.x += direcao * 15  # esquiva rápida

                # Ataque mais rápido
                if hasattr(inseto, "ataque_timer"):
                    inseto.ataque_timer += 1
                else:
                    inseto.ataque_timer = 0

                if inseto.ataque_timer >= 20:  # ataque a cada 20 frames
                    if player.colliderect(inseto.rect) and not morrendo and not inseto.morrendo and not inseto.caindo:
                        vidas -= 1
                        inseto.ataque_timer = 0  # reinicia o tempo de ataque
                        if vidas <= 0:
                            morrer()
                insetos_ativos.append(inseto)
        insetos = insetos_ativos

        # Desenhar fundo
        screen.blit(fundo, (0, 0))

        # Morte do personagem
        if morrendo:
            morte_timer += 1
            if morte_timer >= morte_intervalo:
                if morte_index < len(morte_frames) - 1:
                    morte_index += 1
                    morte_timer = 0
            screen.blit(morte_frames[morte_index], (player.x, player.y))
        else:
            velocidade = velocidade_correndo if keys[pygame.K_LSHIFT] else velocidade_normal
            if atacando:
                velocidade //= 2
            movendo = False
            if keys[pygame.K_LEFT]:
                player.x -= velocidade
                movendo = True
            if keys[pygame.K_RIGHT]:
                player.x += velocidade
                movendo = True
            player.y = ALTURA_CHAO
            if keys[pygame.K_a] and not atacando:
                atacando = True
                ataque_index = 0
                ataque_timer = 0
            if atacando:
                ataque_timer += 1
                if ataque_timer >= ataque_intervalo:
                    ataque_index += 1
                    ataque_timer = 0
                    if ataque_index >= len(ataque_frames):
                        ataque_index = 0
                        atacando = False
                screen.blit(ataque_frames[ataque_index], (player.x, player.y))
            else:
                frames_atuais = correr_frames if velocidade == velocidade_correndo else andar_frames
                if movendo:
                    frame_timer += 1
                    if frame_timer >= frame_interval:
                        frame_index = (frame_index + 1) % len(frames_atuais)
                        frame_timer = 0
                    screen.blit(frames_atuais[frame_index], (player.x, player.y))
                else:
                    screen.blit(frames_atuais[0], (player.x, player.y))

        # Desenhar insetos
        for inseto in insetos:
            inseto.desenhar(screen)

        # HUD
        texto = font.render(f"Vidas: {vidas}", True, (255, 255, 255))
        screen.blit(texto, (10, 10))

    # Atualizar tela
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

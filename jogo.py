import pygame
import sys
import os

# Inicialização
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Jogo de Espada")
clock = pygame.time.Clock()

# Personagem
player = pygame.Rect(100, 100, 50, 50)
velocidade_normal = 5
velocidade_correndo = 10

# Caminho das imagens
caminho_personagem = os.path.join("assets", "personagem")

# Carregar frames de andar
andar_frames = [pygame.image.load(os.path.join(caminho_personagem, f"andar{i}.png")) for i in range(1, 9)]

# Carregar frames de correr
correr_frames = [pygame.image.load(os.path.join(caminho_personagem, f"correr{i}.png")) for i in range(1, 9)]

# Carregar frames de ataque
ataque_frames = [pygame.image.load(os.path.join(caminho_personagem, f"ataque{i}.png")) for i in range(1, 7)]

# Controle de animação de movimento
frame_index = 0
frame_timer = 0
frame_interval = 5

# Controle de ataque
atacando = False
ataque_index = 0
ataque_timer = 0
ataque_intervalo = 5

# Inimigo
inimigo = pygame.Rect(400, 300, 50, 50)

# HUD
vidas = 3
font = pygame.font.SysFont(None, 36)

# Loop principal
running = True
while running:
    screen.fill((0, 0, 0))  # fundo preto

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if atacando:
        velocidade = velocidade_normal // 2  # reduz a velocidade pela metade durante o ataque
    else:
        velocidade = velocidade_correndo if keys[pygame.K_LSHIFT] else velocidade_normal

    movendo = False
    if keys[pygame.K_LEFT]:
        player.x -= velocidade
        movendo = True
    if keys[pygame.K_RIGHT]:
        player.x += velocidade
        movendo = True
    if keys[pygame.K_UP]:
        player.y -= velocidade
        movendo = True
    if keys[pygame.K_DOWN]:
        player.y += velocidade
        movendo = True

    # Iniciar ataque ao pressionar A
    if keys[pygame.K_a] and not atacando:
        atacando = True
        ataque_index = 0
        ataque_timer = 0

    # Executar animação de ataque
    # Executar animação de ataque enquanto anda
    if atacando:
        ataque_timer += 1
        if ataque_timer >= ataque_intervalo:
            ataque_index += 1
            ataque_timer = 0
            if ataque_index >= len(ataque_frames):
                ataque_index = 0
                atacando = False

        # Continua se movendo e desenha ataque
        player.x += (-velocidade if keys[pygame.K_LEFT] else velocidade if keys[pygame.K_RIGHT] else 0)
        player.y += (-velocidade if keys[pygame.K_UP] else velocidade if keys[pygame.K_DOWN] else 0)

        screen.blit(ataque_frames[ataque_index], (player.x, player.y))

    else:
        # Escolher frames de acordo com velocidade
        frames_atuais = correr_frames if velocidade == velocidade_correndo else andar_frames

        if movendo:
            frame_timer += 1
            if frame_timer >= frame_interval:
                frame_index = (frame_index + 1) % len(frames_atuais)
                frame_timer = 0
            screen.blit(frames_atuais[frame_index], (player.x, player.y))
        else:
            screen.blit(frames_atuais[0], (player.x, player.y))

    # Desenhar inimigo
    pygame.draw.rect(screen, (255, 0, 0), inimigo)

    # HUD
    texto = font.render(f"Vidas: {vidas}", True, (255, 255, 255))
    screen.blit(texto, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

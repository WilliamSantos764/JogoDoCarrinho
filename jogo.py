import pygame
import sys
import os
import random

estado_jogo = "menu"  # "menu", "jogando", "morto"

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


def desenhar_menu():
    screen.fill((0, 0, 0))
    texto = font.render("New Game - Pressione ENTER", True, (255, 255, 255))
    screen.blit(texto, (250, 280))


def desenhar_restart():
    screen.fill((0, 0, 0))
    texto = font.render("Você morreu! Pressione R para reiniciar", True, (255, 0, 0))
    screen.blit(texto, (200, 280))


# Fundo
try:
    fundo_original = pygame.image.load(caminho_fundo).convert()
    fundo = pygame.transform.scale(fundo_original, (800, 600))
except:
    print("Erro ao carregar fundo. Verifique o caminho.")
    fundo = pygame.Surface((800, 600))
    fundo.fill((0, 0, 0))

# Faca
try:
    imagem_faca = pygame.image.load(caminho_faca).convert_alpha()
    imagem_faca = pygame.transform.scale(imagem_faca, (40, 10))
except:
    print("Erro ao carregar imagem da faca.")
    imagem_faca = pygame.Surface((40, 10))
    imagem_faca.fill((255, 255, 0))


# Função para carregar frames
def carregar_frames(pasta, prefixo, quantidade, usar_zeros=False, tamanho=None, iniciar_em=1):
    frames = []
    for i in range(iniciar_em, iniciar_em + quantidade):
        nome = f"{prefixo}{str(i).zfill(3) if usar_zeros else i}.png"
        caminho = os.path.join(pasta, nome)
        try:
            img = pygame.image.load(caminho).convert_alpha()
            if tamanho: img = pygame.transform.smoothscale(img, tamanho)
            frames.append(img)
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {caminho}")
    return frames


# Animações do personagem
andar_frames = carregar_frames(caminho_personagem, "andar", 8, iniciar_em=1)
correr_frames = carregar_frames(caminho_personagem, "correr", 8, iniciar_em=1)
ataque_frames = carregar_frames(caminho_personagem, "ataque", 7, iniciar_em=1)
morte_frames = carregar_frames(caminho_personagem, "morte", 3, iniciar_em=1)
pulo_frames = carregar_frames(caminho_personagem, "pulo", 6, iniciar_em=1)

tamanho_inseto = (50, 50)
voar_inseto_frames = carregar_frames(caminho_inimigo, "0_Monster_Fly_", 18, usar_zeros=True, tamanho=tamanho_inseto,
                                     iniciar_em=0)
ataque_inseto_frames = carregar_frames(caminho_inimigo, "0_Monster_Attack_", 17, usar_zeros=True,
                                       tamanho=tamanho_inseto, iniciar_em=0)
morte_inseto_frames = carregar_frames(caminho_inimigo, "0_Monster_Dying_", 17, usar_zeros=True, tamanho=tamanho_inseto,
                                      iniciar_em=0)
queda_inseto_frames = carregar_frames(caminho_inimigo, "0_Monster_Fall_", 17, usar_zeros=True, tamanho=tamanho_inseto,
                                      iniciar_em=0)

ALTURA_CHAO = 450


class InsetoVoador:
    def __init__(self, x, vida=1, chefe=False):
        self.rect = pygame.Rect(x, random.randint(300, 450), 50, 50)
        self.velocidade = 2
        self.atacando = False
        self.morrendo = False
        self.caindo = False
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_interval = 4
        self.vida = vida
        self.chefe = chefe
        if self.chefe:
            self.rect.inflate_ip(50, 50)  # aumenta o tamanho do chefe

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
            idx = min(self.frame_index, len(queda_inseto_frames) - 1)
            tela.blit(queda_inseto_frames[idx], self.rect.topleft)
        elif self.morrendo:
            idx = min(self.frame_index, len(morte_inseto_frames) - 1)
            tela.blit(morte_inseto_frames[idx], self.rect.topleft)
        elif self.atacando:
            idx = self.frame_index % len(ataque_inseto_frames)
            tela.blit(ataque_inseto_frames[idx], self.rect.topleft)
        else:
            idx = self.frame_index % len(voar_inseto_frames)
            tela.blit(voar_inseto_frames[idx], self.rect.topleft)

    def sofrer_dano(self):
        if self.chefe:
            self.vida -= 0.5  # chefe perde menos vida
        else:
            self.vida -= 1
        if self.vida <= 0 and not self.morrendo:
            self.morrer()

    def morrer(self):
        self.morrendo = True
        self.frame_index = 0
        self.frame_timer = 0
        self.velocidade = 0


class Faca:
    def __init__(self, x, y, direcao=1, alvo=None):
        self.rect = pygame.Rect(x, y + 25, 40, 10)
        self.velocidade = 15 * direcao
        self.viva = True
        self.alvo = alvo
        if alvo:
            # Direção vetor normalizado para o alvo
            dx = alvo[0] - x
            dy = alvo[1] - y
            dist = max((dx ** 2 + dy ** 2) ** 0.5, 0.01)
            self.vel_x = (dx / dist) * 15
            self.vel_y = (dy / dist) * 15
        else:
            self.vel_x = self.velocidade
            self.vel_y = 0

    def mover(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        if (self.rect.right < 0 or self.rect.left > 800 or
                self.rect.bottom < 0 or self.rect.top > 600):
            self.viva = False

    def desenhar(self, tela):
        tela.blit(imagem_faca, self.rect.topleft)


# Variáveis globais
player = pygame.Rect(100, ALTURA_CHAO, 50, 50)
vidas, morrendo = 3, False
morte_index, morte_timer, atacando = 0, 0, False
ataque_index, ataque_timer = 0, 0
direcao_ataque = "frente"
frame_index, frame_timer = 0, 0
insetos = []
facas = []

# Parâmetros do jogo
vel_normal, vel_correndo = 5, 10
frame_interval = 5
ataque_intervalo = 5
morte_intervalo = 10
pulo_intervalo = 5
pulando, velocidade_pulo, gravidade, vel_vertical = False, -15, 1, 0
pulo_index, pulo_timer = 0, 0
max_insetos = 25
insetos_mortos = 0

direcao_personagem = 1  # 1 = direita, -1 = esquerda


def reiniciar_jogo():
    global player, vidas, morrendo, morte_index, morte_timer, atacando, ataque_index, ataque_timer
    global frame_index, frame_timer, insetos, facas, estado_jogo, insetos_mortos, direcao_personagem
    player = pygame.Rect(100, ALTURA_CHAO, 50, 50)
    vidas = 3
    morrendo = False
    morte_index = morte_timer = ataque_index = ataque_timer = 0
    atacando = False
    frame_index = frame_timer = 0
    insetos.clear()
    facas.clear()
    insetos_mortos = 0
    estado_jogo = "menu"
    direcao_personagem = 1


reiniciar_jogo()


def morrer():
    global morrendo, morte_index, morte_timer, atacando, estado_jogo
    morrendo = True
    morte_index = morte_timer = 0
    atacando = False
    estado_jogo = "morto"


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif estado_jogo == "jogando":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # clique esquerdo - ataque corpo a corpo
                    atacando = True
                    ataque_index = ataque_timer = 0
                elif event.button == 3:  # clique direito - lança faca na posição do mouse
                    mx, my = pygame.mouse.get_pos()
                    direcao_faca = 1 if mx > player.centerx else -1
                    facas.append(Faca(player.centerx, player.centery, direcao=direcao_faca, alvo=(mx, my)))

    keys = pygame.key.get_pressed()

    if estado_jogo == "menu":
        if keys[pygame.K_RETURN]:
            estado_jogo = "jogando"
        desenhar_menu()

    elif estado_jogo == "morto":
        desenhar_restart()
        if keys[pygame.K_r]:
            reiniciar_jogo()

    elif estado_jogo == "jogando":
        # Spawn insetos até maximo 25 vivos
        while len(insetos) < 5 and (insetos_mortos + len(insetos)) < max_insetos:
            # Se já matou 24, spawnar o chefe
            if insetos_mortos == max_insetos - 1:
                insetos.append(InsetoVoador(random.randint(800, 1200), vida=10, chefe=True))
            else:
                insetos.append(InsetoVoador(random.randint(800, 1200)))

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
                        if vidas <= 0: morrer()
                insetos_ativos.append(inseto)
            else:
                insetos_mortos += 1
        insetos = insetos_ativos

        screen.blit(fundo, (0, 0))

        # Atualiza e desenha facas
        for faca in facas[:]:
            faca.mover()
            faca.desenhar(screen)
            for inseto in insetos:
                if faca.viva and not inseto.morrendo and not inseto.caindo and faca.rect.colliderect(inseto.rect):
                    inseto.sofrer_dano()  # corrigido o nome do método
                    faca.viva = False
            if not faca.viva:
                facas.remove(faca)

        # Ataque corpo a corpo
        if atacando:
            ataque_timer += 1
            if ataque_timer >= ataque_intervalo:
                ataque_index += 1
                ataque_timer = 0
                # Área de ataque
                if direcao_personagem == 1:
                    ataque_area = pygame.Rect(player.right, player.top, 40, player.height)
                else:
                    ataque_area = pygame.Rect(player.left - 40, player.top, 40, player.height)
                for inseto in insetos:
                    if not inseto.morrendo and not inseto.caindo and ataque_area.colliderect(inseto.rect):
                        inseto.sofrer_dano()
                if ataque_index >= len(ataque_frames):
                    atacando = False
                    ataque_index = 0
            frame_atual = ataque_frames[ataque_index]
            if direcao_personagem == -1:
                frame_atual = pygame.transform.flip(frame_atual, True, False)
            screen.blit(frame_atual, player.topleft)

        else:
            velocidade = vel_correndo if keys[pygame.K_LSHIFT] else vel_normal
            movendo = False
            if keys[pygame.K_a]:
                player.x -= velocidade
                direcao_personagem = -1
                movendo = True
            if keys[pygame.K_d]:
                player.x += velocidade
                direcao_personagem = 1
                movendo = True
            player.y = ALTURA_CHAO
            frame_timer += 1
            if frame_timer >= frame_interval:
                frame_timer = 0
                frame_index = (frame_index + 1) % len(andar_frames)
            frame_atual = andar_frames[frame_index] if movendo else andar_frames[0]
            if direcao_personagem == -1:
                frame_atual = pygame.transform.flip(frame_atual, True, False)
            screen.blit(frame_atual, player.topleft)

        # Vida do jogador
        vidas_texto = font.render(f"Vidas: {vidas}", True, (255, 255, 255))
        screen.blit(vidas_texto, (10, 10))

        # Insetos
        for inseto in insetos:
            inseto.desenhar(screen)

        if insetos_mortos >= max_insetos:
            # Vitória
            texto_vitoria = font.render("Você venceu!", True, (0, 255, 0))
            screen.blit(texto_vitoria, (350, 280))
            pygame.display.flip()
            pygame.time.delay(3000)
            reiniciar_jogo()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

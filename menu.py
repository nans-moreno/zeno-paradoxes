# menu.py
import pygame, sys
from dichotomy import DichotomyScene
from arrow import ArrowScene

WIDTH, HEIGHT = 980, 560
BLACK = (18, 18, 18)

def draw_vertical_gradient(surface, rect, color_top, color_bottom):
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        c = (int(color_top[0] + (color_bottom[0] - color_top[0]) * t),
             int(color_top[1] + (color_bottom[1] - color_top[1]) * t),
             int(color_top[2] + (color_bottom[2] - color_top[2]) * t))
        pygame.draw.line(surface, c, (x, y + i), (x + w, y + i))

class Button:
    def __init__(self, rect, label, font, on_click=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.font = font
        self.on_click = on_click
        self._hover = False
        self._down = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos): self._down = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was = self._down; self._down = False
            if was and self.rect.collidepoint(event.pos):
                if self.on_click: self.on_click()

    def draw(self, surface):
        base = (240,240,240); hov = (225,225,225); act = (210,210,210)
        color = act if self._down else (hov if self._hover else base)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (200,200,200), self.rect, 1, border_radius=10)
        img = self.font.render(self.label, True, BLACK)
        surface.blit(img, (self.rect.x + (self.rect.w - img.get_width()) // 2,
                           self.rect.y + (self.rect.h - img.get_height()) // 2))

class MenuScene:
    def __init__(self, screen, fonts, on_pick):
        self.screen = screen
        self.font, self.font_small, self.font_big = fonts
        self.on_pick = on_pick
        self.background = pygame.Surface((WIDTH, HEIGHT))
        draw_vertical_gradient(self.background, (0,0,WIDTH,HEIGHT), (225,238,255), (190,210,255))
        self.title = "Paradoxes de Zénon — Suite interactive"
        self.subtitle = [
            "Choisissez un paradoxe à explorer.",
            "Raccourcis en simulation: Espace ▶/❚❚, N (étape), R (réinit), S (réglages), M (menu)."
        ]
        self.buttons = []
        bw, bh = 420, 66
        spacing = 22
        start_y = HEIGHT//2 - (2*bh + spacing)//2
        x = (WIDTH - bw)//2
        self.buttons.append(Button((x, start_y, bw, bh), "Paradoxe de la Dichotomie (pomme → arbre)", self.font_big, lambda: self.on_pick("dichotomy")))
        self.buttons.append(Button((x, start_y + bh + spacing, bw, bh), "Paradoxe de la Flèche", self.font_big, lambda: self.on_pick("arrow")))

    def handle_event(self, event):
        for b in self.buttons: b.handle_event(event)

    def update(self, dt): pass

    def draw(self):
        self.screen.blit(self.background, (0,0))
        timg = self.font_big.render(self.title, True, BLACK)
        self.screen.blit(timg, ((WIDTH - timg.get_width())//2, 90))
        y = 140
        for line in self.subtitle:
            img = self.font.render(line, True, BLACK)
            self.screen.blit(img, ((WIDTH - img.get_width())//2, y))
            y += self.font.get_linesize() + 2
        for b in self.buttons: b.draw(self.screen)

class ZenoSuite:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Paradoxes de Zénon — Menu")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 22)
        self.font_small = pygame.font.SysFont(None, 20)
        self.font_big = pygame.font.SysFont(None, 28)
        fonts = (self.font, self.font_small, self.font_big)
        self.menu = MenuScene(self.screen, fonts, self.pick_scene)
        self.dichotomy = DichotomyScene(self.screen, fonts)
        self.arrow = ArrowScene(self.screen, fonts)
        self.scene = self.menu

    def pick_scene(self, which):
        self.scene = self.dichotomy if which == "dichotomy" else (self.arrow if which == "arrow" else self.menu)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.scene.handle_event(event)
            self.scene.update(dt)
            # retour menu si demandé par une scène
            if hasattr(self.scene, "back_to_menu") and self.scene.back_to_menu:
                self.scene.back_to_menu = False
                self.scene = self.menu
            self.scene.draw()
            pygame.display.flip()
        pygame.quit(); sys.exit()

if __name__ == "__main__":
    ZenoSuite().run()

import pygame
import sys

# ------------------ Constantes & Couleurs ------------------
WIDTH, HEIGHT = 900, 520

WHITE = (255, 255, 255)
BLACK = (18, 18, 18)
GREY = (220, 220, 220)
BROWN = (120, 70, 20)
BROWN_DARK = (85, 50, 15)
BROWN_LIGHT = (160, 95, 30)
BLUE_LINE = (48, 140, 255)

SKY_TOP = (210, 230, 255)
SKY_BOTTOM = (160, 200, 255)
GROUND_TOP = (150, 200, 150)
GROUND_BOTTOM = (110, 170, 110)

APPLE_RED = (225, 55, 55)
APPLE_RED_D = (175, 35, 35)

PANEL_BG = (250, 250, 245)
BTN_BG = (240, 240, 240)
BTN_BG_HOVER = (225, 225, 225)
BTN_BG_ACTIVE = (210, 210, 210)

# ------------------ Objets & Mécanique ------------------
APPLE_RADIUS = 14
TRUNK_WIDTH = 28
TRUNK_HEIGHT = 190

MIN_INTERVAL = 40
MAX_INTERVAL = 2000
DEFAULT_STEP_INTERVAL_MS = 600

# Valeurs par défaut si on appelle les setters avant lancement
_PENDING_DEFAULTS = {
    "distance_px": 300.0,
    "steps_per_sec": 1000.0 / DEFAULT_STEP_INTERVAL_MS,  # ~1.67
    "stop_distance_px": 0.5
}
APP_INSTANCE = None  # référence globale de l'app (pour setters externes)

# ------------------ Utilitaires dessin ------------------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def lerp(a, b, t):
    return a + (b - a) * t

def color_lerp(c1, c2, t):
    return (int(lerp(c1[0], c2[0], t)),
            int(lerp(c1[1], c2[1], t)),
            int(lerp(c1[2], c2[2], t)))

def draw_vertical_gradient(surface, rect, color_top, color_bottom):
    x, y, w, h = rect
    if h <= 0: return
    for i in range(h):
        t = i / max(1, (h - 1))
        c = color_lerp(color_top, color_bottom, t)
        pygame.draw.line(surface, c, (x, y + i), (x + w, y + i))

def draw_rounded_panel(surface, rect, bg, stroke=(40, 40, 40), radius=10, stroke_w=1):
    pygame.draw.rect(surface, bg, rect, border_radius=radius)
    if stroke_w > 0:
        pygame.draw.rect(surface, stroke, rect, width=stroke_w, border_radius=radius)

def draw_lines(surface, lines, start_pos, color, font, vspace=4):
    x, y = start_pos
    line_h = font.get_linesize()
    for text in lines:
        img = font.render(text, True, color)
        surface.blit(img, (x, y))
        y += line_h + vspace
    return y

# ------------------ Widgets ------------------
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
            if self.rect.collidepoint(event.pos):
                self._down = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_down = self._down
            self._down = False
            if was_down and self.rect.collidepoint(event.pos):
                if self.on_click: self.on_click()

    def draw(self, surface):
        color = BTN_BG
        if self._down:
            color = BTN_BG_ACTIVE
        elif self._hover:
            color = BTN_BG_HOVER
        draw_rounded_panel(surface, self.rect, color, stroke=(200, 200, 200), radius=8, stroke_w=1)
        text_img = self.font.render(self.label, True, BLACK)
        tx = self.rect.x + (self.rect.w - text_img.get_width()) // 2
        ty = self.rect.y + (self.rect.h - text_img.get_height()) // 2
        surface.blit(text_img, (tx, ty))

class Slider:
    """
    Slider discret: si step est défini, on 'snap' aux crans.
    Garantit que l'extrémité gauche = vmin (ex: 0.01) est atteignable.
    self.y = axe vertical de la piste (centre)
    """
    def __init__(self, x, y, w, vmin, vmax, value, step=None):
        self.x = x; self.y = y; self.w = w
        self.vmin = vmin; self.vmax = vmax
        self.step = step
        self.track_h = 6
        self.knob_r = 9
        self.dragging = False
        self._update_ticks()
        self.value = self._snap(value)

    def _update_ticks(self):
        if self.step and self.step > 0 and self.vmax > self.vmin:
            self.N = int(round((self.vmax - self.vmin) / self.step))
        else:
            self.N = None

    def set_range(self, vmin, vmax, step=None):
        self.vmin, self.vmax = vmin, vmax
        if step is not None:
            self.step = step
        self._update_ticks()
        self.value = self._snap(self.value)

    def _snap(self, v):
        v = clamp(v, self.vmin, self.vmax)
        if self.N is not None:
            # Convertit valeur -> cran entier, puis cran -> valeur exacte
            k = int(round((v - self.vmin) / (self.vmax - self.vmin) * self.N))
            k = clamp(k, 0, self.N)
            return self.vmin + k * (self.vmax - self.vmin) / self.N
        else:
            return v

    def _val_to_x(self):
        t = (self.value - self.vmin) / (self.vmax - self.vmin) if self.vmax > self.vmin else 0
        return int(round(self.x + t * self.w))

    def _x_to_val(self, px):
        t = clamp((px - self.x) / self.w, 0, 1)
        if self.N is not None:
            k = int(round(t * self.N))
            return self.vmin + k * (self.vmax - self.vmin) / self.N
        else:
            return self.vmin + t * (self.vmax - self.vmin)

    def handle_event(self, event):
        changed = False
        knob_x = self._val_to_x()
        knob_rect = pygame.Rect(knob_x - self.knob_r - 3, self.y - self.knob_r - 3, 2*(self.knob_r+3), 2*(self.knob_r+3))

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            track_rect = pygame.Rect(self.x, self.y - 10, self.w, 20)
            if knob_rect.collidepoint(event.pos) or track_rect.collidepoint(event.pos):
                self.dragging = True
                new_v = self._x_to_val(event.pos[0])
                new_v = self._snap(new_v)
                if new_v != self.value:
                    self.value = new_v
                    changed = True

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_v = self._x_to_val(event.pos[0])
            new_v = self._snap(new_v)
            if new_v != self.value:
                self.value = new_v
                changed = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        return changed

    def draw_track(self, surface):
        pygame.draw.rect(surface, (210, 210, 210), (self.x, self.y - self.track_h//2, self.w, self.track_h), border_radius=3)
        knob_x = self._val_to_x()
        pygame.draw.rect(surface, (140, 170, 240), (self.x, self.y - self.track_h//2, knob_x - self.x, self.track_h), border_radius=3)
        pygame.draw.circle(surface, (0, 0, 0, 60), (knob_x + 2, self.y + 2), self.knob_r + 1)
        pygame.draw.circle(surface, (255, 255, 255), (knob_x, self.y), self.knob_r)
        pygame.draw.circle(surface, (180, 180, 180), (knob_x, self.y), self.knob_r, width=1)

class TextInput:
    def __init__(self, rect, font, placeholder="", value="", numeric=True):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.placeholder = placeholder
        self.text = str(value)
        self.numeric = numeric
        self.active = False
        self.caret_visible = True
        self._blink_timer = 0

    def set_value(self, v, fmt=None):
        if fmt:
            self.text = fmt.format(v)
        else:
            self.text = str(v)

    def get_value(self):
        t = self.text.strip().replace(",", ".")
        if self.numeric:
            try:
                return float(t)
            except ValueError:
                return None
        return t

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True  # commit
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                ch = event.unicode
                if ch:
                    if not self.numeric or ch.isdigit() or ch in ".,+- ":
                        self.text += ch
        return False

    def update(self, dt_ms):
        if self.active:
            self._blink_timer += dt_ms
            if self._blink_timer >= 450:
                self._blink_timer = 0
                self.caret_visible = not self.caret_visible
        else:
            self.caret_visible = False
            self._blink_timer = 0

    def draw(self, surface):
        draw_rounded_panel(surface, self.rect, (255, 255, 255), stroke=(180, 180, 180), radius=8, stroke_w=1)
        txt = self.text.strip()
        if not txt:
            img = self.font.render(self.placeholder, True, (140, 140, 140))
        else:
            img = self.font.render(self.text, True, BLACK)
        x = self.rect.x + 8
        y = self.rect.y + (self.rect.h - img.get_height()) // 2
        surface.blit(img, (x, y))
        if self.active and self.caret_visible:
            caret_x = x + img.get_width() + 2
            pygame.draw.line(surface, BLACK, (caret_x, self.rect.y + 6), (caret_x, self.rect.y + self.rect.h - 6), 1)

# ------------------ Application principale ------------------
class ZenonApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Paradoxe de Zénon — Pomme (axe horizontal)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 22)
        self.font_small = pygame.font.SysFont(None, 20)
        self.font_big = pygame.font.SysFont(None, 28)

        # Scène
        self.ground_y = HEIGHT - 90
        self.trunk_rect = pygame.Rect(0, 0, TRUNK_WIDTH, TRUNK_HEIGHT)
        self.trunk_rect.midbottom = (WIDTH - 160, self.ground_y)

        self.apple_y = float(self.trunk_rect.centery)
        self.target_x = float(self.trunk_rect.left)

        # Paramètres (distance, vitesse, epsilon)
        self.chosen_distance = 300.0
        self.step_interval = DEFAULT_STEP_INTERVAL_MS
        self.stop_epsilon = 0.5
        self.apply_pending_defaults()

        # État simulation
        self.apple_x = self.start_x()
        self.auto = False
        self.reached = False
        self.step_count = 0
        self.total_travel = 0.0
        self.last_step_delta = 0.0
        self.last_step_time = pygame.time.get_ticks()

        # Boutons de contrôle (haut droite)
        self.buttons = []
        pad = 8
        bx = WIDTH - 15
        by = 12
        bw, bh = 92, 34

        def add_btn(label, cb):
            nonlocal bx
            r = pygame.Rect(bx - bw, by, bw, bh)
            b = Button(r, label, self.font, cb)
            self.buttons.append(b)
            bx -= (bw + pad)

        add_btn("Réglages", self.toggle_settings)
        add_btn("Réinit.", self.reset)
        add_btn("Étape", self.step_once)
        add_btn("❚❚/▶", self.toggle_auto)

        # Panneau réglages
        self.settings_open = False
        self._build_settings_ui()

        # Fond pré-rendu
        self.background = pygame.Surface((WIDTH, HEIGHT))
        self._render_background(self.background)

        self.inputs = [self.in_distance, self.in_speed, self.in_epsilon]
        self.focus_index = -1

    # ---------- Helpers ----------
    def _render_background(self, surf):
        draw_vertical_gradient(surf, (0, 0, WIDTH, self.ground_y), SKY_TOP, SKY_BOTTOM)
        draw_vertical_gradient(surf, (0, self.ground_y, WIDTH, HEIGHT - self.ground_y), GROUND_TOP, GROUND_BOTTOM)

    def valid_distance_range(self):
        return 10.0, (self.target_x - (APPLE_RADIUS + 12))

    def steps_per_second(self):
        return 1000.0 / self.step_interval if self.step_interval > 0 else 0.0

    def interval_from_sps(self, sps):
        if sps and sps > 0:
            ms = int(round(1000.0 / sps))
            return clamp(ms, MIN_INTERVAL, MAX_INTERVAL)
        return self.step_interval

    def start_x(self):
        return self.target_x - self.chosen_distance

    def reset(self):
        self.apple_x = self.start_x()
        self.auto = False
        self.reached = False
        self.step_count = 0
        self.total_travel = 0.0
        self.last_step_delta = 0.0
        self.last_step_time = pygame.time.get_ticks()

    def toggle_auto(self):
        if not self.reached:
            self.auto = not self.auto
            self.last_step_time = pygame.time.get_ticks()

    def step_once(self):
        if not self.auto:
            self.perform_step()

    def remaining_distance(self):
        return abs(self.target_x - self.apple_x)

    def apply_pending_defaults(self):
        dmin, dmax = self.valid_distance_range()
        self.chosen_distance = clamp(float(_PENDING_DEFAULTS["distance_px"]), dmin, dmax)
        self.step_interval = self.interval_from_sps(float(_PENDING_DEFAULTS["steps_per_sec"]))
        self.stop_epsilon = float(_PENDING_DEFAULTS["stop_distance_px"])

    # ---------- Réglages UI (sans chevauchement) ----------
    def _build_settings_ui(self):
        # Panneau: largeur/hauteur; hauteur recalculée dynamiquement
        panel_w, panel_h = 600, 200
        self.settings_rect = pygame.Rect(20, 20, panel_w, panel_h)

        base_x = self.settings_rect.x + 20
        right_pad = 20
        input_w, input_h = 160, 36

        # Colonne droite: zone des inputs
        in_x = self.settings_rect.right - right_pad - input_w

        # La piste des sliders s’arrête avant les inputs
        track_w = (in_x - 12) - base_x  # marge 12px

        # Positions verticales
        top_y = self.settings_rect.y + 64
        row_gap = 92
        row1_y = top_y
        row2_y = row1_y + row_gap
        row3_y = row2_y + row_gap

        # Plages sliders
        dmin, dmax = self.valid_distance_range()

        # Sliders (y au dessous des inputs)
        self.sld_distance = Slider(base_x, row1_y + input_h + 12, track_w, dmin, dmax, clamp(_PendingOrDefault("distance_px", 300.0), dmin, dmax), step=1.0)
        self.sld_speed    = Slider(base_x, row2_y + input_h + 12, track_w, 0.2, 20.0, max(0.2, self.steps_per_second()), step=0.1)
        # ε: min 0.01, step 0.01 (discret)
        self.sld_epsilon  = Slider(base_x, row3_y + input_h + 12, track_w, 0.01, 20.0, max(0.01, _PendingOrDefault("stop_distance_px", 0.5)), step=0.01)

        # Inputs
        self.in_distance = TextInput((in_x, row1_y, input_w, input_h), self.font, placeholder="px", value=f"{self.chosen_distance:.1f}")
        self.in_speed    = TextInput((in_x, row2_y, input_w, input_h), self.font, placeholder="étapes/s", value=f"{self.steps_per_second():.2f}")
        self.in_epsilon  = TextInput((in_x, row3_y, input_w, input_h), self.font, placeholder="ε (px)", value=f"{self.stop_epsilon:.2f}")

        # Libellés
        self._rows = [
            ("Distance initiale (px)", row1_y),
            ("Vitesse (étapes/s)", row2_y),
            ("Distance d'arrêt ε (px)", row3_y)
        ]

        # Boutons sous le dernier slider
        b_w, b_h = 120, 34
        below_last_slider = self.sld_epsilon.y + self.sld_epsilon.knob_r + 20
        x1 = self.settings_rect.right - (b_w + 20)
        x0 = x1 - (b_w + 10)
        yb = int(below_last_slider + 12)
        self.btn_apply = Button((x0, yb, b_w, b_h), "Appliquer", self.font, on_click=self.apply_settings)
        self.btn_close = Button((x1, yb, b_w, b_h), "Fermer", self.font, on_click=self.toggle_settings)

        # Ajuste la hauteur du panneau pour contenir proprement les boutons
        new_panel_h = (yb + b_h + 16) - self.settings_rect.y
        self.settings_rect.h = max(self.settings_rect.h, new_panel_h)

    def toggle_settings(self):
        self.settings_open = not self.settings_open
        if self.settings_open:
            self.auto = False
            # Sync sliders/inputs avec l'état courant
            dmin, dmax = self.valid_distance_range()
            self.sld_distance.set_range(dmin, dmax, step=1.0)
            self.sld_distance.value = clamp(self.chosen_distance, dmin, dmax)
            self.in_distance.set_value(self.sld_distance.value, fmt="{:.1f}")

            self.sld_speed.set_range(0.2, 20.0, step=0.1)
            self.sld_speed.value = clamp(self.steps_per_second(), 0.2, 20.0)
            self.in_speed.set_value(self.sld_speed.value, fmt="{:.2f}")

            self.sld_epsilon.set_range(0.01, 20.0, step=0.01)
            self.sld_epsilon.value = max(0.01, self.stop_epsilon)
            self.in_epsilon.set_value(self.sld_epsilon.value, fmt="{:.2f}")

            self.focus_index = -1
            for inp in [self.in_distance, self.in_speed, self.in_epsilon]:
                inp.active = False

    def apply_settings(self):
        # Inputs priment si valides, sinon sliders
        dmin, dmax = self.valid_distance_range()

        d_val = self.in_distance.get_value()
        if d_val is None: d_val = self.sld_distance.value
        d_val = clamp(d_val, dmin, dmax)

        sps_val = self.in_speed.get_value()
        if sps_val is None or sps_val <= 0: sps_val = self.sld_speed.value
        sps_val = clamp(sps_val, 0.2, 20.0)

        eps_val = self.in_epsilon.get_value()
        if eps_val is None or eps_val <= 0: eps_val = self.sld_epsilon.value
        eps_val = clamp(eps_val, 0.01, 1000.0)  # min 0.01

        self.chosen_distance = d_val
        self.step_interval = self.interval_from_sps(sps_val)
        self.stop_epsilon = eps_val

        # Resync affichage
        self.sld_distance.value = self.chosen_distance
        self.in_distance.set_value(self.chosen_distance, fmt="{:.1f}")
        self.sld_speed.value = sps_val
        self.in_speed.set_value(sps_val, fmt="{:.2f}")
        self.sld_epsilon.value = self.stop_epsilon
        self.in_epsilon.set_value(self.stop_epsilon, fmt="{:.2f}")

        self.reset()
        self.settings_open = False

    # ---------- API publique ----------
    def set_parameters(self, distance_px=None, steps_per_sec=None, stop_distance_px=None, reset_view=True):
        if distance_px is not None:
            self.chosen_distance = clamp(float(distance_px), *self.valid_distance_range())
        if steps_per_sec is not None:
            self.step_interval = self.interval_from_sps(float(steps_per_sec))
        if stop_distance_px is not None:
            self.stop_epsilon = max(0.01, float(stop_distance_px))  # min 0.01
        if reset_view:
            self.reset()

    # ---------- Simulation ----------
    def perform_step(self):
        if self.reached:
            return
        prev_x = self.apple_x
        self.apple_x = 0.5 * (self.apple_x + self.target_x)  # moitié de la distance restante
        self.last_step_delta = abs(self.apple_x - prev_x)
        self.total_travel += self.last_step_delta
        self.step_count += 1
        if self.remaining_distance() <= self.stop_epsilon:
            self.reached = True

    # ---------- Dessin scène ----------
    def draw_trunk(self, surface):
        r = self.trunk_rect
        trunk_surf = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        draw_vertical_gradient(trunk_surf, (0, 0, r.w, r.h), BROWN_LIGHT, BROWN_DARK)
        pygame.draw.rect(trunk_surf, (255, 255, 255, 25), (0, 0, 6, r.h))
        pygame.draw.rect(trunk_surf, (0, 0, 0, 30), (r.w - 6, 0, 6, r.h))
        surface.blit(trunk_surf, r.topleft)
        pygame.draw.ellipse(surface, (0, 0, 0, 40), (r.centerx - r.w, r.bottom - 6, 2*r.w, 12))

    def draw_apple(self, surface):
        x, y = int(self.apple_x), int(self.apple_y)
        # Ombre portée
        shadow = pygame.Surface((APPLE_RADIUS*4, APPLE_RADIUS*4), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0, 0, 0, 70), (APPLE_RADIUS*2, APPLE_RADIUS*2), APPLE_RADIUS + 2)
        # CORRECTION: passer une position (tuple) et non deux entiers séparés
        surface.blit(shadow, (x - (APPLE_RADIUS*2) + 3, y - (APPLE_RADIUS*2) + 3))
        # Corps de la pomme
        pygame.draw.circle(surface, APPLE_RED_D, (x, y), APPLE_RADIUS + 2)
        pygame.draw.circle(surface, APPLE_RED, (x, y), APPLE_RADIUS)
        # Reflet
        pygame.draw.circle(surface, (255, 255, 255, 160), (x - 5, y - 5), 5)
        

    def draw_hud(self):
        info_rect = pygame.Rect(16, 12, 380, 170)
        draw_rounded_panel(self.screen, info_rect, PANEL_BG, radius=10)
        d_remain = self.remaining_distance()
        lines = [
            f"Mode: {'AUTO' if self.auto else 'PAUSE'}",
            f"Étapes: {self.step_count}",
            f"Distance initiale: {self.chosen_distance:.1f}px",
            f"Distance parcourue (étape): {self.last_step_delta:.3f}px",
            f"Distance parcourue (totale): {self.total_travel:.3f}px",
            f"Distance restante: {d_remain:.3f}px",
            f"Vitesse: {self.steps_per_second():.2f} étapes/s (Δ: {self.step_interval} ms)",
            f"ε (arrêt): {self.stop_epsilon:.2f}px",
        ]
        draw_lines(self.screen, lines, (info_rect.x + 12, info_rect.y + 10), BLACK, self.font, vspace=2)

        for b in self.buttons:
            b.draw(self.screen)

        pygame.draw.line(self.screen, BLUE_LINE, (int(self.apple_x), int(self.apple_y)),
                         (int(self.target_x), int(self.apple_y)), 2)

        if self.reached:
            msg_rect = pygame.Rect(16, info_rect.bottom + 10, 460, 64)
            draw_rounded_panel(self.screen, (msg_rect), (255, 250, 220), radius=10)
            draw_lines(self.screen, [
                "Fin: seuil d'arrêt atteint.",
                f"Étapes: {self.step_count} | d_totale: {self.total_travel:.3f}px | d_restante: {self.remaining_distance():.3f}px"
            ], (msg_rect.x + 12, msg_rect.y + 10), BLACK, self.font, vspace=2)

    def draw_settings(self):
        draw_rounded_panel(self.screen, self.settings_rect, PANEL_BG, radius=12)
        title = self.font_big.render("Réglages", True, BLACK)
        self.screen.blit(title, (self.settings_rect.x + 20, self.settings_rect.y + 20))

        # Lignes: libellé + input (ligne 1), piste slider (ligne 2)
        for (label, y), input_widget, slider in [
            (self._rows[0], self.in_distance, self.sld_distance),
            (self._rows[1], self.in_speed,    self.sld_speed),
            (self._rows[2], self.in_epsilon,  self.sld_epsilon),
        ]:
            self.screen.blit(self.font.render(label, True, BLACK), (self.settings_rect.x + 20, y))
            input_widget.draw(self.screen)
            slider.draw_track(self.screen)

        self.btn_apply.draw(self.screen)
        self.btn_close.draw(self.screen)

    # ---------- Boucle principale ----------
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)

            if self.settings_open:
                for inp in [self.in_distance, self.in_speed, self.in_epsilon]:
                    inp.update(dt)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and not self.settings_open:
                        self.toggle_auto()
                    elif event.key == pygame.K_n and not self.settings_open:
                        self.step_once()
                    elif event.key == pygame.K_r and not self.settings_open:
                        self.reset()
                    elif event.key == pygame.K_s:
                        self.toggle_settings()
                    elif event.key == pygame.K_UP and not self.settings_open:
                        self.step_interval = max(MIN_INTERVAL, self.step_interval - 40)
                    elif event.key == pygame.K_DOWN and not self.settings_open:
                        self.step_interval = min(MAX_INTERVAL, self.step_interval + 40)
                    elif event.key == pygame.K_TAB and self.settings_open:
                        if self.focus_index == -1:
                            self.focus_index = 0
                        else:
                            self.focus_index = (self.focus_index + 1) % len(self.inputs)
                        for i, inp in enumerate(self.inputs):
                            inp.active = (i == self.focus_index)

                # Widgets
                if self.settings_open:
                    # Sliders → maj inputs (live)
                    if self.sld_distance.handle_event(event):
                        self.in_distance.set_value(self.sld_distance.value, fmt="{:.1f}")
                    if self.sld_speed.handle_event(event):
                        self.in_speed.set_value(self.sld_speed.value, fmt="{:.2f}")
                    if self.sld_epsilon.handle_event(event):
                        self.in_epsilon.set_value(self.sld_epsilon.value, fmt="{:.2f}")

                    # Inputs (Entrée = commit → Appliquer tout)
                    committed = False
                    if self.in_distance.handle_event(event):
                        val = self.in_distance.get_value()
                        if val is not None:
                            self.sld_distance.value = clamp(val, *self.valid_distance_range())
                        committed = True
                    if self.in_speed.handle_event(event):
                        val = self.in_speed.get_value()
                        if val is not None and val > 0:
                            self.sld_speed.value = clamp(val, 0.2, 20.0)
                        committed = True
                    if self.in_epsilon.handle_event(event):
                        val = self.in_epsilon.get_value()
                        if val is not None and val > 0:
                            # Snap et clamp min 0.01
                            self.sld_epsilon.value = max(0.01, val)
                            self.sld_epsilon.value = self.sld_epsilon._snap(self.sld_epsilon.value)
                            self.in_epsilon.set_value(self.sld_epsilon.value, fmt="{:.2f}")
                        committed = True
                    if committed:
                        self.apply_settings()

                    # Boutons
                    self.btn_apply.handle_event(event)
                    self.btn_close.handle_event(event)
                else:
                    for b in self.buttons:
                        b.handle_event(event)

            # Avancement auto
            if self.auto and not self.reached and not self.settings_open:
                now = pygame.time.get_ticks()
                if now - self.last_step_time >= self.step_interval:
                    self.perform_step()
                    self.last_step_time = now

            # ---- Rendu global ----
            self.screen.blit(self.background, (0, 0))
            pygame.draw.line(self.screen, (120, 160, 120), (0, self.ground_y), (WIDTH, self.ground_y), 2)
            self.draw_trunk(self.screen)
            self.draw_apple(self.screen)
            self.draw_hud()
            if self.settings_open:
                self.draw_settings()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

# ------------------ Helpers internes ------------------
def _PendingOrDefault(key, default):
    return _PENDING_DEFAULTS.get(key, default)

# ------------------ Fonctions publiques ------------------
def set_parameters(distance_px=None, steps_per_sec=None, stop_distance_px=None):
    global APP_INSTANCE, _PENDING_DEFAULTS
    if APP_INSTANCE is not None:
        APP_INSTANCE.set_parameters(distance_px, steps_per_sec, stop_distance_px, reset_view=True)
    else:
        if distance_px is not None:
            _PENDING_DEFAULTS["distance_px"] = float(distance_px)
        if steps_per_sec is not None:
            _PENDING_DEFAULTS["steps_per_sec"] = float(steps_per_sec)
        if stop_distance_px is not None:
            _PENDING_DEFAULTS["stop_distance_px"] = float(stop_distance_px)

def set_distance_and_speed(distance_px=None, steps_per_sec=None):
    set_parameters(distance_px=distance_px, steps_per_sec=steps_per_sec, stop_distance_px=None)

def main():
    global APP_INSTANCE
    APP_INSTANCE = ZenonApp()
    APP_INSTANCE.run()

if __name__ == "__main__":
    main()


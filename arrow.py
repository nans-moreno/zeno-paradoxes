# arrow.py
import pygame

WIDTH, HEIGHT = 980, 560

# Thème
BLACK=(18,18,18)
SKY_TOP=(210,230,255); SKY_BOTTOM=(160,200,255)
GROUND_TOP=(150,200,150); GROUND_BOTTOM=(110,170,110)

def clamp(v, lo, hi): return max(lo, min(hi, v))
def draw_vertical_gradient(surface, rect, color_top, color_bottom):
    x,y,w,h=rect
    for i in range(h):
        t=i/max(1,h-1)
        c=(int(color_top[0]+(color_bottom[0]-color_top[0])*t),
           int(color_top[1]+(color_bottom[1]-color_top[1])*t),
           int(color_top[2]+(color_bottom[2]-color_top[2])*t))
        pygame.draw.line(surface, c, (x,y+i),(x+w,y+i))

# Widgets légers
class Button:
    def __init__(self, rect, label, font, on_click=None):
        self.rect=pygame.Rect(rect); self.label=label; self.font=font; self.on_click=on_click
        self._hover=False; self._down=False
    def handle_event(self, e):
        if e.type==pygame.MOUSEMOTION: self._hover=self.rect.collidepoint(e.pos)
        elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1 and self.rect.collidepoint(e.pos): self._down=True
        elif e.type==pygame.MOUSEBUTTONUP and e.button==1:
            was=self._down; self._down=False
            if was and self.rect.collidepoint(e.pos) and self.on_click: self.on_click()
    def draw(self, s):
        base=(240,240,240); hov=(225,225,225); act=(210,210,210)
        col=act if self._down else (hov if self._hover else base)
        pygame.draw.rect(s, col, self.rect, border_radius=10)
        pygame.draw.rect(s, (200,200,200), self.rect, 1, border_radius=10)
        img=self.font.render(self.label, True, BLACK)
        s.blit(img, (self.rect.x+(self.rect.w-img.get_width())//2, self.rect.y+(self.rect.h-img.get_height())//2))

class Slider:
    def __init__(self, x, y, w, vmin, vmax, value, step=None):
        self.x=x; self.y=y; self.w=w; self.vmin=vmin; self.vmax=vmax; self.step=step
        self.track_h=6; self.knob_r=9; self.dragging=False
        self._update_ticks(); self.value=self._snap(value)
    def _update_ticks(self):
        if self.step and self.step>0 and self.vmax>self.vmin: self.N=int(round((self.vmax-self.vmin)/self.step))
        else: self.N=None
    def set_range(self, vmin, vmax, step=None):
        self.vmin=vmin; self.vmax=vmax
        if step is not None: self.step=step
        self._update_ticks(); self.value=self._snap(self.value)
    def _snap(self, v):
        v=clamp(v, self.vmin, self.vmax)
        if self.N is not None:
            k=int(round((v-self.vmin)/(self.vmax-self.vmin)*self.N)); k=clamp(k,0,self.N)
            return self.vmin + k*(self.vmax-self.vmin)/self.N
        return v
    def _val_to_x(self):
        t=(self.value-self.vmin)/(self.vmax-self.vmin) if self.vmax>self.vmin else 0
        return int(round(self.x + t*self.w))
    def _x_to_val(self, px):
        t=clamp((px-self.x)/self.w, 0, 1)
        if self.N is not None:
            k=int(round(t*self.N)); return self.vmin + k*(self.vmax-self.vmin)/self.N
        return self.vmin + t*(self.vmax-self.vmin)
    def handle_event(self, e):
        changed=False; kx=self._val_to_x()
        knob=pygame.Rect(kx-self.knob_r-3, self.y-self.knob_r-3, 2*(self.knob_r+3), 2*(self.knob_r+3))
        if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
            tr=pygame.Rect(self.x, self.y-10, self.w, 20)
            if knob.collidepoint(e.pos) or tr.collidepoint(e.pos):
                self.dragging=True
                nv=self._snap(self._x_to_val(e.pos[0])); 
                if nv!=self.value: self.value=nv; changed=True
        elif e.type==pygame.MOUSEMOTION and self.dragging:
            nv=self._snap(self._x_to_val(e.pos[0])); 
            if nv!=self.value: self.value=nv; changed=True
        elif e.type==pygame.MOUSEBUTTONUP and e.button==1:
            self.dragging=False
        return changed
    def draw(self, s):
        pygame.draw.rect(s, (210,210,210), (self.x, self.y-self.track_h//2, self.w, self.track_h), border_radius=3)
        kx=self._val_to_x()
        pygame.draw.rect(s, (140,170,240), (self.x, self.y-self.track_h//2, kx-self.x, self.track_h), border_radius=3)
        pygame.draw.circle(s, (0,0,0,60), (kx+2, self.y+2), self.knob_r+1)
        pygame.draw.circle(s, (255,255,255), (kx, self.y), self.knob_r)
        pygame.draw.circle(s, (180,180,180), (kx, self.y), self.knob_r, 1)

class TextInput:
    def __init__(self, rect, font, value="", numeric=True):
        self.rect=pygame.Rect(rect); self.font=font; self.text=str(value); self.numeric=numeric
        self.active=False; self.caret=True; self._blink=0
    def set_value(self, v, fmt=None): self.text=(fmt.format(v) if fmt else str(v))
    def get_value(self):
        t=self.text.strip().replace(",", ".")
        if self.numeric:
            try: return float(t)
            except ValueError: return None
        return t
    def handle_event(self, e):
        if e.type==pygame.MOUSEBUTTONDOWN and e.button==1: self.active=self.rect.collidepoint(e.pos)
        elif e.type==pygame.KEYDOWN and self.active:
            if e.key==pygame.K_RETURN: return True
            elif e.key==pygame.K_BACKSPACE: self.text=self.text[:-1]
            else:
                ch=e.unicode
                if ch and (not self.numeric or ch.isdigit() or ch in ".,+- "): self.text+=ch
        return False
    def update(self, dt):
        if self.active:
            self._blink+=dt
            if self._blink>=450: self._blink=0; self.caret=not self.caret
        else:
            self.caret=False; self._blink=0
    def draw(self, s):
        pygame.draw.rect(s, (255,255,255), self.rect, border_radius=8)
        pygame.draw.rect(s, (180,180,180), self.rect, 1, border_radius=8)
        txt=self.text if self.text else ""
        img=self.font.render(txt, True, BLACK)
        x=self.rect.x+8; y=self.rect.y+(self.rect.h-img.get_height())//2
        s.blit(img, (x,y))
        if self.active and self.caret:
            cx=x+img.get_width()+2
            pygame.draw.line(s, BLACK, (cx, self.rect.y+6), (cx, self.rect.y+self.rect.h-6), 1)

# Scène Flèche
class ArrowScene:
    def __init__(self, screen, fonts):
        self.screen=screen
        self.font, self.font_small, self.font_big = fonts

        # Décor
        self.ground_y=HEIGHT-90
        self.track_y=self.ground_y-80
        self.background=pygame.Surface((WIDTH,HEIGHT))
        self._render_background(self.background)

        # Paramètres
        self.arrow_speed=260.0     # px/s
        self.strobe_period=0.20    # s entre "instants"
        self.trail_len=6           # nb d'instantanés à afficher
        self.instant_mode=True     # stroboscopique

        # État — départ à GAUCHE, mouvement →, tête à DROITE
        self.x_start=60.0          # bord gauche piste
        self.x_end=WIDTH-140.0
        self.x=self.x_start
        self.auto=False
        self.last_time=pygame.time.get_ticks()
        self.accum=0.0
        self.snapshots=[]
        self.back_to_menu=False

        # UI
        self._build_top_buttons()
        self.settings_open=False
        
    def _request_menu(self): self.back_to_menu = True
    # Décor
    def _render_background(self, surf):
        draw_vertical_gradient(surf, (0,0,WIDTH,self.ground_y), SKY_TOP, SKY_BOTTOM)
        draw_vertical_gradient(surf, (0,self.ground_y,WIDTH,HEIGHT-self.ground_y), GROUND_TOP, GROUND_BOTTOM)

    # Boutons haut-droite
    def _build_top_buttons(self):
        self.buttons=[]
        pad=8; bx=WIDTH-15; by=12; bw,bh=140,34
        def add(label, cb):
            nonlocal bx
            r=pygame.Rect(bx-bw, by, bw, bh); self.buttons.append(Button(r,label,self.font,cb)); bx-=(bw+pad)
        add("Menu (M)", self._go_menu)
        add("Réglages (S)", self._toggle_settings)
        add("Réinit. (R)", self.reset)
        add("Étape (N)", self.step_once)
        add("❚❚/▶ (Espace)", self.toggle_auto)

    def _go_menu(self): self.back_to_menu=True

    # Mouvement: TOUJOURS vers la DROITE, départ GAUCHE
    def toggle_auto(self):
        self.auto=not self.auto
        self.last_time=pygame.time.get_ticks()
    def reset(self):
        self.x=self.x_start
        self.snapshots.clear()
        self.accum=0.0
        self.auto=False
    def step_once(self):
        dt=self.strobe_period if self.instant_mode else 0.05
        self._advance(dt)
    def _advance(self, dt):
        self.x += self.arrow_speed * dt
        if self.x > self.x_end:
            self.x = self.x_start + (self.x - self.x_end)  # boucle à gauche
            self.snapshots.clear()
        if self.instant_mode:
            self.snapshots.append(self.x)
            if len(self.snapshots) > self.trail_len:
                self.snapshots = self.snapshots[-self.trail_len:]

    # Réglages
    def _build_settings(self):
        self.settings_rect=pygame.Rect(20,20,640,300)
        base_x=self.settings_rect.x+20; input_w,input_h=160,36; in_x=self.settings_rect.right-20-input_w
        track_w=(in_x-12)-base_x
        top_y=self.settings_rect.y+64; gap=92
        y1=top_y; y2=y1+gap; y3=y2+gap

        self.sld_speed =Slider(base_x, y1+input_h+12, track_w, 10.0,1000.0, self.arrow_speed, step=10.0)
        self.sld_period=Slider(base_x, y2+input_h+12, track_w, 0.02,1.00, self.strobe_period, step=0.01)
        self.sld_trail =Slider(base_x, y3+input_h+12, track_w, 0.0,20.0, float(self.trail_len), step=1.0)

        self.in_speed =TextInput((in_x,y1,input_w,input_h), self.font, f"{self.arrow_speed:.1f}")
        self.in_period=TextInput((in_x,y2,input_w,input_h), self.font, f"{self.strobe_period:.2f}")
        self.in_trail =TextInput((in_x,y3,input_w,input_h), self.font, f"{self.trail_len:.0f}")

        b_w,b_h=120,34
        below=y3 + input_h + 30
        x1=self.settings_rect.right-(b_w+20); x0=x1-(b_w+10); yb=int(below)
        self.btn_apply=Button((x0,yb,b_w,b_h), "Appliquer", self.font, self._apply_settings)
        self.btn_close=Button((x1,yb,b_w,b_h), "Fermer", self.font, self._toggle_settings)
        self.settings_rect.h=(yb+b_h+16)-self.settings_rect.y

        self._rows=[("Vitesse (px/s)", y1), ("Période d'instant t (s)", y2), ("Longueur traînée (#)", y3)]

    def _toggle_settings(self):
        self.settings_open=not self.settings_open
        if self.settings_open:
            self.auto=False
            self.sld_speed.set_range(10.0,1000.0,10.0); self.sld_speed.value=clamp(self.arrow_speed,10.0,1000.0); self.in_speed.set_value(self.sld_speed.value, "{:.1f}")
            self.sld_period.set_range(0.02,1.00,0.01); self.sld_period.value=clamp(self.strobe_period,0.02,1.00); self.in_period.set_value(self.sld_period.value, "{:.2f}")
            self.sld_trail.set_range(0.0,20.0,1.0); self.sld_trail.value=clamp(float(self.trail_len),0.0,20.0); self.in_trail.set_value(self.sld_trail.value, "{:.0f}")

    def _apply_settings(self):
        spd = self.in_speed.get_value()  or self.sld_speed.value
        per = self.in_period.get_value() or self.sld_period.value
        trl = self.in_trail.get_value()  or self.sld_trail.value
        self.arrow_speed = clamp(spd, 10.0, 1000.0)
        self.strobe_period = clamp(per, 0.02, 1.00)
        self.trail_len = int(clamp(trl, 0.0, 20.0))
        self.snapshots = self.snapshots[-self.trail_len:]
        self.reset()
        self.settings_open=False
        self.auto=False

    # Entrées
    def handle_event(self, e):
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_m or e.key==pygame.K_ESCAPE: self._go_menu()
            elif e.key==pygame.K_SPACE and not self.settings_open: self.toggle_auto()
            elif e.key==pygame.K_n and not self.settings_open: self.step_once()
            elif e.key==pygame.K_r and not self.settings_open: self.reset()
            elif e.key==pygame.K_s: self._toggle_settings()

        if self.settings_open:
            if self.sld_speed.handle_event(e): self.in_speed.set_value(self.sld_speed.value, "{:.1f}")
            if self.sld_period.handle_event(e): self.in_period.set_value(self.sld_period.value, "{:.2f}")
            if self.sld_trail.handle_event(e): self.in_trail.set_value(self.sld_trail.value, "{:.0f}")
            committed=False
            if self.in_speed.handle_event(e):
                v=self.in_speed.get_value()
                if v is not None and v>10: self.sld_speed.value=clamp(v,10.0,1000.0)
                committed=True
            if self.in_period.handle_event(e):
                v=self.in_period.get_value()
                if v is not None and v>0: self.sld_period.value=clamp(v,0.02,1.00)
                committed=True
            if self.in_trail.handle_event(e):
                v=self.in_trail.get_value()
                if v is not None and v>=0: self.sld_trail.value=clamp(v,0.0,20.0)
                committed=True
            if committed: self._apply_settings()
            self.btn_apply.handle_event(e); self.btn_close.handle_event(e)
        else:
            for b in self.buttons: b.handle_event(e)

    # Update
    def update(self, dt):
        if self.settings_open:
            for inp in (self.in_speed, self.in_period, self.in_trail): inp.update(dt)
        if self.auto and not self.settings_open:
            now=pygame.time.get_ticks()
            dt=(now - self.last_time)/1000.0
            self.last_time=now
            if self.instant_mode:
                self.accum+=dt
                while self.accum>=self.strobe_period:
                    self._advance(self.strobe_period); self.accum-=self.strobe_period
            else:
                self._advance(dt)

    # Dessins
    def _draw_track(self):
        y=self.track_y
        pygame.draw.line(self.screen, (60,60,60), (60,y), (WIDTH-60,y), 2)
        for i in range(10):
            tx = 60 + (WIDTH-120)*i/9
            pygame.draw.line(self.screen, (120,120,120), (int(tx), y-6), (int(tx), y+6), 1)

    def _draw_arrow(self, x, y, color=(20,20,20), alpha=255, scale=1.0):
        # Flèche vers la DROITE, tête à DROITE du corps
        shaft_w, head_w, h = 58, 20, 16
        surf = pygame.Surface((shaft_w + head_w, h), pygame.SRCALPHA)
        col = (color[0], color[1], color[2], alpha)

        # Corps (tige)
        pygame.draw.rect(surf, col, (0, (h - 4) // 2, shaft_w, 4), border_radius=2)

        # TÊTE (triangle) → vers la DROITE (ligne à modifier)
        pygame.draw.polygon(surf, col, [
            (shaft_w, h ),
            (shaft_w, 0),
            (shaft_w + head_w, h//2)
            
        ])

        # Reflet (optionnel)
        pygame.draw.rect(surf, (255,255,255,60), (2, (h - 4)//2 + 1, 40, 2), border_radius=1)

        # Pas de flip/rotation ici
        if scale != 1.0:
            surf = pygame.transform.smoothscale(surf, (int(surf.get_width()*scale), int(h*scale)))
            h = surf.get_height()

        self.screen.blit(surf, (int(x), int(y - h/2)))




    def draw(self):
        self.screen.blit(self.background, (0,0))
        pygame.draw.line(self.screen, (120,160,120), (0,self.ground_y), (WIDTH,self.ground_y), 2)
        self._draw_track()

        # Traînée (instantané)
        if self.trail_len>0 and len(self.snapshots)>0:
            alphas=[max(30, int(200*(i+1)/max(1,self.trail_len))) for i in range(len(self.snapshots))]
            for xi,a in zip(self.snapshots[:-1], alphas[:-1]):
                self._draw_arrow(xi, self.track_y, color=(20,80,20), alpha=a, scale=1.0)

        # Flèche actuelle (→)
        self._draw_arrow(self.x, self.track_y, color=(20,20,20), alpha=255, scale=1.0)

        # HUD minimal
        panel=pygame.Rect(16,12,520,164)
        pygame.draw.rect(self.screen, (250,250,245), panel, border_radius=10)
        pygame.draw.rect(self.screen, (40,40,40), panel, 1, border_radius=10)
        mode="Instantané (stroboscopique)" if self.instant_mode else "Continu"
        lines=[
            f"Flèche — Mode: {'AUTO' if self.auto else 'PAUSE'}",
            f"Affichage: {mode}",
            f"Vitesse: {self.arrow_speed:.1f} px/s",
            f"Période t: {self.strobe_period:.2f} s   •   Traînée: {self.trail_len}",
            "Raccourcis: Espace/N/R/S/M"
        ]
        y=panel.y+10
        for t in lines:
            img=self.font.render(t, True, BLACK); self.screen.blit(img, (panel.x+12,y)); y+=self.font.get_linesize()+2

        for b in self.buttons: b.draw(self.screen)

        # Réglages
        if self.settings_open:
            sr=self.settings_rect
            pygame.draw.rect(self.screen, (250,250,245), sr, border_radius=12)
            pygame.draw.rect(self.screen, (40,40,40), sr, 1, border_radius=12)
            title=self.font_big.render("Réglages — Flèche", True, BLACK)
            self.screen.blit(title, (sr.x+20, sr.y+20))
            for (label, y), inp, sld in [
                (self._rows[0], self.in_speed,  self.sld_speed),
                (self._rows[1], self.in_period, self.sld_period),
                (self._rows[2], self.in_trail,  self.sld_trail),
            ]:
                self.screen.blit(self.font.render(label, True, BLACK), (sr.x+20, y))
                inp.draw(self.screen); sld.draw(self.screen)
            self.btn_apply.draw(self.screen); self.btn_close.draw(self.screen)

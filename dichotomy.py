# dichotomy.py
import pygame
WIDTH, HEIGHT = 980, 560

# Couleurs
WHITE=(255,255,255); BLACK=(18,18,18)
BROWN=(120,70,20); BROWN_DARK=(85,50,15); BROWN_LIGHT=(160,95,30)
BLUE_LINE=(48,140,255)
SKY_TOP=(210,230,255); SKY_BOTTOM=(160,200,255)
GROUND_TOP=(150,200,150); GROUND_BOTTOM=(110,170,110)
LEAF_D1=(70,160,70); LEAF_D2=(50,140,60); LEAF_L1=(120,200,110); LEAF_L2=(100,185,100)

MIN_INTERVAL=40; MAX_INTERVAL=2000; DEFAULT_STEP_INTERVAL_MS=600
APPLE_RADIUS=14; TRUNK_WIDTH=28; TRUNK_HEIGHT=190

def clamp(v, lo, hi): return max(lo, min(hi, v))
def draw_vertical_gradient(surface, rect, color_top, color_bottom):
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h-1)
        c = (int(color_top[0] + (color_bottom[0]-color_top[0])*t),
             int(color_top[1] + (color_bottom[1]-color_top[1])*t),
             int(color_top[2] + (color_bottom[2]-color_top[2])*t))
        pygame.draw.line(surface, c, (x, y+i), (x+w, y+i))

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
        col=(240,240,240); hov=(225,225,225); act=(210,210,210)
        c=act if self._down else (hov if self._hover else col)
        pygame.draw.rect(s, c, self.rect, border_radius=10)
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
        t=clamp((px-self.x)/self.w,0,1)
        if self.N is not None:
            k=int(round(t*self.N)); return self.vmin + k*(self.vmax-self.vmin)/self.N
        return self.vmin + t*(self.vmax-self.vmin)
    def handle_event(self, e):
        changed=False; kx=self._val_to_x()
        knob=pygame.Rect(kx-self.knob_r-3, self.y-self.knob_r-3, 2*(self.knob_r+3), 2*(self.knob_r+3))
        if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
            if knob.collidepoint(e.pos) or pygame.Rect(self.x, self.y-10, self.w, 20).collidepoint(e.pos):
                self.dragging=True; nv=self._snap(self._x_to_val(e.pos[0])); 
                if nv!=self.value: self.value=nv; changed=True
        elif e.type==pygame.MOUSEMOTION and self.dragging:
            nv=self._snap(self._x_to_val(e.pos[0])); 
            if nv!=self.value: self.value=nv; changed=True
        elif e.type==pygame.MOUSEBUTTONUP and e.button==1: self.dragging=False
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
    def set_value(self, v, fmt=None): self.text = (fmt.format(v) if fmt else str(v))
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
        else: self.caret=False; self._blink=0
    def draw(self, s):
        pygame.draw.rect(s, (255,255,255), self.rect, border_radius=8)
        pygame.draw.rect(s, (180,180,180), self.rect, 1, border_radius=8)
        img=self.font.render(self.text if self.text else "", True, BLACK)
        x=self.rect.x+8; y=self.rect.y+(self.rect.h-img.get_height())//2
        s.blit(img, (x,y))
        if self.active and self.caret:
            cx=x+img.get_width()+2
            pygame.draw.line(s, BLACK, (cx, self.rect.y+6), (cx, self.rect.y+self.rect.h-6), 1)

class DichotomyScene:
    def __init__(self, screen, fonts):
        self.screen=screen
        self.font, self.font_small, self.font_big = fonts
        self.ground_y=HEIGHT-90
        self.trunk_rect=pygame.Rect(0,0,TRUNK_WIDTH,TRUNK_HEIGHT); self.trunk_rect.midbottom=(WIDTH-160, self.ground_y)
        self.apple_y=float(self.trunk_rect.centery); self.target_x=float(self.trunk_rect.left)

        # paramètres
        self.chosen_distance=300.0
        self.step_interval=DEFAULT_STEP_INTERVAL_MS
        self.stop_epsilon=0.5
        self.step_ratio=0.50   # pourcentage de distance à chaque étape (0.01..0.99)

        # état
        self.apple_x=self.start_x(); self.auto=False; self.reached=False
        self.step_count=0; self.total_travel=0.0; self.last_step_delta=0.0
        self.last_step_time=pygame.time.get_ticks()
        self.back_to_menu=False

        # UI: fond, feuillage, boutons, réglages
        self.background=pygame.Surface((WIDTH,HEIGHT)); self._render_background(self.background)
        self.foliage_surface=self._render_foliage()
        self._build_top_buttons()
        self.settings_open=False; self._build_settings()

    def _render_background(self, surf):
        draw_vertical_gradient(surf, (0,0,WIDTH,self.ground_y), SKY_TOP, SKY_BOTTOM)
        draw_vertical_gradient(surf, (0,self.ground_y,WIDTH,HEIGHT-self.ground_y), GROUND_TOP, GROUND_BOTTOM)

    def _render_foliage(self):
        cw,ch=220,150; s=pygame.Surface((cw,ch), pygame.SRCALPHA); cx,cy=cw//2, ch//2+10
        for col, r, a in [(LEAF_D2,86,0.55),(LEAF_D1,76,0.45),(LEAF_L2,66,0.35),(LEAF_L1,56,0.25)]:
            colA=(col[0],col[1],col[2], int(255*a))
            for dx,dy,sc in [(-34,-20,1.0),(34,-12,0.96),(-49,12,0.88),(46,16,0.92),(0,0,1.07)]:
                pygame.draw.circle(s, colA, (cx+dx, cy+dy), int(r*sc))
        for dx,dy,r in [(-76,-10,15),(76,-8,13),(0,-32,11),(-34,32,12),(38,28,11)]:
            pygame.draw.circle(s, (255,255,255,30), (cx+dx,cy+dy), r)
        return s

    def _build_top_buttons(self):
        self.buttons=[]
        pad=8; bx=WIDTH-15; by=12; bw,bh=120,34
        def add(label, cb):
            nonlocal bx
            r=pygame.Rect(bx-bw, by, bw, bh); self.buttons.append(Button(r,label,self.font,cb)); bx-=(bw+pad)
        add("Menu (M)", self._go_menu)
        add("Réglages (S)", self._toggle_settings)
        add("Réinit. (R)", self.reset)
        add("Étape (N)", self.step_once)
        add("❚❚/▶ (Espace)", self.toggle_auto)

    def _go_menu(self): self.back_to_menu=True

    # logique
    def start_x(self): return self.target_x - self.chosen_distance
    def steps_per_second(self): return 1000.0/self.step_interval if self.step_interval>0 else 0.0
    def valid_distance_range(self): return 10.0, (self.target_x - (APPLE_RADIUS+12))
    def interval_from_sps(self, sps):
        if sps and sps>0: return clamp(int(round(1000.0/sps)), MIN_INTERVAL, MAX_INTERVAL)
        return self.step_interval
    def remaining(self): return abs(self.target_x - self.apple_x)
    def reset(self):
        self.apple_x=self.start_x(); self.auto=False; self.reached=False
        self.step_count=0; self.total_travel=0.0; self.last_step_delta=0.0
        self.last_step_time=pygame.time.get_ticks()
    def toggle_auto(self):
        if not self.reached:
            self.auto=not self.auto; self.last_step_time=pygame.time.get_ticks()
    def step_once(self):
        if not self.auto: self._step()
    def _step(self):
        if self.reached: return
        px=self.apple_x
        r=self.step_ratio
        self.apple_x = self.apple_x + r*(self.target_x - self.apple_x)
        self.last_step_delta=abs(self.apple_x - px); self.total_travel+=self.last_step_delta; self.step_count+=1
        if self.remaining() <= self.stop_epsilon: self.reached=True

    # réglages
    def _build_settings(self):
        self.settings_rect=pygame.Rect(20,20,640,380)
        base_x=self.settings_rect.x+20; input_w,input_h=160,36; in_x=self.settings_rect.right-20-input_w
        track_w=(in_x-12)-base_x
        top_y=self.settings_rect.y+64; gap=92
        y1=top_y; y2=y1+gap; y3=y2+gap; y4=y3+gap

        dmin,dmax=self.valid_distance_range()
        self.sld_dist=Slider(base_x, y1+input_h+12, track_w, dmin,dmax, self.chosen_distance, step=1.0)
        self.sld_sps =Slider(base_x, y2+input_h+12, track_w, 0.2,20.0, max(0.2,self.steps_per_second()), step=0.1)
        self.sld_eps =Slider(base_x, y3+input_h+12, track_w, 0.01,20.0, max(0.01,self.stop_epsilon), step=0.01)
        self.sld_ratio=Slider(base_x, y4+input_h+12, track_w, 1.0,99.0, self.step_ratio*100.0, step=1.0)

        self.in_dist=TextInput((in_x,y1,input_w,input_h), self.font, f"{self.chosen_distance:.1f}")
        self.in_sps =TextInput((in_x,y2,input_w,input_h), self.font, f"{self.steps_per_second():.2f}")
        self.in_eps =TextInput((in_x,y3,input_w,input_h), self.font, f"{self.stop_epsilon:.2f}")
        self.in_ratio=TextInput((in_x,y4,input_w,input_h), self.font, f"{self.step_ratio*100:.0f}")

        b_w,b_h=120,34; below=self.sld_ratio.y+self.sld_ratio.knob_r+24
        x1=self.settings_rect.right-(b_w+20); x0=x1-(b_w+10); yb=int(below)
        self.btn_apply=Button((x0,yb,b_w,b_h), "Appliquer", self.font, self._apply_settings)
        self.btn_close=Button((x1,yb,b_w,b_h), "Fermer", self.font, self._toggle_settings)
        self.settings_rect.h=(yb+b_h+16)-self.settings_rect.y

        self._rows=[("Distance initiale (px)", y1), ("Vitesse (étapes/s)", y2), ("Distance d'arrêt ε (px)", y3), ("Pas r (%/étape)", y4)]
        self.inputs=[self.in_dist,self.in_sps,self.in_eps,self.in_ratio]; self.focus_idx=-1

    def _toggle_settings(self):
        self.settings_open=not self.settings_open
        if self.settings_open:
            self.auto=False
            dmin,dmax=self.valid_distance_range()
            self.sld_dist.set_range(dmin,dmax,1.0); self.sld_dist.value=clamp(self.chosen_distance, dmin,dmax); self.in_dist.set_value(self.sld_dist.value, "{:.1f}")
            self.sld_sps.set_range(0.2,20.0,0.1); self.sld_sps.value=clamp(self.steps_per_second(),0.2,20.0); self.in_sps.set_value(self.sld_sps.value, "{:.2f}")
            self.sld_eps.set_range(0.01,20.0,0.01); self.sld_eps.value=max(0.01,self.stop_epsilon); self.in_eps.set_value(self.sld_eps.value, "{:.2f}")
            self.sld_ratio.set_range(1.0,99.0,1.0); self.sld_ratio.value=clamp(self.step_ratio*100.0,1.0,99.0); self.in_ratio.set_value(self.sld_ratio.value, "{:.0f}")
            self.focus_idx=-1
            for inp in self.inputs: inp.active=False

    def _apply_settings(self):
        dmin,dmax=self.valid_distance_range()
        dist=self.in_dist.get_value() or self.sld_dist.value; dist=clamp(dist,dmin,dmax)
        sps =self.in_sps.get_value() or self.sld_sps.value; sps=clamp(sps,0.2,20.0)
        eps =self.in_eps.get_value() or self.sld_eps.value; eps=clamp(eps,0.01,1000.0)
        r_pct=self.in_ratio.get_value() or self.sld_ratio.value; r_pct=clamp(r_pct,1.0,99.0)

        self.chosen_distance=dist
        self.step_interval=self.interval_from_sps(sps)
        self.stop_epsilon=eps
        self.step_ratio=r_pct/100.0
        self.reset()
        self.settings_open=False

    # événements / update / draw
    def handle_event(self, e):
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_m or e.key==pygame.K_ESCAPE: self._go_menu()
            elif e.key==pygame.K_SPACE and not self.settings_open: self.toggle_auto()
            elif e.key==pygame.K_n and not self.settings_open: self.step_once()
            elif e.key==pygame.K_r and not self.settings_open: self.reset()
            elif e.key==pygame.K_s: self._toggle_settings()
            elif e.key==pygame.K_TAB and self.settings_open:
                self.focus_idx = 0 if self.focus_idx==-1 else (self.focus_idx+1)%len(self.inputs)
                for i,inp in enumerate(self.inputs): inp.active=(i==self.focus_idx)

        if self.settings_open:
            # sliders -> inputs
            if self.sld_dist.handle_event(e): self.in_dist.set_value(self.sld_dist.value, "{:.1f}")
            if self.sld_sps.handle_event(e): self.in_sps.set_value(self.sld_sps.value, "{:.2f}")
            if self.sld_eps.handle_event(e): self.in_eps.set_value(self.sld_eps.value, "{:.2f}")
            if self.sld_ratio.handle_event(e): self.in_ratio.set_value(self.sld_ratio.value, "{:.0f}")
            # inputs
            committed=False
            if self.in_dist.handle_event(e):
                v=self.in_dist.get_value(); 
                if v is not None: self.sld_dist.value=clamp(v, *self.valid_distance_range())
                committed=True
            if self.in_sps.handle_event(e):
                v=self.in_sps.get_value(); 
                if v is not None and v>0: self.sld_sps.value=clamp(v,0.2,20.0)
                committed=True
            if self.in_eps.handle_event(e):
                v=self.in_eps.get_value(); 
                if v is not None and v>0:
                    self.sld_eps.value=clamp(v,0.01,1000.0); self.in_eps.set_value(self.sld_eps.value, "{:.2f}")
                committed=True
            if self.in_ratio.handle_event(e):
                v=self.in_ratio.get_value(); 
                if v is not None and v>0: self.sld_ratio.value=clamp(v,1.0,99.0)
                committed=True
            if committed: self._apply_settings()

            self.btn_apply.handle_event(e); self.btn_close.handle_event(e)
        else:
            for b in self.buttons: b.handle_event(e)

    def update(self, dt):
        for inp in getattr(self, "inputs", []): inp.update(dt)
        if self.auto and not self.reached and not self.settings_open:
            now=pygame.time.get_ticks()
            if now - self.last_step_time >= self.step_interval:
                self._step(); self.last_step_time=now

    # dessin
    def _draw_trunk(self, s):
        r=self.trunk_rect
        tr=pygame.Surface((r.w,r.h), pygame.SRCALPHA)
        # gradient vertical tronc
        for i in range(r.h):
            t=i/max(1,r.h-1)
            col=(int(BROWN_LIGHT[0]+(BROWN_DARK[0]-BROWN_LIGHT[0])*t),
                 int(BROWN_LIGHT[1]+(BROWN_DARK[1]-BROWN_LIGHT[1])*t),
                 int(BROWN_LIGHT[2]+(BROWN_DARK[2]-BROWN_LIGHT[2])*t))
            pygame.draw.line(tr, col, (0,i),(r.w,i))
        pygame.draw.rect(tr, (255,255,255,25), (0,0,6,r.h))
        pygame.draw.rect(tr, (0,0,0,30), (r.w-6,0,6,r.h))
        s.blit(tr, r.topleft)
        pygame.draw.ellipse(s, (0,0,0,40), (r.centerx-r.w, r.bottom-6, 2*r.w, 12))
        # feuillage
        cx=r.centerx - self.foliage_surface.get_width()//2
        cy=r.top - self.foliage_surface.get_height() + 20
        s.blit(self.foliage_surface, (cx,cy))

    def _draw_apple(self, s):
        x,y=int(self.apple_x), int(self.apple_y)
        shadow=pygame.Surface((APPLE_RADIUS*4, APPLE_RADIUS*4), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0,0,0,70), (APPLE_RADIUS*2, APPLE_RADIUS*2), APPLE_RADIUS+2)
        s.blit(shadow, (x-(APPLE_RADIUS*2)+3, y-(APPLE_RADIUS*2)+3))
        pygame.draw.circle(s, (175,35,35), (x,y), APPLE_RADIUS+2)
        pygame.draw.circle(s, (225,55,55), (x,y), APPLE_RADIUS)
        pygame.draw.circle(s, (255,255,255,160), (x-5,y-5), 5)

    def draw(self):
        self.screen.blit(self.background, (0,0))
        pygame.draw.line(self.screen, (120,160,120), (0,self.ground_y), (WIDTH,self.ground_y), 2)
        self._draw_trunk(self.screen)
        self._draw_apple(self.screen)

        # HUD
        panel=pygame.Rect(16,12,470,196)
        pygame.draw.rect(self.screen, (250,250,245), panel, border_radius=10)
        pygame.draw.rect(self.screen, (40,40,40), panel, 1, border_radius=10)
        lines=[
            f"Dichotomie — Mode: {'AUTO' if self.auto else 'PAUSE'}",
            f"Étapes: {self.step_count}",
            f"Distance initiale: {self.chosen_distance:.1f}px",
            f"Distance parcourue (étape): {self.last_step_delta:.3f}px",
            f"Distance parcourue (totale): {self.total_travel:.3f}px",
            f"Distance restante: {self.remaining():.3f}px",
            f"Vitesse: {self.steps_per_second():.2f} étapes/s (Δ: {self.step_interval} ms)",
            f"Pas r: {self.step_ratio*100:.0f}%  •  ε (arrêt): {self.stop_epsilon:.2f}px",
            "Raccourcis: Espace/N/R/S/M"
        ]
        y=panel.y+10
        for t in lines:
            img=self.font.render(t, True, BLACK); self.screen.blit(img, (panel.x+12, y)); y+=self.font.get_linesize()+2

        for b in self.buttons: b.draw(self.screen)
        pygame.draw.line(self.screen, BLUE_LINE, (int(self.apple_x), int(self.apple_y)), (int(self.target_x), int(self.apple_y)), 2)

        if self.reached:
            msg=pygame.Rect(16, panel.bottom+10, 520, 64)
            pygame.draw.rect(self.screen, (255,250,220), msg, border_radius=10)
            pygame.draw.rect(self.screen, (40,40,40), msg, 1, border_radius=10)
            txt=[
                "Fin: seuil d'arrêt atteint.",
                f"Étapes: {self.step_count} | d_totale: {self.total_travel:.3f}px | d_restante: {self.remaining():.3f}px"
            ]
            yy=msg.y+10
            for t in txt:
                img=self.font.render(t, True, BLACK); self.screen.blit(img, (msg.x+12, yy)); yy+=self.font.get_linesize()+2

        if self.settings_open:
            sr=self.settings_rect
            pygame.draw.rect(self.screen, (250,250,245), sr, border_radius=12)
            pygame.draw.rect(self.screen, (40,40,40), sr, 1, border_radius=12)
            title=self.font_big.render("Réglages — Dichotomie", True, BLACK)
            self.screen.blit(title, (sr.x+20, sr.y+20))
            for (label, y), inp, sld in [
                (self._rows[0], self.in_dist, self.sld_dist),
                (self._rows[1], self.in_sps,  self.sld_sps),
                (self._rows[2], self.in_eps,  self.sld_eps),
                (self._rows[3], self.in_ratio,self.sld_ratio),
            ]:
                self.screen.blit(self.font.render(label, True, BLACK), (sr.x+20, y))
                inp.draw(self.screen); sld.draw(self.screen)
            self.btn_apply.draw(self.screen); self.btn_close.draw(self.screen)

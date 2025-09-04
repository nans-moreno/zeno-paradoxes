"""
Simulation du paradoxe d'Achille et la Tortue de Zénon
Version graphique améliorée avec Pygame
"""

import sys
import math
import random

def simulation_pygame():
    """Version graphique améliorée avec Pygame"""
    try:
        import pygame
        import pygame_gui
    except ImportError:
        print("Pygame ou pygame_gui n'est pas installé. Installez-les avec: pip install pygame pygame_gui")
        return
    
    pygame.init()
    
    # Constantes
    LARGEUR = 1200
    HAUTEUR = 700
    FPS = 60
    
    # Palette de couleurs moderne
    BLANC = (255, 255, 255)
    NOIR = (20, 20, 20)
    ROUGE = (231, 76, 60)
    VERT = (46, 204, 113)
    BLEU = (52, 152, 219)
    GRIS = (149, 165, 166)
    GRIS_CLAIR = (236, 240, 241)
    JAUNE = (241, 196, 15)
    VIOLET = (155, 89, 182)
    FOND = (245, 245, 250)
    
    # Configuration de la fenêtre
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Paradoxe d'Achille et la Tortue - Simulation Interactive")
    horloge = pygame.time.Clock()
    
    # Charger les polices
    pygame.font.init()
    font_titre = pygame.font.Font(None, 48)
    font_normal = pygame.font.Font(None, 32)
    font_petit = pygame.font.Font(None, 24)
    
    # Variables par défaut
    distance_parcourue = 900.0
    avance_tortue = 300.0
    vitesse_achille = 250.0
    vitesse_tortue = 100.0
    
    # Classe pour les particules
    class Particule:
        def __init__(self, x, y, couleur):
            self.x = x
            self.y = y
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(-5, -2)
            self.couleur = couleur
            self.vie = 30
            self.taille = random.randint(2, 5)
        
        def update(self):
            self.x += self.vx
            self.y += self.vy
            self.vy += 0.2  # Gravité
            self.vie -= 1
            self.taille = max(1, self.taille - 0.1)
        
        def draw(self, surface):
            if self.vie > 0:
                alpha = int(255 * (self.vie / 30))
                couleur = (*self.couleur, alpha)
                pygame.draw.circle(surface, self.couleur[:3], 
                                 (int(self.x), int(self.y)), 
                                 int(self.taille))
    
    particules = []
    
    # Menu de configuration amélioré
    def menu_configuration():
        nonlocal distance_parcourue, avance_tortue, vitesse_achille, vitesse_tortue
        
        manager = pygame_gui.UIManager((LARGEUR, HAUTEUR), 
                                      theme_path=None)
        clock = pygame.time.Clock()
        
        # Créer un panneau central
        panel_largeur = 500
        panel_hauteur = 450
        panel_x = (LARGEUR - panel_largeur) // 2
        panel_y = (HAUTEUR - panel_hauteur) // 2
        
        # Champs de saisie avec style
        input_distance = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((panel_x + 250, panel_y + 80), (180, 40)), 
            manager=manager)
        input_distance.set_text(str(int(distance_parcourue)))
        
        input_avance = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((panel_x + 250, panel_y + 150), (180, 40)), 
            manager=manager)
        input_avance.set_text(str(int(avance_tortue)))
        
        input_vitesse_achille = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((panel_x + 250, panel_y + 220), (180, 40)), 
            manager=manager)
        input_vitesse_achille.set_text(str(int(vitesse_achille)))
        
        input_vitesse_tortue = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((panel_x + 250, panel_y + 290), (180, 40)), 
            manager=manager)
        input_vitesse_tortue.set_text(str(int(vitesse_tortue)))
        
        # Bouton pour démarrer avec style
        bouton_demarrer = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((LARGEUR // 2 - 75, panel_y + 370), (150, 50)),
            text="DÉMARRER",
            manager=manager)
        
        # Animation de fond
        etoiles = [(random.randint(0, LARGEUR), random.randint(0, HAUTEUR)) 
                   for _ in range(50)]
        
        en_menu = True
        animation_time = 0
        
        while en_menu:
            temps_delta = clock.tick(FPS) / 1000.0
            animation_time += temps_delta
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == bouton_demarrer:
                        try:
                            distance_parcourue = float(input_distance.get_text())
                            avance_tortue = float(input_avance.get_text())
                            vitesse_achille = float(input_vitesse_achille.get_text())
                            vitesse_tortue = float(input_vitesse_tortue.get_text())
                            
                            # Validation des valeurs
                            if vitesse_achille <= vitesse_tortue:
                                print("Achille doit être plus rapide que la tortue!")
                                continue
                            if avance_tortue >= distance_parcourue:
                                print("L'avance de la tortue doit être inférieure à la distance totale!")
                                continue
                                
                            en_menu = False
                        except ValueError:
                            print("Veuillez entrer des valeurs numériques valides.")
                            continue
                
                manager.process_events(event)
            
            manager.update(temps_delta)
            
            # Dessiner le fond
            ecran.fill(FOND)
            
            # Dessiner les étoiles animées
            for i, (x, y) in enumerate(etoiles):
                taille = 1 + math.sin(animation_time * 2 + i) * 0.5
                pygame.draw.circle(ecran, GRIS_CLAIR, (x, y), int(taille))
            
            # Dessiner le panneau de configuration
            panneau = pygame.Surface((panel_largeur, panel_hauteur))
            panneau.set_alpha(240)
            panneau.fill(BLANC)
            ecran.blit(panneau, (panel_x, panel_y))
            
            # Bordure du panneau
            pygame.draw.rect(ecran, BLEU, 
                           (panel_x, panel_y, panel_largeur, panel_hauteur), 3)
            
            # Titre
            titre = font_titre.render("CONFIGURATION", True, BLEU)
            titre_rect = titre.get_rect(center=(LARGEUR // 2, panel_y + 30))
            ecran.blit(titre, titre_rect)
            
            # Labels
            labels = [
                ("Distance totale (px):", panel_y + 85),
                ("Avance tortue (px):", panel_y + 155),
                ("Vitesse Achille (px/s):", panel_y + 225),
                ("Vitesse tortue (px/s):", panel_y + 295)
            ]
            
            for texte, y in labels:
                label = font_petit.render(texte, True, NOIR)
                ecran.blit(label, (panel_x + 50, y))
            
            # Dessiner l'interface
            manager.draw_ui(ecran)
            
            # Petit texte d'information
            info = font_petit.render("Le paradoxe de Zénon - Achille ne rattrapera jamais la tortue... ou presque!", 
                                    True, GRIS)
            info_rect = info.get_rect(center=(LARGEUR // 2, HAUTEUR - 30))
            ecran.blit(info, info_rect)
            
            pygame.display.update()
    
    # Appeler le menu de configuration
    menu_configuration()
    
    # Variables de la simulation
    position_achille = 100.0
    position_tortue = 100.0 + avance_tortue
    temps_total = 0.0
    simulation_active = False
    simulation_terminee = False
    moment_depassement = None
    distance_depassement = None
    
    # Historique des positions pour tracer les trajectoires
    historique_achille = []
    historique_tortue = []
    
    # Variables pour l'animation
    animation_time = 0
    flash_alpha = 0
    
    def dessiner_coureur(surface, x, y, couleur, nom, est_achille=True):
        """Dessine un coureur avec style"""
        # Ombre
        pygame.draw.circle(surface, (0, 0, 0, 50), (int(x) + 2, y + 2), 18)
        
        # Corps principal
        pygame.draw.circle(surface, couleur, (int(x), y), 16)
        
        # Effet de brillance
        pygame.draw.circle(surface, BLANC, (int(x) - 5, y - 5), 5)
        
        # Bordure
        pygame.draw.circle(surface, NOIR, (int(x), y), 16, 2)
        
        # Nom avec ombre
        font = pygame.font.Font(None, 26)
        text_shadow = font.render(nom, True, (0, 0, 0, 128))
        text = font.render(nom, True, couleur)
        surface.blit(text_shadow, (x - 30 + 1, y - 45 + 1))
        surface.blit(text, (x - 30, y - 45))
        
        # Effet de mouvement (petites lignes derrière)
        if simulation_active and not simulation_terminee:
            for i in range(3):
                alpha = 100 - i * 30
                ligne_x = x - (i + 1) * 10
                pygame.draw.line(surface, (*couleur, alpha), 
                               (ligne_x, y - 5), (ligne_x - 5, y), 2)
                pygame.draw.line(surface, (*couleur, alpha), 
                               (ligne_x, y + 5), (ligne_x - 5, y), 2)
    
    def dessiner_piste(surface):
        """Dessine une piste de course améliorée"""
        y_piste = HAUTEUR // 2
        
        # Fond de la piste
        pygame.draw.rect(surface, (220, 220, 220), 
                        (0, y_piste - 80, LARGEUR, 160))
        
        # Lignes de la piste
        for i in range(0, LARGEUR, 50):
            if i % 100 == 0:
                pygame.draw.line(surface, GRIS, (i, y_piste - 70), (i, y_piste + 70), 1)
        
        # Bordures de la piste
        pygame.draw.line(surface, NOIR, (0, y_piste - 80), (LARGEUR, y_piste - 80), 3)
        pygame.draw.line(surface, NOIR, (0, y_piste + 80), (LARGEUR, y_piste + 80), 3)
        
        # Ligne de départ
        for i in range(0, 160, 20):
            color = BLANC if (i // 20) % 2 == 0 else NOIR
            pygame.draw.rect(surface, color, (95, y_piste - 80 + i, 10, 20))
        
        # Ligne d'arrivée
        for i in range(0, 160, 20):
            for j in range(0, 20, 20):
                color = BLANC if ((i + j) // 20) % 2 == 0 else NOIR
                pygame.draw.rect(surface, color, 
                               (distance_parcourue - 5 + j, y_piste - 80 + i, 20, 20))
        
        # Labels
        font = pygame.font.Font(None, 24)
        depart_text = font.render("DÉPART", True, NOIR)
        arrivee_text = font.render("ARRIVÉE", True, NOIR)
        surface.blit(depart_text, (60, y_piste - 110))
        surface.blit(arrivee_text, (distance_parcourue - 40, y_piste - 110))
    
    def afficher_statistiques(surface):
        """Affiche les statistiques de la course"""
        # Panneau de statistiques
        panneau = pygame.Surface((350, 180))
        panneau.set_alpha(230)
        panneau.fill(BLANC)
        surface.blit(panneau, (10, 10))
        pygame.draw.rect(surface, BLEU, (10, 10, 350, 180), 2)
        
        # Titre du panneau
        titre = font_normal.render("STATISTIQUES", True, BLEU)
        surface.blit(titre, (20, 20))
        
        # Informations
        infos = [
            f"Temps: {temps_total:.2f}s",
            f"Position Achille: {position_achille:.0f}px",
            f"Position Tortue: {position_tortue:.0f}px",
            f"Distance restante: {max(0, position_tortue - position_achille):.0f}px"
        ]
        
        for i, info in enumerate(infos):
            text = font_petit.render(info, True, NOIR)
            surface.blit(text, (20, 55 + i * 30))
        
        # Barre de progression
        progress_achille = min(1, (position_achille - 100) / (distance_parcourue - 100))
        progress_tortue = min(1, (position_tortue - 100 - avance_tortue) / (distance_parcourue - 100 - avance_tortue))
        
        pygame.draw.rect(surface, GRIS_CLAIR, (20, 165, 320, 10))
        pygame.draw.rect(surface, ROUGE, (20, 165, int(320 * progress_achille), 10))
        pygame.draw.rect(surface, NOIR, (20, 165, 320, 10), 1)
    
    # Boucle principale
    en_cours = True
    while en_cours:
        dt = horloge.tick(FPS) / 1000.0
        animation_time += dt
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not simulation_terminee:
                    simulation_active = not simulation_active
                elif event.key == pygame.K_r:
                    # Réinitialisation complète
                    position_achille = 100.0
                    position_tortue = 100.0 + avance_tortue
                    temps_total = 0.0
                    historique_achille.clear()
                    historique_tortue.clear()
                    particules.clear()
                    simulation_active = False
                    simulation_terminee = False
                    moment_depassement = None
                    distance_depassement = None
                    flash_alpha = 0
                elif event.key == pygame.K_ESCAPE:
                    en_cours = False
        
        # Mise à jour de la simulation
        if simulation_active and not simulation_terminee:
            if position_achille < distance_parcourue and position_tortue < distance_parcourue + 100:
                # Mise à jour des positions
                position_achille += vitesse_achille * dt
                position_tortue += vitesse_tortue * dt
                temps_total += dt
                
                # Ajouter à l'historique (échantillonnage pour optimisation)
                if len(historique_achille) == 0 or \
                   abs(historique_achille[-1][0] - position_achille) > 5:
                    historique_achille.append((position_achille, HAUTEUR // 2 - 20))
                    historique_tortue.append((position_tortue, HAUTEUR // 2 + 20))
                
                # Vérifier le dépassement
                if position_achille >= position_tortue and moment_depassement is None:
                    moment_depassement = temps_total
                    distance_depassement = position_achille
                    simulation_terminee = True
                    flash_alpha = 255
                    
                    # Créer des particules de célébration
                    for _ in range(30):
                        particules.append(Particule(position_achille, HAUTEUR // 2, JAUNE))
                        particules.append(Particule(position_achille, HAUTEUR // 2, ROUGE))
        
        # Mise à jour des particules
        for p in particules[:]:
            p.update()
            if p.vie <= 0:
                particules.remove(p)
        
        # Diminuer l'effet de flash
        if flash_alpha > 0:
            flash_alpha = max(0, flash_alpha - 5)
        
        # Affichage
        ecran.fill(FOND)
        
        # Grille de fond
        for x in range(0, LARGEUR, 50):
            pygame.draw.line(ecran, (230, 230, 230), (x, 0), (x, HAUTEUR), 1)
        for y in range(0, HAUTEUR, 50):
            pygame.draw.line(ecran, (230, 230, 230), (0, y), (LARGEUR, y), 1)
        
        dessiner_piste(ecran)
        
        # Dessiner les trajectoires avec dégradé
        if len(historique_achille) > 1:
            for i in range(len(historique_achille) - 1):
                alpha = int(255 * (i / len(historique_achille)))
                pygame.draw.line(ecran, ROUGE, 
                               historique_achille[i], historique_achille[i + 1], 3)
        
        if len(historique_tortue) > 1:
            for i in range(len(historique_tortue) - 1):
                alpha = int(255 * (i / len(historique_tortue)))
                pygame.draw.line(ecran, VERT, 
                               historique_tortue[i], historique_tortue[i + 1], 3)
        
        # Dessiner les particules
        for p in particules:
            p.draw(ecran)
        
        # Dessiner les coureurs
        dessiner_coureur(ecran, position_achille, HAUTEUR // 2 - 20, ROUGE, "Achille", True)
        dessiner_coureur(ecran, position_tortue, HAUTEUR // 2 + 20, VERT, "Tortue", False)
        
        # Afficher les statistiques
        afficher_statistiques(ecran)
        
        # Instructions
        panneau_instructions = pygame.Surface((280, 120))
        panneau_instructions.set_alpha(230)
        panneau_instructions.fill(BLANC)
        ecran.blit(panneau_instructions, (LARGEUR - 290, 10))
        pygame.draw.rect(ecran, GRIS, (LARGEUR - 290, 10, 280, 120), 2)
        
        instructions = [
            "COMMANDES",
            "",
            "ESPACE : Démarrer/Pause",
            "R : Réinitialiser",
            "ESC : Quitter"
        ]
        
        for i, instruction in enumerate(instructions):
            couleur = BLEU if i == 0 else NOIR
            font_inst = font_petit if i > 0 else font_normal
            texte_inst = font_inst.render(instruction, True, couleur)
            ecran.blit(texte_inst, (LARGEUR - 280, 20 + i * 22))
        
        # Effet de flash si dépassement
        if flash_alpha > 0:
            flash_surface = pygame.Surface((LARGEUR, HAUTEUR))
            flash_surface.set_alpha(flash_alpha)
            flash_surface.fill(JAUNE)
            ecran.blit(flash_surface, (0, 0))
        
        # Message de fin
        if simulation_terminee:
            # Panneau de victoire
            panneau_victoire = pygame.Surface((600, 200))
            panneau_victoire.set_alpha(240)
            panneau_victoire.fill(BLANC)
            ecran.blit(panneau_victoire, (LARGEUR // 2 - 300, HAUTEUR // 2 - 100))
            pygame.draw.rect(ecran, JAUNE, 
                           (LARGEUR // 2 - 300, HAUTEUR // 2 - 100, 600, 200), 4)
            
            # Textes de victoire
            texte_victoire = font_titre.render("ACHILLE A DÉPASSÉ LA TORTUE!", True, ROUGE)
            texte_victoire_rect = texte_victoire.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 40))
            ecran.blit(texte_victoire, texte_victoire_rect)
            
            if moment_depassement:
                texte_temps = font_normal.render(f"Temps: {moment_depassement:.2f} secondes", True, NOIR)
                texte_temps_rect = texte_temps.get_rect(center=(LARGEUR // 2, HAUTEUR // 2))
                ecran.blit(texte_temps, texte_temps_rect)
                
                texte_distance = font_normal.render(f"Distance: {distance_depassement:.0f} pixels", True, NOIR)
                texte_distance_rect = texte_distance.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 35))
                ecran.blit(texte_distance, texte_distance_rect)
            
            texte_reset = font_petit.render("Appuyez sur R pour recommencer", True, GRIS)
            texte_reset_rect = texte_reset.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 70))
            ecran.blit(texte_reset, texte_reset_rect)
        
        # État de la simulation
        if not simulation_active and not simulation_terminee:
            texte_pause = font_normal.render("PAUSE - Appuyez sur ESPACE pour démarrer", True, BLEU)
            texte_pause_rect = texte_pause.get_rect(center=(LARGEUR // 2, HAUTEUR - 50))
            
            # Effet de pulsation
            scale = 1 + math.sin(animation_time * 3) * 0.05
            texte_pause = pygame.transform.rotozoom(texte_pause, 0, scale)
            texte_pause_rect = texte_pause.get_rect(center=(LARGEUR // 2, HAUTEUR - 50))
            ecran.blit(texte_pause, texte_pause_rect)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    simulation_pygame()
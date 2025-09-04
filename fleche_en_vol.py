# Position initiale
pos = 0

# Vitesse (m/s)
vitesse = 5

# Durée totale de la simulation
temps_total = 5

# Pas de temps
durée_total = 1   # TODO : essayer 1 puis 0.01

temps = 0
while temps < temps_total:
    pos += vitesse * durée_total
    temps += durée_total
    print(f"pos={pos}, temps={temps}, durée_total={durée_total}")

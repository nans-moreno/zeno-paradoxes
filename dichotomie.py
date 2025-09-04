# Distance totale
distance = 8
reste = distance
parcouru = 0
etape = 0

while reste > 0.01:
    demi = reste / 2   # TODO : calculer la moitié du reste
    parcouru += demi
    reste -= demi
    etape += 1
    print(f"Étape {etape} : parcouru = {parcouru}, reste = {reste}")

print(etape)

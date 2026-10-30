def anzahlzeichen(wort):
    x = 0
    for i in wort.split("-"):
        x+=1
    return x

print(anzahlzeichen("mu-al-lid"))

['mu', 'al', 'lid']
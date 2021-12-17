# hur funktioner beskrivs:
# konstanter => (5, 0)
# termer => (5, -3)
# t0 => koefficienten för termen, t1 => variabeln, t2 => exponenten till variabeln
# funktion: (5, -3) + (7, 1) + (-19, 0)

# funktion som deriverar
def derivera(function:list):

    derv_funktion= []

    for count, t in enumerate(function):
        k = t[0]
        gradtal = t[1]

        new_k = k * gradtal
        new_g = gradtal - 1

        derv_funktion.append((new_k, new_g))

    print(f'deriverad funk: {derv_funktion}')
    return derv_funktion


def kalk_funk(funktion:list, x):

    terms = []

    for t in funktion:
        k = t[0]
        e = t[1]

        value = k*(x**e)
        terms.append(value)
    print(f'kalkulation: funk={funktion}, x-värde: {x} summa:{sum(terms)}')

    return sum(terms)


def main():

    gradtal = int(input("Ekvationens gradtal: "))

    funktion = []

    for i in range(gradtal):
        k = float(input(f"Koefficientet till x^{gradtal-i}: "))
        funktion.append((k, gradtal-i))

    funktion.append((float(input('Funktionens konstant: ')), 0))

    närmevärde = float(input("Närmevärde till funktionens nollställe: "))
    print('\n')

    # räknar ut nollställen till 5 decimalers noggrannhet
    x = närmevärde
    old_res = None
    lösningar = []
    while True:

        resultat = x - (kalk_funk(funktion=funktion, x=x) / kalk_funk(derivera(funktion), x))

        if not old_res:
            x = resultat
            old_res = resultat
            print(f'X = {resultat}')
        elif round(old_res, 5) == round(resultat, 5):
            print(f'Hittade nollställe, X={resultat}')
            lösningar.append(resultat)
            break
        else:

            x = resultat
            old_res = resultat
            print(f'X = {resultat}')

    # testa svaret, fungerar inte riktigt p.g.a. Pythons avrundningsfunktion
    if test := round(kalk_funk(funktion=funktion, x=resultat) != 0):
        print(f"\n\nTestet MISSLYCKADES, data: \nY = {test}\n~X = {round(old_res, 5)}")
    else:
        print(f"\n\nTest lyckades, data: \nY = {test}\n~X = {round(old_res, 5)}")



if __name__ == '__main__':
    main()
import sqlite3
import logging
import queue
import multiprocessing

# hur funktioner beskrivs:
# konstanter => (5, 0)
# termer => (5, -3)
# t0 => koefficienten för termen, t1 => variabeln, t2 => exponenten till variabeln
# funktion: (5, -3) + (7, 1) + (-19, 0)

# funktion som deriverar
def derivera(function: list):
    derv_funktion = []

    for count, t in enumerate(function):
        k = t[0]
        gradtal = t[1]

        new_k = k * gradtal
        new_g = gradtal - 1

        derv_funktion.append((new_k, new_g))

    # print(f'deriverad funk: {derv_funktion}')
    return derv_funktion


def kalk_funk(funktion: list, x):
    terms = []

    for t in funktion:
        k = t[0]
        e = t[1]

        value = k * (x ** e)
        terms.append(value)
    # print(f'kalkulation: funk={funktion}, x-värde: {x} summa:{sum(terms)}')

    return sum(terms)


# Räkna ut nollställe
def algoritm(funktion:list, noggrannhet:int, startvärde:float):

    x = startvärde
    old_res = None
    while True:

        try:
            resultat = x - (kalk_funk(funktion=funktion, x=x) / kalk_funk(derivera(funktion), x))
        except ZeroDivisionError:
            print(f'Hittade extrempunkt, X = {x}')
            print(f'Proces terminerar sig själv!')
            exit()

        if not old_res:
            x = resultat
            old_res = resultat
        elif round(old_res, noggrannhet) == round(resultat, noggrannhet):
            print(f'Hittade nollställe: X = {resultat}')
            break
        else:

            x = resultat
            old_res = resultat
            # print(f'X = {resultat}')


def main():

    # # meny för funktionsinmatning
    # konstruera funktion
    gradtal = int(input("Ekvationens gradtal: "))

    funktion = []

    for i in range(gradtal):
        k = float(input(f"Koefficientet till x^{gradtal - i}: "))
        funktion.append((k, gradtal - i))

    funktion.append((float(input('Konstant: ')), 0))

    # marginal & inställningar
    marginal = int(input('Absolut marginal: '))

    prcs_max = int(input('Maximalt jämnt-antal processer: '))

    noggrannhet = int(input('Noggrannhet, antal decimaler: '))

    # # multiprocesser
    for i in range(int(prcs_max/2)):

        prcs1 = multiprocessing.Process(target=algoritm, args=(funktion, noggrannhet, ((-marginal/(2*prcs_max))*(i+1))))
        prcs2 = multiprocessing.Process(target=algoritm, args=(funktion, noggrannhet, ((marginal/(2*prcs_max))*(i+1))))

        prcs1.start()
        prcs2.start()

    prcs1.join()
    prcs2.join()

    print('Done!')


if __name__ == '__main__':
    main()

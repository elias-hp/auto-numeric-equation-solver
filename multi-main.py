# TODO: Add graphics
import queue
import multiprocessing
from configparser import ConfigParser
import time

# TODO: Documentation
# hur funktioner beskrivs:
# konstanter => (5, 0)
# termer => (5, -3)
# t0 => koefficienten för termen, t1 => variabeln, t2 => exponenten till variabeln
# funktion: (5, -3) + (7, 1) + (-19, 0)


# construct polynomial function from configuration file string
# TODO: Shorten
def construct_polynomial(polynomial_str: str) -> list:
    # format raw list w. string tuples
    raw_list = list(polynomial_str.strip('[]').split('\\'))

    # format tuples of koefficient & exponent
    polynomial = []
    for t in raw_list:
        raw_t = eval(t)
        polynomial.append((float(raw_t[0]), float(raw_t[1])))

    return polynomial


# funktion som deriverar
# TODO: Shorten
def derivera(function: list):
    derv_funktion = []

    for count, t in enumerate(function):
        k = t[0]
        gradtal = t[1]

        new_k = k * gradtal
        new_g = gradtal - 1

        derv_funktion.append((new_k, new_g))

    return derv_funktion


# TODO: Shorten
def kalk_funk(funktion: list, x):
    terms = []

    for t in funktion:
        k = t[0]
        e = t[1]

        value = k * (x ** e)
        terms.append(value)

    return sum(terms)


# Räkna ut nollställe
# TODO: Add logging of calculations
# TODO: Recognize already found solutions & skip logg/save
# TODO: Recognize already searched areas
# TODO: Handle polynomials w.o. solutions
def algoritm(funktion: list, noggrannhet: int, startvärde: float, solution_queue: queue.Queue, status_queue: queue.Queue):
    x = startvärde
    old_res = None
    while True:

        # try numerical equation
        try:
            resultat = x - (kalk_funk(funktion=funktion, x=x) / kalk_funk(derivera(funktion), x))
        except ZeroDivisionError:  # division by zero => extreme value
            status_queue.put(1)
            exit()      # exit when extrem value, otherwise it crashes

        # first run of algorithm
        if not old_res:
            x = resultat
            old_res = resultat

        # if found solution
        elif round(old_res, noggrannhet) == round(resultat, noggrannhet):
            solution_queue.put(round(resultat, noggrannhet))
            status_queue.put(1)
            break

        # no passable solution found
        else:
            x = resultat
            old_res = resultat


# TODO: Print all solutions
# TODO: Terminate algorithms when all solutions found
def communicator(solution_queue: queue.Queue, polynomial: list, comm_queue: queue.Queue, status_queue: queue.Queue, prcs_max):
    solutions = []
    completed_prcs = []

    # Determine max solutions
    max_solutions = max(polynomial, key=lambda item: item[1])[1]

    # active role
    while True:

        # send kill flag & print when all possible solutions found
        if len(solutions) == max_solutions:
            comm_queue.put(1)
            break

        # send kill flag & print when all available solutions found => all prcs done
        elif not status_queue.empty():
            completed_prcs.append(status_queue.get())
            if len(completed_prcs) == prcs_max:
                comm_queue.put(2)
                break

        # handle new solutions
        elif not solution_queue.empty():
            new_x = solution_queue.get()
            found = False

            # search if solution already saved
            for x in solutions:
                if x == new_x:
                    found = True

            # save new solution
            if not found:
                solutions.append(new_x)

    print(f'\nAll solutions found, X = {solutions}')


def main():
    # # Settings & function-construction
    if input('Use configuration-file? y/n ') == 'y':

        # Read config file & apply settings
        config = ConfigParser()
        config.read('config.ini')

        # construct function
        funktion = construct_polynomial(config.get('SETTINGS', 'polynomial'))
        marginal = int(config.get('SETTINGS', 'margin'))
        prcs_max = int(config.get('SETTINGS', 'prcs_max'))
        noggrannhet = int(config.get('SETTINGS', 'accuracy'))

    else:
        # meny för funktionsinmatning
        # konstruera funktion
        gradtal = int(input("Ekvationens gradtal: "))

        funktion = []

        for i in range(gradtal):
            k = float(input(f"Koefficienten till x^{gradtal - i}: "))
            funktion.append((k, gradtal - i))

        funktion.append((float(input('Konstant: ')), 0))

        # marginal & inställningar
        marginal = int(input('Marginal (positiv X): '))

        prcs_max = int(input('Maximalt jämnt-antal processer: '))

        noggrannhet = int(input('Noggrannhet, antal decimaler: '))

    # # Misc
    # start timer
    program_start = time.time()

    # Queues
    solution_queue = multiprocessing.Queue()
    comm_queue = multiprocessing.Queue()
    status_queue = multiprocessing.Queue()

    # # multiprocesser
    # TODO: Analyse area in which there could be a solution

    program_prcs_starting = time.time()

    prcs_list = []
    for i in range(int(prcs_max/2)):
        prcs1 = multiprocessing.Process(target=algoritm,
                                args=(funktion, noggrannhet, ((-marginal / (2 * prcs_max)) * (i + 1)), solution_queue, status_queue))
        prcs2 = multiprocessing.Process(target=algoritm,
                                args=(funktion, noggrannhet, ((marginal / (2 * prcs_max)) * (i + 1)), solution_queue, status_queue))
        prcs_list.append(prcs1)
        prcs_list.append(prcs2)

    # start communicator process
    comm = multiprocessing.Process(target=communicator, args=(solution_queue, funktion, comm_queue, status_queue, prcs_max))
    comm.start()

    program_calculation_start = time.time()

    # start all processes
    # TODO: move to thread or something...
    for j, prcs in enumerate(prcs_list):
        prcs.start()

    program_prcs_started = time.time()

    # TODO: Stop this from being hindered by function starter

    while True:
        if not comm_queue.empty():
            flag = comm_queue.get()
            if flag == 1:
                program_calculation_complete = time.time()
                for prcs in prcs_list:
                    prcs.kill()
                break

            if flag == 2:
                print(2)
                program_calculation_complete = time.time()
                break

    # join all processes
    for prcs in prcs_list:
        prcs.join()
        comm.join()

    # TODO: Add tests

    program_end = time.time()

    print('\n--------- STATISTICS  ------------------- ')
    print(f'Multiprocessors begin starting: {round(program_prcs_starting - program_start, 4)}')
    print(f'Multiprocessors started: {round(program_prcs_started - program_start, 4)}')
    print(f'Multiprocessors starting sequence time: {round(program_prcs_started - program_prcs_starting, 4)}')

    print(f'\nCalculation time: {round(program_end - program_calculation_start, 4)}')
    print(f'Full capacity calculation time: {round(program_end - program_prcs_started, 4)}')

    print(f'\nCalculations complete: {round(program_calculation_complete - program_start, 4)}')
    print(f'Calculation to solution time : {round(program_calculation_complete - program_calculation_start, 4)}')
    print(f'Full capacity calculation to solution time : {round(program_calculation_complete - program_prcs_started, 4)}')

    print(f'\nProgram execution sequence: {round(program_end - program_start, 4)}')


if __name__ == '__main__':
    main()

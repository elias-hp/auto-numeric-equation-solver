# TODO: Add graphics
import queue
import multiprocessing
from configparser import ConfigParser
import time


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
# TODO: understand how my equation really works, like why does it move zig zag when no solution
# TODO: Add logging of calculations
# TODO: Recognize already searched areas + Recognize already found solutions & skip logg/save
# TODO: Handle polynomials w.o. solutions
def algoritm(funktion: list, noggrannhet: int, startvärde: float,
             solution_queue: queue.Queue, status_queue: queue.Queue):
    x = startvärde
    old_res = None
    while True:

        # try numerical equation
        try:
            resultat = x - (kalk_funk(funktion=funktion, x=x) / kalk_funk(derivera(funktion), x))

        except ZeroDivisionError:  # division by zero => extreme value
            status_queue.put(1)
            exit()  # exit when extrem value, otherwise it crashes

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


# TODO: Communicate how program ended: All solution for degree found, processors end or time end
def communicator(solution_queue: queue.Queue, polynomial: list, comm_queue: queue.Queue,
                 status_queue: queue.Queue, prcs_max, prcs_queue: queue.Queue):
    solutions = []
    completed_prcs = []

    # Determine max solutions
    max_solutions = max(polynomial, key=lambda item: item[1])[1]

    # active role
    while True:

        # send kill flag & print when all possible solutions found
        if len(solutions) == max_solutions:
            comm_queue.put(1)

            # killing all algorithm-processes
            while not prcs_queue.empty():
                prcs = prcs_queue.get()
                prcs.kill()
            print('Killed algorithm-processes')

            break

        # send kill flag & print when all available solutions found => all prcs done
        elif not status_queue.empty():
            completed_prcs.append(status_queue.get())
            if len(completed_prcs) == prcs_max:
                comm_queue.put(1)
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


# TODO: rename swedish variables to english
def main():
    # # Settings & function-construction
    if input('Use configuration-file? y/n ').lower() == 'y':

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
    prcs_queue = multiprocessing.Queue()

    # # multiprocesser
    # TODO: Analyse area in which there could be a solution

    program_prcs_starting = time.time()

    prcs_list = []
    for i in range(int(prcs_max / 2)):
        prcs1 = multiprocessing.Process(target=algoritm,
                                        args=(funktion, noggrannhet, ((-marginal / (2 * prcs_max)) * (i + 1)),
                                              solution_queue, status_queue))
        prcs2 = multiprocessing.Process(target=algoritm,
                                        args=(funktion, noggrannhet, ((marginal / (2 * prcs_max)) * (i + 1)),
                                              solution_queue, status_queue))
        prcs_list.append(prcs1)
        prcs_list.append(prcs2)

    # start communicator process
    comm = multiprocessing.Process(target=communicator, args=(solution_queue, funktion, comm_queue,
                                                              status_queue, prcs_max, prcs_queue))
    comm.start()

    program_calculation_start = time.time()

    # start all processes
    started_prcs = []
    all_started = True
    for j, prcs in enumerate(prcs_list):
        # stop starting prcs if solutions found
        if not comm_queue.empty():
            program_calculation_complete = time.time()
            comm_queue.get()
            all_started = False
            prcs_started = j
            program_prcs_started = program_calculation_complete
            break

        # start
        prcs.start()

        # TODO: Fix authentication typeerror
        # raises typeerror because AuthenticationString in process object, still works doe
        # only prints errors, probably a security flaw  :(
        prcs_queue.put(prcs)

        started_prcs.append(prcs)

    # time when all prcs started / not accurate when skipped for finding solution early
    if all_started:
        program_prcs_started = time.time()

    # join all processes
    for prcs in started_prcs:
        prcs.join()
    comm.join()

    # time calculations end when program finished
    if not comm_queue.empty():
        program_calculation_complete = time.time()

    # TODO: Add tests

    program_end = time.time()

    # TODO: How it was solved, by max avl. or by processors end or maybe time end

    print('\n--------- STATISTICS  ------------------- ')
    print(f'Multiprocessors begin starting: {round(program_prcs_starting - program_start, 4)}')
    print(f'Multiprocessors started: {round(program_prcs_started - program_start, 4)}')
    print(f'Multiprocessors starting sequence time: {round(program_prcs_started - program_prcs_starting, 4)}')

    print(f'\nTotal processors started: {prcs_started}')
    print(f'Total processors not started: {prcs_max - prcs_started}')
    print(f'Max available processors: {prcs_max}')

    print(f'\nCalculation time: {round(program_calculation_complete - program_calculation_start, 4)}')
    print(f'Full capacity calculation time: {round(program_calculation_complete - program_prcs_started, 4)}')

    print(f'\nCalculations complete: {round(program_calculation_complete - program_start, 4)}')
    print(f'Calculation to solution time : {round(program_calculation_complete - program_calculation_start, 4)}')
    print(f'Full capacity calculation to solution time : '
          f'{round(program_calculation_complete - program_prcs_started, 4)}')

    print(f'\nProgram execution sequence: {round(program_end - program_start, 4)}')


if __name__ == '__main__':
    main()

# Automatic Polynomial Solver

## Attention! for optimal performance use branch "new_feature"

## Install:
### Windows & Linux systems:
The code only requires python 3 to be installed, all dependencies should be defaults.

## Usage:
The Automatic Polynomial Solver (APS) takes a polynomial function (f (x)) and returns all x where f (x) = 0.

Because of limitations in time & functionality, only polynomials with real roots work. If no real root is found it will continue forever and probably crash the PC.
### Configuration-file:
The project contains a example configuration file, any new config file should be parsed the same way and have the same name to be recognised by the script. 

**How functions are parsed:** 
All functions in the configuration file are written in the following manner:
````python
polynomial = [(k,e)\(k,e)\(k,e)]
````
Each term of a polynomial is represented by a tuple of x:s constant & exponent. The terms are then separated by backslash \ inside a list to form polynomial. You could say that a \ represents +.

K represents a real constant in either integer or decimal form, fractions don't work.
e represents a real constant following the same rules as K in addition to only being a positive number, otherwise it's not a polynomial.

For example, the epolynomial: **x⁷+2x⁴-6x²+21x+71** would be parsed:
````python
polynomial = [(1,7)\(2,4)\(-6,2)\(21,1)\(71,0)]
````

**margin and prcs_max**:
The margin variable in the configuration-file stands for the interval of x, in one direction (|x|), to be inspected by the script.
For example a margin value of 15 would imply a closed interval between x values -15 to 15. If there's any solutions outside this interval they will not be found.

The accuracy / probability of finding all solutions with the program depends on the number of processors used. 
Each processor will execute an algorithm from a designated x value inside the margin, the more processors available for the program 
the higher the resolution of the searched intervalls become. The size of the intervals also grow larger.


The resolution is also determined by the size of the margin, for example:

>500 processors and margin 15 => resolution 15/500 = 0,03
>500 processors and margin 5 => resolution 5/500 = 0,01


My recommendation is max 2000 processors, generally works for most intervals even marginal > 1000

### Manual-input:
The script also has an option for manual input where you can input the function directly in the terminal. This feature is not recommended as it has not been properly tested.


This option can be chosen when starting the script.

### Things to keep in mind:
- When running th code will output multiple errors like this: *"TypeError: Pickling an AuthenticationString object is disallowed for security reasons"*
    . This error is raised by the multiprocessing library when the code attempts to pt a process object on a multiprocessor Queue. The code successfully executes this but the library still raises this error/warning.
    Either way it's nothing to worry about but should probably be patched.


- If there's no solution to a polynomial, all available processors will be started. Therefore, you should be carful with the 
maximum amount of processors you allow the program to start. My Thinkpad can handle ca ~1000 instantly, ~5000 ok, but 
starts to crash at ~200 000 processors.


- More processors doesn't always equate to faster execution. Only smaller marginal does. This happens because of pythons 
global interpreter, multiprocessing is therefore a form of "fake" parallel execution, where every process has to go 
through the interpreter one at a time. If 200 000 processes has to be run in "parallell" the interpreter will have to switch
between 200 000 processes, resulting in considerably slower execution speed. My theory is that thins change is exponential.

Multiprocessing is therefore only more effektiv than regular programing if it utilises a fewer amount of processes (at leas in python).
In my experience 2000 processors should be more than enough for most if not all polynomials to find all possible solutions. 
If less than 100 are used there's a considerable risk of missing possible solution

## How it works:

### Numerical equation:
The program makes use of the following equation to numerically find an approximate value of f(x) = 0

>(1): y = f(a) + f'(a)(x-a)

rewritten to:
>(2): x = (f(a)/f'(a)) + a


by continuously solving (2) and changing a:s value to x, we get an infinitely closer value to the true solution. We can
stop this infinite execution when the desired precision is reached. 

The problem with this equation is that it requires a
start value to a and is also only capable of calculating one approximate solution.

### Multiprocessing:
This flaw can be worked around thanks to pythons multiprocessing library.
The program starts a desired amount of processors inside an intervall, both defined by the user.
Each processor runs a separate instance of the algorithm from its own designated x start value.
These start values are determined by the marginal/amount of processors * processor instance. 
This way all processors are equally distributed through negatives & positives of x.

### The nature of the algorithm:
The algorithm, most of the time, 'moves' depending on weather the graph of the polynomial is descending or ascending at x.
Therefore, all processors will result in values closer and closer to x values of solutions.


With a large enough intervall (margin) and resolution we can assume that all solutions available have been found.
We can also confirm that all have been found by the degree of the polynomial, degree 3 => max 3 possible solutions.

## Extension / upgraded program
This program works in a rader "brute-force" way, but there is a possible way to build upon this code 
to make an even more accurate & faster program... 
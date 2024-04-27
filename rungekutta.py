def f(x, y):
    return x + y

def rungekutta4(x0, y0, xn, n):

    h = (xn - x0) / n

    print('\n--------SOLUTION--------')
    print('-------------------------')
    print('x0\t\ty0\t\tyn')
    print('-------------------------')
    for i in range(n):
        k1 = h * (f(x0, y0))
        k2 = h * (f((x0 + h / 2), (y0 + k1 / 2)))
        k3 = h * (f((x0 + h / 2), (y0 + k2 / 2)))
        k4 = h * (f((x0 + h), (y0 + k3)))
        k = (k1 + 2 * k2 + 2 * k3 + k4) / 6
        yn = y0 + k
        print('%.4f\t%.4f\t%.4f' % (x0, y0, yn))
        print('-------------------------')
        y0 = yn
        x0 = x0 + h

    print('\nAt x=%.4f, y=%.4f' % (xn, yn))

rungekutta4(0,1,1,3)
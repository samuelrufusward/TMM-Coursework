import numpy as np
import CubicEquationSolver
import matplotlib.pyplot as plt


def plot_solution_space():
    q1_arr = np.linspace(0, 60/13, 100)
    q2_arr = np.linspace(0, 1, 100)
    tol = 0.000001
    for q1 in q1_arr:
        for q2 in q2_arr:

            sol = CubicEquationSolver.solve(1, -50, 600+195*q1+400*q2, -3900*q1-12000*q2)
            if q2 == 0.0:
                print(sol)
            if any(abs(v.imag)<tol and v >= 0 - tol and v <= 20 + tol for v in sol):

                plt.plot([q1], [q2], marker="o", markersize=2, markeredgecolor="green",
                            markerfacecolor="green")

            else:
                plt.plot([q1], [q2], marker="o", markersize=2, markeredgecolor="red",
                         markerfacecolor="red")
    plt.title("Flow Capacity Region")
    plt.xlabel("q1")
    plt.ylabel("q2")
    plt.show()

plot_solution_space()
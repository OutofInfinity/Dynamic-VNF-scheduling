import cplex


class Solver:

    def __init__(self, t, n, r, v, d, f, rho, vir):
        self.R = r
        self.N = n
        self.T = t
        self.V = v
        self.d = d
        self.f = f
        self.rho = rho
        self.vir = vir
        self.h = []
        self.z = []
        self.lr = []

    def setupproblem(self, c):
        c.objective.set_sense(c.objective.sense.maximize)

        allh = []
        allz = []

        # h
        for t in range(self.T):
            self.h.append([])
            for n in range(self.N):
                self.h[t].append([])
                for r in range(self.R):
                    self.h[t][n].append([])
                    for v in range(self.V):
                        hvarname = "h" + str(t) + str(n) + str(r) + str(v)
                        self.h[t][n][r].append(hvarname)
                        allh.append(hvarname)
        c.variables.add(names=allh, lb=[0] * len(allh), ub=[1] * len(allh), types=["B"] * len(allh))

        # z
        for t in range(self.T):
            self.z.append([])
            for n in range(self.N):
                self.z[t].append([])
                for r in range(self.R):
                    self.z[t][n].append([])
                    for v in range(self.V):
                        varname = "z" + str(t) + str(n) + str(r) + str(v)
                        self.z[t][n][r].append(varname)
                        allz.append(varname)
        c.variables.add(names=allz, lb=[0] * len(allz), ub=[1] * len(allz), types=["B"] * len(allz))

        # lr
        for r in range(self.R):
            lrvarname = "lr" + str(r)
            self.lr.append(lrvarname)
        c.variables.add(names=self.lr, lb=[0] * len(self.lr), ub=[1] * len(self.lr), types=["B"] * len(self.lr),
                        obj=[1] * len(self.lr))

        # constraint3
        for t in range(self.T):
            for n in range(self.N):
                for r in range(self.R):
                    for v in range(self.V):
                        hvars = []
                        hcoefs = []
                        hvars.append(self.h[t][n][r][v])
                        hcoefs.append(1)
                        for t1 in range(t, min(t+self.rho[n][r][v], self.T)):
                            for r1 in range(self.R):
                                if r1 != r:
                                    for v1 in range(self.V):
                                        hvars.append(self.h[t1][n][r1][v1])
                                        hcoefs.append(1)
                                # else:
                                #     continue
                        c.linear_constraints.add(lin_expr=[cplex.SparsePair(hvars, hcoefs)],
                                                 senses="L", rhs=[1])

        # constraint4
        for r in range(self.R):
            for i in range(len(self.vir[r]) - 1):
                lvar = []
                lcoefs = []
                for n in range(self.N):
                    for t in range(self.T):
                        lvar.append(self.h[t][n][r][self.vir[r][i + 1]])
                        lcoefs.append(self.f[n][r][self.vir[r][i + 1]] * t)
                        lvar.append(self.h[t][n][r][self.vir[r][i]])
                        lcoefs.append(-self.f[n][r][self.vir[r][i]] * (t + self.rho[n][r][self.vir[r][i]]))
                c.linear_constraints.add(lin_expr=[cplex.SparsePair(lvar, lcoefs)],
                                         senses="G", rhs=[0])

        # constraint5
        for r in range(self.R):
            for v in range(self.V):
                for n in range(self.N):
                    c5var = []
                    c5coefs = []
                    for t in range(self.T):
                        c5var.append(self.h[t][n][r][v])
                        c5coefs.append(1)
                    c.linear_constraints.add(lin_expr=[cplex.SparsePair(c5var, c5coefs)],
                                             senses="E", rhs=[self.f[n][r][v]])

        # 7a
        for r in range(self.R):
            for n in range(self.N):
                for t in range(self.T):
                    c7avar = []
                    c7acoef = []
                    c7avar.append(self.z[t][n][r][self.vir[r][len(self.vir[r]) - 1]])
                    c7acoef.append(1)
                    c7avar.append(self.h[t][n][r][self.vir[r][len(self.vir[r]) - 1]])
                    c7acoef.append(-1)
                    c.linear_constraints.add(lin_expr=[cplex.SparsePair(c7avar, c7acoef)],
                                             senses="L", rhs=[0])

        # 7b
        for r in range(self.R):
            for n in range(self.N):
                for t in range(self.T):
                    c7bvar = []
                    c7bcoef = []
                    c7bvar.append(self.z[t][n][r][self.vir[r][len(self.vir[r]) - 1]])
                    c7bcoef.append(1)
                    c7bvar.append(self.lr[r])
                    c7bcoef.append(-1)
                    c.linear_constraints.add(lin_expr=[cplex.SparsePair(c7bvar, c7bcoef)],
                                             senses="L", rhs=[0])

        # 7c
        for r in range(self.R):
            for n in range(self.N):
                for t in range(self.T):
                    c7cvar = []
                    c7ccoef = []
                    c7cvar.append(self.z[t][n][r][self.vir[r][len(self.vir[r]) - 1]])
                    c7ccoef.append(1)
                    c7cvar.append(self.h[t][n][r][self.vir[r][len(self.vir[r]) - 1]])
                    c7ccoef.append(-1)
                    c7cvar.append(self.lr[r])
                    c7ccoef.append(-1)
                    c.linear_constraints.add(lin_expr=[cplex.SparsePair(c7cvar, c7ccoef)],
                                             senses="G", rhs=[-1])

        # 8
        for r in range(self.R):
            lzvar = []
            lzcoef = []
            for n in range(self.N):
                for t in range(self.T):
                    lzvar.append(self.z[t][n][r][self.vir[r][len(self.vir[r]) - 1]])
                    lzcoef.append(self.f[n][r][self.vir[r][len(self.vir[r]) - 1]] *
                                  (t + self.rho[n][r][self.vir[r][len(self.vir[r]) - 1]]))
            c.linear_constraints.add(lin_expr=[cplex.SparsePair(lzvar, lzcoef)],
                                     senses="L", rhs=[self.d[r]])

    def solve(self):
        c = cplex.Cplex()

        # Set an overall node limit
        # c.parameters.mip.limits.nodes.set(5000)

        self.setupproblem(c)

        c.solve()

        sol = c.solution

        if sol.is_primal_feasible():
            ans = []
            for t in range(self.T):
                ans.append([])
                for n in range(self.N):
                    ans[t].append([])
                    for r in range(self.R):
                        ans[t][n].append([])
                        for v in range(self.V):
                            ans[t][n][r].append(sol.get_values(self.h[t][n][r][v]))

            return ans[0]
        else:
            return []


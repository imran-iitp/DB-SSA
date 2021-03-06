

class MyRawCfgToGraph():
    
    def __init__(self, rawCfg, cfg):   # here 'tree'=RawCfg
        self.tree = rawCfg
        self.dot_str = ""
        self.cfg = cfg
    
    
    def execute(self):
        tokens = self.modifyRawCfg()
        f, l = self.cfgReader(tokens, 0, len(tokens) - 1)
        self.dot_str = "\n\tstart -> " + f + ";" + self.dot_str
        for i in l:
            self.dot_str = self.dot_str + "\n\t" + i + " -> exit;"
        self.dot_str = "# dot file created at runtime\n" + "\ndigraph G {" + self.dot_str
        self.dot_str = self.dot_str + "\n\n\tstart [shape=Msquare, color=green];\n\texit [shape=Msquare, color=red];\n}"
        print("\n\n", self.dot_str)
        self.cfg.dotGraph = self.dot_str
    
    
    def modifyRawCfg(self):
        self.tree = self.tree.replace("  ", " ")
        self.tree = self.tree.strip()
        tokens = self.tree.split(" ")
        return tokens

    def connect(self, x, y):
        if not x==y:
            self.cfg.connect(int(x), int(y))
            self.dot_str = self.dot_str + "\n\t" + x + " -> " + y + " ;"

    def makeTrueBranch(self, parent, child):
        self.cfg.nodes[int(parent)].branching['true'] = int(child)

    def makeFalseBranch(self, parent, child):
        self.cfg.nodes[int(parent)].branching['false'] = int(child)


    def connectForDot(self, x, y, param=""):
        if not (x == y):
            self.dot_str = self.dot_str + "\n\t" + x + " -> " + y + " "
            if (param == "if_true" or param == "while_true"):
                self.dot_str = self.dot_str + "[color=green] ;"
            elif param == "if_false" or param == "while_false":
                self.dot_str = self.dot_str + "[color=red] ;"
            else:
                self.dot_str = self.dot_str + ";"
    

    def reshapeNodeStyle(self, node, shape, color):
        self.dot_str = self.dot_str + "\n\t" + node + " [shape=" + shape + ", color=" + color + "] ;"
    

    def utilBracketMatcher(self, tokens, i):
        c = 1
        while True:
            i = i + 1
            if (tokens[i] == "]"):
                c = c - 1
            if (tokens[i] == "["):
                c = c + 1
            if (c == 0):
                return i
    
    
    def cfgReader(self, tokens, s, e):
        # assumming : we get string of form [---] here, strictly
        s = s + 1  # start
        e = e - 1  # end
        current = s
        # a = "-1"	#maintain parent
        a = set()
        # re = "-1"	#maintain return_end
        re = set()
        rs = "-1"  # maintain return_start
        while current <= e:
            # case_0
            if tokens[current] == "[":
                curr2 = self.utilBracketMatcher(tokens, current)
                f, l = self.cfgReader(tokens, current, curr2)  # returns (first, last)
                current = curr2 + 1
                # connecting parent
                if (len(a) > 0):
                    for i in a:
                        self.connect(i, f)
                # a
                a = set(l)
                # rs
                if (rs == "-1"):
                    rs = f
                # re
                re = set(l)
            # case_1
            elif tokens[current].isdigit() == True:
                # rs
                if (rs == "-1"):
                    rs = tokens[current]
                # connecting parent
                if (len(a) > 0):
                    for i in a:
                        self.connect(i, tokens[current])
                while current + 1 <= e and tokens[current + 1].isdigit() == True:
                    self.connect(tokens[current], tokens[current + 1])
                    current = current + 1
                current = current + 1
                # a
                a = set()
                a.add(tokens[current - 1])
                # re
                re = set(a)
            # print (" rs = ", rs, " , re = ", re)
            # case_2
            elif tokens[current].split("_")[0] == "if":
                to_merge_set = set()
                # if_handling...
                temp = tokens[current].split("_")[1]  # if_condition
                self.reshapeNodeStyle(temp, "diamond", "orange")
                # connecting parent
                if (len(a) > 0):
                    for i in a:
                        self.connect(i, temp)
                # rs
                if (rs == "-1"):
                    rs = temp
                current = current + 1
                curr2 = self.utilBracketMatcher(tokens, current)  # if_true
                f1, l1 = self.cfgReader(tokens, current, curr2)
                self.connect(temp, f1)  # ---connection
                self.makeTrueBranch(temp, f1)
                for i in l1:
                    to_merge_set.add(i)
                current = curr2 + 1
                # elsif_handling...
                while tokens[current + 1].split("_")[0] == "elsif":
                    current = current + 1
                    temp_i = tokens[current].split("_")[1]  # elsif_condition
                    self.reshapeNodeStyle(temp_i, "diamond", "orange")
                    self.connect(temp, temp_i)  # connecting parent
                    self.makeFalseBranch(temp, temp_i)
                    temp = temp_i  # making temp pseudo-parent
                    current = current + 1
                    curr2_i = self.utilBracketMatcher(tokens, current)  # -----elsif_true
                    f_i, l_i = self.cfgReader(tokens, current, curr2_i)
                    self.connect(temp_i, f_i)  # ---connection
                    self.makeTrueBranch(temp_i, f_i)
                    for i in l_i:
                        to_merge_set.add(i)
                    current = curr2_i + 2  # ---[ elsif_x [ y x ] ]

                # else handling...
                curr2 = self.utilBracketMatcher(tokens, current)  # else_part
                f2, l2 = self.cfgReader(tokens, current, curr2)
                self.connect(temp, f2)  # ---connection
                self.makeFalseBranch(temp, f2)
                for i in l2:
                    to_merge_set.add(i)
                # print (" rs = ", rs, " , re = ", re, " , a = ", a)
                # print (" f1 = ", f1, " , l1 = ", l1, ", f2 = ", f2, ", l2 = ", l2)
                current = curr2 + 2  # <<---note : [ if_XX [ ][ ] ]

                # re
                re = set(to_merge_set)
                # a
                a = set(re)

        # return
        # print (" rs = ", rs, " , re = ", re)
        return rs, re

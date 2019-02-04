import sys
from MyHelper import MyHelper
from gen.PlSqlVisitor import PlSqlVisitor

global varSet
varSet = list()

class z3formulaofvcs(PlSqlVisitor):
    def __init__(self, cfg, parser):
        self.cfg = cfg
        self.parser = parser
        self.helper = MyHelper(self.parser)


    def z3VariableDeclarationSet(self, path):
        global varSet
        for i in range(len(path)):
            node = path[i]
            if self.cfg.nodes[node].versionedRHS:
                for element in self.cfg.nodes[node].versionedRHS:
                    values = self.cfg.nodes[node].versionedRHS[element]
                    if values not in varSet:
                        varSet.append(values)

            if self.cfg.nodes[node].versionedLHS:
                for element in self.cfg.nodes[node].versionedLHS:
                    values = self.cfg.nodes[node].versionedLHS[element]
                    if values not in varSet:
                        varSet.append(values)

            if  self.cfg.nodes[node].destructedPhi:
                    #print(context)
                    for element in self.cfg.nodes[node].destructedPhi:
                        values = self.cfg.nodes[node].destructedPhi[element]
                        for i in range(len(values)):
                            if values[i] not in varSet:
                                varSet.append(values[i])


        return varSet
    
    def z3FormulaForEachPath(self, vc):
        global varSet
        y = list(map(lambda k: k+" = Int('"+k+"')\n", varSet))
        with open('fun.py', 'w') as outfile:
            outfile.writelines("from z3 import *\n")
            outfile.writelines(y)
            outfile.writelines("s = Solver()\n")
            outfile.writelines("s.add("+vc[8:len(vc)-10]+")\n")
            outfile.writelines("s.add(Not("+vc+"))\n")
            outfile.writelines("print(s.check())\n")
            outfile.writelines("print(s.model())\n")
            

    


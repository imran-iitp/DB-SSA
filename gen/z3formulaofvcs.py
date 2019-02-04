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


        print(varSet)


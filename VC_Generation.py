import sys
from inspect import signature
from antlr4 import *
from gen.PlSqlLexer import PlSqlLexer
from gen.PlSqlParser import PlSqlParser
from gen.PlSqlVisitor import PlSqlVisitor
from MyHelper import MyHelper

from MyNode import MyNode

class VC_Generation(PlSqlVisitor):
    path = ""
    def __init__(self, cfg, utility):
        self.cfg = cfg
        self.utility = utility
        self.SEVC = ""
        #self.getRuleName = getRuleName

    def SeVc(self, cfg, ctx):
        for nodeId in cfg.nodes:
            ruleName = MyHelper(ctx).getRuleName(ctx)
            if ruleName == "assignment_statement":
                if len(list(cfg.nodes[nodeId].versionedLHS.values())) == 1 and len(list(cfg.nodes[nodeId].versionedRHS.values())) == 1:
                    path = path + "(" + list(cfg.nodes[nodeId].versionedLHS.values())+ "=="+ list(cfg.nodes[nodeId].versionedRHS.values()) +")"
                    print(path)
                    print("hi")
                
                
                
                
        

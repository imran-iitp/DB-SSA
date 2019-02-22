import sys
from MyHelper import MyHelper
from gen.PlSqlVisitor import PlSqlVisitor

global vcs
vcs = " "

class SymbolicVcGeneration(PlSqlVisitor):
    
    def __init__(self, cfg, parser):
        self.cfg = cfg
        self.parser = parser
        self.helper = MyHelper(self.parser)
        #input("enter a num")
        
    def SymbolicVc(self, path):
        global vcs
        vcs = "True"
        for i in range(len(path)):
            node = path[i]
            context = self.cfg.nodes[node].ctx
            if context is None:
                if  self.cfg.nodes[node].destructedPhi:
                    #print(context)
                    for element in self.cfg.nodes[node].destructedPhi:
                        values = self.cfg.nodes[node].destructedPhi[element]
                        vcs = "And(" + vcs + ", " +values[0] + " == " + values[1] + ")" 
                        #print(self.cfg.nodes[node].destructedPhi[element])
                    #vcs = vcs + 
            else:
                ruleName = self.helper.getRuleName(context)
                #print(ruleName)
                #print(str(context.toStringTree(recog=self.parser)))
                if ruleName == "condition":
                    tempctx = context.children[0]
                    
                    if self.cfg.nodes[node].branching['true'] == path[i + 1]:
                        if childctx.children[2].getText() == "NULL":
                            vcs = "And(" + vcs + ", " +"True" + ")"
                        elif childctx.children[2].getText() == "NOTNULL":
                            vcs = "And(" + vcs + ", " + "True" + ")"
                        else:
                            vcs = "And(" + vcs + ", " + self.getCondition(node, childctx) + ")"

                    else:
                        if childctx.children[2].getText() == "NULL":
                            vcs = "And(" + vcs + ", "+ "True" + ")"
                        elif childctx.children[2].getText() == "NOTNULL":
                            vcs = "And(" + vcs + ", " + "True" + ")"
                        else:
                            vcs = "And(" + vcs + ", " + "Not("+self.getCondition(node, childctx) + "))"
    
                if ruleName == "assignment_statement":
                    vcs = "And(" + vcs + ", " + self.getAssignment_statement(node, context) + ")"
                if ruleName == "update_statement":
                    vcs = "And(" + vcs + ", " + self.getUpdate_statement(node, context) + ")"
                if ruleName == "insert_statement":
                    vcs =  self.getInsert_statement(node, context)
                if ruleName == "cursor_declaration":
                    vcs = "And(" + vcs + ", " + self.getCursor_declaration(node, context) +")"
                if ruleName == "fetch_statement":
                    vcs = "And(" + vcs + ", " + self.getFetch_statement(node, context)+ ")"
                if ruleName == "select_statement":
                    vcs = self.getSelect_statement(node, context)
                if ruleName == "delete_statement":
                    vcs = "And("+vcs+" , "+self.getDelete_statement(node, context)+")"
                if ruleName == "raise_statement":
                    print("Exception Raised")
                    break
                if ruleName == "exception_handler":
                    temp_ctx = context.children[3]
                    child_count =temp_ctx.getChildCount()
                    for child in range(child_count):
                        if temp_ctx.children[child].getText() == ";":
                            continue
                        else:
                            child_ctx = temp_ctx.children[child]
                            if self.helper.getRuleName(child_ctx.children[0]) == "assert_statement":
                                #input("wait")
                                vcs = "Implies(" + vcs + ", " + self.getAssert_statement(node, child_ctx.children[0]) + ")"
                            else:
                                continue
                if ruleName == "assume_statement":
                    vcs = "And(" + vcs + ", "+ self.getAssume_statement(node, context) +")"
                if ruleName == "assert_statement":
                    vcs = "Implies(" + vcs + ", " + self.getAssert_statement(node, context)+")"
                else:
                    pass
        
        #print(vcs)
        return vcs
    def getAssume_statement(self, nodeId, ctx):
        #global vcs
        res =  self.getWhereexpr(nodeId, ctx.children[1])
        return res
    
    def getAssert_statement(self, nodeId, ctx):
        res =  self.assertExpression(nodeId, ctx.children[1]) 
        return res

    def assertExpression(self, nodeId, ctx):
        if  ctx.children[1].getText() == "AND":
            #print(self.helper.getRuleName(ctx.children[0]))
            res =  "Or(" + self.assertExpression(nodeId, ctx.children[0])+ ", " + \
                   self.assertExpression(nodeId, ctx.children[2])+ ")"
        else:
            if ctx.children[1].getText() == "=":
                #input("wait")
                res = self.getVersionedTerminalRHS(nodeId, ctx.children[0]) + "==" + \
                      self.getVersionedTerminalRHS(nodeId, ctx.children[2])
            else:
                res = self.getVersionedTerminalRHS(nodeId, ctx.children[0]) + self.getTerminal(ctx.children[1]) + \
                      self.getVersionedTerminalRHS(nodeId, ctx.children[2])
        return res

    def getSelect_statement(self, nodeId, ctx):
        global vcs
       
        vcs = "And(" + vcs + ", " + self.getInto_clause(nodeId, ctx.children[0].children[0].children[2]) + "==" + \
              self.getVersionedTerminalRHS(nodeId, ctx.children[0].children[0].children[1]) + ")"
        vcs = "And(" + vcs + ", " + self.getWhereClause(nodeId, ctx.children[0].children[0].children[4]) +")"
        
        if self.cfg.nodes[nodeId].destructedPhi:
            for element in self.cfg.nodes[nodeId].destructedPhi:
                values = self.cfg.nodes[nodeId].destructedPhi[element]
                vcs = "And(" + vcs + ", " + values[0] + "==" + values[1] + ")"
               
        return vcs
       

    def getInto_clause(self, nodeId, ctx):
        return self.getVersionedTerminalRHS(nodeId, ctx.children[1])
        
    
    def getFetch_statement(self, nodeId, ctx):
        #global vcs
        res = self.getVersionedTerminalRHS(nodeId, ctx.children[1])+ " == " \
              + self.getVersionedTerminalLHS(nodeId, ctx.children[3]) 
        return res

    def getCursor_declaration(self, nodeId, ctx):
        #global vcs
        if ctx.children[3].children[0].children[0].getChildCount() == 4:
            res =  "And(" + self.getVersionedTerminalLHS(nodeId, ctx.children[1]) + " == " \
              + self.getVersionedTerminalRHS(nodeId, ctx.children[3].children[0].children[0].children[1])+ ", " + \
              self.getWhereClause(nodeId, ctx.children[3].children[0].children[0].children[3]) + ")" 
        else:
            res =  self.getVersionedTerminalLHS(nodeId, ctx.children[1]) + " == " \
              + self.getVersionedTerminalRHS(nodeId, ctx.children[3].children[0].children[0].children[1])
        return res


    def getCondition(self, nodeId, ctx):
        
        if ctx.children[1].getText() == "AND":
            # print(self.helper.getRuleName(ctx.children[0]))
            res = self.getCondition(nodeId, ctx.children[0]) + " && " + \
                  "(" + self.getCondition(nodeId, ctx.children[2]) + ")"
            # input("wait")

        elif ctx.children[1].getText() == "IN":
            res = self.getVersionedTerminalRHS(nodeId, ctx.children[0]) + "==" + \
                  self.getVersionedTerminalRHS(nodeId, ctx.children[3].children[0].children[1]) + \
                  "&&" + self.getWhereexpr(nodeId, ctx.children[3].children[0].children[3].children[1])
        elif ctx.children[1].getText() == "IS":
            res = "true"

        else:
            if ctx.children[1].getText() == "=":
                res = self.getVersionedTerminalRHS(nodeId, ctx.children[0]) + "==" + \
                      self.getVersionedTerminalRHS(nodeId, ctx.children[2])
            else:
                res = self.getVersionedTerminalRHS(nodeId, ctx.children[0]) + self.getTerminal(ctx.children[1]) + \
                      self.getVersionedTerminalRHS(nodeId, ctx.children[2])

        return res

    def getAssignment_statement(self, node, ctx):
        #global vcs
        res = self.getVersionedTerminalLHS(node, ctx.children[0]) +' == '+ \
              self.getVersionedTerminalRHS(node, ctx.children[2]) 
        if self.cfg.nodes[node].destructedPhi:
            for element in self.cfg.nodes[node].destructedPhi:
                values = self.cfg.nodes[node].destructedPhi[element]
                res = "And(" + res + ", " + values[0] + "==" + values[1] + ")" 
        return res
        #print(vcs)

    def getUpdate_statement(self, nodeId, ctx):
        #global vcs
        res = "Or(" + "And(" + self.getSetClause(nodeId, ctx.children[2]) + "," \
              + self.getWhereClause(nodeId, ctx.children[3])+")" + ", " + \
              "And(" + "Not(" + self.getWhereClause(nodeId, ctx.children[3]) +")"+ ", "+\
              self.getNotSetClause(nodeId, ctx.children[2]) +"))"
        if self.cfg.nodes[nodeId].destructedPhi:
            for element in self.cfg.nodes[nodeId].destructedPhi:
                values = self.cfg.nodes[nodeId].destructedPhi[element]
                res = "And(" + res + ", " + values[0] + "==" + values[1] + ")"
        return res

    def getSetClause(self, NodeId, ctx):
        child = ctx.getChildCount()
        for i in range(child):
            if self.helper.getRuleName(ctx.children[i]) == "column_based_update_set_clause":
                print(i)
        #print(child)
        #input("wait")
        res = self.getColsetClause(NodeId, ctx.children[1])
        return res

    def getColsetClause(self, nodeId, ctx):
        res = self.getVersionedTerminalLHS(nodeId, ctx.children[0]) +' == '+ \
              self.getVersionedTerminalRHS(nodeId, ctx.children[2])
        return res
    
    def getNotSetClause(self, nodeId, ctx):
        res = self.getNotColsetClause(nodeId, ctx.children[1])
        return res

    def getNotColsetClause(self, nodeId, ctx):
        res = self.getVersionedTerminalLHS(nodeId, ctx.children[0]) +' == '+ \
              self.getVersionedTerminalRHS(nodeId, ctx.children[0])
        return res
    
    def getDelete_statement(self, nodeId, ctx):
        c = ctx.getChildCount()
        res = self.getWhereClause(nodeId, ctx.children[c-1])
        for key in self.cfg.nodes[node].versionedLHS:
            res = "And("+ res +","+self.cfg.nodes[node].versionedLHS[key]+"=="+ self.cfg.nodes[node].versionedRHS[key]+")" 
        return res
    
    def getWhereClause(self, nodeId, ctx):
        res = self.getWhereexpr(nodeId, ctx.children[1])
        return res

    def getWhereexpr(self, nodeId, ctx):
       
        if  ctx.children[1].getText() == "AND":
            #print(self.helper.getRuleName(ctx.children[0]))
            res =  "And(" + self.getWhereexpr(nodeId, ctx.children[0])+ ", " + \
                   self.getWhereexpr(nodeId, ctx.children[2])+ ")"
            #input("wait")
            
        elif ctx.children[1].getText() == "IN":
            res = "And(" +  self.getVersionedTerminalRHS(nodeId, ctx.children[0]) + "==" +\
                  self.getVersionedTerminalRHS(nodeId, ctx.children[3].children[0].children[1]) +\
                  "," + self.getWhereexpr(nodeId, ctx.children[3].children[0].children[3].children[1])+")"
        elif ctx.children[1].getText() == "BETWEEN":
            res = "And("+ self.getVersionedTerminalRHS(nodeId, ctx.children[0])+">=" +self.getVersionedTerminalRHS(nodeId, ctx.children[2])+\
                  " , "+self.getVersionedTerminalRHS(nodeId, ctx.children[0])+"<=" +self.getVersionedTerminalRHS(nodeId, ctx.children[2])+")"
        elif ctx.children[1].getText() == "LIKE": #LIKE is similar to  assignment if operand does not have wildcard.
            res = self.getVersionedTerminalRHS(nodeId, ctx.children[0]) + "==" + \
                      self.getVersionedTerminalRHS(nodeId, ctx.children[2])
        else:
            
            if ctx.children[1].getText() == "=":
                #input("wait")
                res = self.getVersionedTerminalRHS(nodeId, ctx.children[0]) + "==" + \
                      self.getVersionedTerminalRHS(nodeId, ctx.children[2])
            else:
                res = self.getVersionedTerminalRHS(nodeId, ctx.children[0]) + self.getTerminal(ctx.children[1]) + \
                      self.getVersionedTerminalRHS(nodeId, ctx.children[2])
        return res
       
        '''
        for i in range(c):
            if ctx.children[i].getChildCount() > 1:
                res = res + self.getWhereexpr(nodeId, ctx.children[i])
        if ctx.children[0].getChildCount() == 3:
            res = ""
            res = res + "&&" + self.getWhereexpr(nodeId, ctx.children[0])
        else:
            res = self.getVersionedTerminalRHS(nodeId, ctx)
        '''
        
        

    def getInsert_statement(self, nodeId, ctx):
        global vcs
        vcs = str(self.getInsertIntoandValueClause(nodeId, ctx.children[1]))
        if self.cfg.nodes[nodeId].destructedPhi:
            for element in self.cfg.nodes[nodeId].destructedPhi:
                values = self.cfg.nodes[nodeId].destructedPhi[element]
                res = "And(" + res + ", " + values[0] + "==" + values[1] + ")"
        return vcs 

    def getInsertIntoandValueClause(self, nodeId, ctx):
        global vcs
        colmnlistinto = []
        colmnlistvalues = []
        c1 = ctx.children[0].getChildCount()
        for item in range(c1):
            if self.helper.getRuleName(ctx.children[0].children[item]) == "column_name":
                #pass
                colmnlistinto.append(self.getVersionedTerminalLHS(nodeId, ctx.children[0].children[item]))
            else:
                pass
        c2 = ctx.children[1].children[1].getChildCount()
        for i in range(c2):
            if self.helper.getRuleName(ctx.children[1].children[1].children[i]) == "expression":
                colmnlistvalues.append(self.getVersionedTerminalRHS(nodeId, ctx.children[1].children[1].children[i]))
            else:
                pass

        for element in range(len(colmnlistinto)):
            vcs = "And(" + vcs + ", " + colmnlistinto[element] +" == "+colmnlistvalues[element] +")"
        return vcs

    

    def getVersionedTerminalRHS(self, nodeId, ctx):
        c = ctx.getChildCount()
        if c==0:
            if str(ctx) in self.cfg.nodes[nodeId].versionedRHS.keys():
                return self.cfg.nodes[nodeId].versionedRHS[str(ctx)] + " "
            else:
                return str(ctx) + " "
        else:
            res = ""
            for i in range(c):
                res = res + self.getVersionedTerminalRHS(nodeId, ctx.children[i])
            return res


    def getVersionedTerminalLHS(self, nodeId, ctx):
        c = ctx.getChildCount()
        if c==0:
            if str(ctx) in self.cfg.nodes[nodeId].versionedLHS.keys():
                return self.cfg.nodes[nodeId].versionedLHS[str(ctx)] + " "
            else:
                return str(ctx) + " "
        else:
            res = ""
            for i in range(c):
                res = res + self.getVersionedTerminalLHS(nodeId, ctx.children[i])
            return res


    def getTerminal(self, ctx):
        if ctx==None:
            return ""
        c = ctx.getChildCount()
        if c==0:
            return str(ctx) + " "
        else:
            res = ""
            for i in range(c):
                res = res + self.getTerminal(ctx.children[i])
            return res


            

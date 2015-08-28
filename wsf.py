from random import randint
from math import exp

class Asset(object):
    def __init__(self, assettype, notional):
        self.assettype = assettype
        self.notional = notional
        self.RWA = 0
        self.pay = 0

    ##Update the asset each quarter based on prevailing
    ##market conditions
    def step(self, market):
        return

class Mortgage(Asset):
    def __init__(self, assettype, notional, risk, interest):
        self.assettype = assettype
        self.notional = notional
        self.risk = risk
        self.interest = interest
        self.age = 0
        self.paid = 0
        self.cashflow = 0
        self.profit = 0
        if risk != 3:
            self.payment = notional*(interest/4)/(1-(1+interest/4)**(-120))
        else:
            self.payment = notional*interest/4
    
    def __repr__(self):
        s = str(self.notional) + " mortgage, " + str(self.risk) + ", " + str(self.interest) + "\n"
        return s

    def step(self,market):
        self.age += 1
        if self.notional == 0:
            self.profit = 0
            return
        if self.notional < self.payment or self.notional < 1:
            self.paid = 1
            self.cashflow = self.notional
            self.profit = 0
            self.notional = 0
            return
        
        if market == 3:
            self.cashflow = self.payment
            self.profit = self.notional*self.interest/4
            self.notional = self.notional - self.payment + self.notional*self.interest/4

        if market == 2:
            self.cashflow = 0.99*self.payment
            self.profit = 0.99*self.notional*self.interest/4-0.01*self.notional
            self.notional = 0.99*(self.notional - self.payment + self.notional*self.interest/4)
            self.payment = 0.99*self.payment

        if market == 1:
            if self.risk == 1:
                self.cashflow = 0.975*self.payment
                self.profit = 0.975*self.notional*self.interest/4-0.025*self.notional
                self.notional = 0.975*(self.notional - self.payment + self.notional*self.interest/4)
                self.payment = 0.975*self.payment
            if self.risk == 2:
                self.cashflow = 0.945*self.payment
                self.profit = 0.945*self.notional*self.interest/4-0.055*self.notional
                self.notional = 0.945*(self.notional - self.payment + self.notional*self.interest/4)
                self.payment = 0.945*self.payment
            if self.risk == 3:
                self.cashflow = 0.85*self.payment
                self.profit = 0.85*self.notional*self.interest/4-0.15*self.notional
                self.notional = 0.85*(self.notional - self.payment + self.notional*self.interest/4)
                self.payment = 0.85*self.payment

        if self.age == 360:
            self.cashflow += self.notional*0.95
            self.profit = -0.05*self.notional
            self.notional = 0
            return
        
class Bond(Asset):
    def __init__(self, assettype, notional, risk, interest, maturity):
        self.assettype = assettype
        self.paid = 0
        self.notional = notional
        self.risk = risk
        self.interest = interest/2
        self.age = 0
        self.maturity = maturity
        self.profit = 0
        self.cashflow = 0
        self.coverage = 12/risk+1
    
    def __repr__(self):
        s = "Bond: %.1f notional maturing in %.2f years, %0.1f interest rate\n" % (self.notional, (self.maturity-self.age)/4.0, self.interest*200)
        return s
    
    def step(self, market):
        if self.notional == 0:
            self.profit = 0
            self.cashflow = 0
            self.paid = 1
            return
        self.age += 1
        if self.age % 2 == 1:
            self.profit = self.interest*self.notional
            self.cashflow = self.interest*self.notional
        else:
            self.profit = 0
            self.cashflow = 0
        if market == 3:
            self.coverage += 0.5
        elif market == 1:
            self.coverage -= 1
        
        if self.coverage == 0:
            if risk == 3:
                self.cashflow += 0.6*self.notional
                self.profit -= 0.4*self.notional
            elif risk == 2:
                self.cashflow += 0.4*self.notional
                self.profit -= 0.6*self.notional
            else:
                self.profit -= self.notional
            self.notional = 0
            self.paid = 1
        
        if self.age == self.maturity:
            self.cashflow += self.notional
            self.notional = 0
            self.paid = 1

class Project(object):
    def __init__(self, size):
        if size == 1:
            self.fee = randint(50,100)
        elif size == 2:
            self.fee = randint(100,750)
        else:
            self.fee = size*randint(50,100) + size*size*randint(50,100)
        self.size = self.fee*5
        self.missfee = self.fee/4
        self.wait = 8
    
    def __repr__(self):
        s = "Size: " + str(self.size) + ", fee: " + str(self.fee) + ", wait: " + str(self.wait)
        return s
    
    def step(self):
        self.wait -= 1
    

##The top level company
class Bank(object):
    def __init__(self,name):
        self.name = ''
        self.equity = 1000
        self.capital = 1000
        self.deposits = 0
        self.assets = 1000
        self.profits = 0
        self.cashflow = 0
        self.RWA = 1000
        self.desks = []
        self.lifeprofits = 0
        self.lifequarters = 0
        self.risk = 0
        self.debt = 0
        self.debts = []
        self.firmRating = 'A'
        self.globalInterest = 0.01
        
        self.market = 3
        self.mlength = 4
        self.dlength = 4

    def startDesk(self):
        print("Starting a desk will cost $50.")
        answer = input("Would you like to start one? Y or N: ")
        if answer == "Y" or answer == "y":
            print("What desk would you like to start?")
            answer = input("Teller, Mortgage, etc: ")
            if answer == "Teller" or answer == "teller":
                newDesk = Teller()
                self.desks.append(newDesk)
            elif answer == "Mortgage" or answer == "mortgage":
                newDesk = MortgageDesk()
                self.desks.append(newDesk)
            else:
                print("That isn't a desk type...")
            self.equity -= 50
            self.assets -= 50
            self.RWA -= 50
            self.capital -= 50

    def runGame(self):
        self.profits = 0
        self.cashflow = 0
        self.RWA = self.capital
        for desk in self.desks:
            desk.runDesk(self.market)
            self.profits += desk.getProfits()
            self.cashflow += desk.getCashflow()
            self.capital = self.capital + desk.assetChange
            self.RWA += desk.RWA
            if(isinstance(desk,Teller)):
                self.deposits += desk.assetChange
            if(isinstance(desk,AnalysisDesk)):
                if desk.project is None:
                    for desk2 in self.desks:
                        if(isinstance(desk2,AccountManagement)):
                            if not (not desk2.projects):
                                desk.project = desk2.projects[0]
                                desk2.projects.pop(0)
                                desk.project.wait += 2
                else:
                    print(str(desk.project.size) + " left in " + str(desk.project.wait) + " quarters")
        self.profits -= self.deposits*0.0025
        self.deposits += self.deposits*0.0025
        
        self.debt = 0
        for i,bond in enumerate(self.debts):
            bond.step(2)
            bond.coverage = 10
            self.cashflow -= bond.cashflow
            self.profits -= bond.profit
            if bond.paid == 1:
                self.debt -= bond.notional
                self.debts.pop(i)
                continue
            self.debt += bond.notional
        
        self.lifeprofits += self.profits
        self.capital += self.cashflow
        self.equity += self.profits
        
        D2E = self.debt/self.equity
        if D2E < 1:
            self.firmRating = 'A'
        elif D2E < 1.5:
            self.firmRating = 'BBB'
        elif D2E < 2:
            self.firmRating = 'BB'
        elif D2E < 2.5:
            self.firmRating = 'B'
        else:
            self.firmRating = 'C'
        
        self.risk = 2*self.deposits/self.RWA
        self.mlength -= 1
        self.dlength -= 1
        if self.mlength == 0:
            if self.market == 3:
                self.market = randint(2,3)
                self.mlength = randint(4,10)
                self.dlength = self.mlength+randint(0,4)-2
            elif self.market == 2:
                self.market = randint(0,100)
                self.mlength = randint(4,10)
                self.dlength = self.mlength+randint(0,4)-2
                if self.market < 5:
                    self.market = 1
                    self.mlength = 8
                    self.dlength = self.mlength+randint(0,4)-2
                elif self.market < 50:
                    self.market = 2
                else:
                    self.market = 3
            else:
                self.market = randint(1,3)
                self.mlength = randint(1,2)
                self.dlength = self.mlength
        
        if self.dlength < 0:
            print("Market will be " + str(self.market) + " for 0 quarters longer")
        else:
            print("Market will be " + str(self.market) + " for " + str(self.dlength) + " quarters longer")
        
    
    def issueDebt(self, amount):
        if amount > self.equity:
            print("That is too much debt. Try an amount less than %.2f" % (self.equity))
            return
        
        maturing = 0
        for bond in self.debts:
            if (bond.maturity-bond.age) < 3:
                maturing += bond.notional
        
        D2E = (self.debt+amount)/self.equity
        if D2E < 1:
            print("Your debt rating will be A.")
            print("You can issue debt for %.3f per year and a 5 year maturity." %(self.globalInterest+0.01))
            answer = input("Issue debt? ")
            if answer == 'y' or answer == 'Y':
                self.debt += amount
                bond = Bond('bond',amount,1,(self.globalInterest/4+0.0025),20)
                self.capital += amount
                self.debts.append(bond)
        elif D2E < 1.5:
            print("Your debt rating will be BBB.")
            print("You can issue debt for %.3f per year and a 5 year maturity." %(self.globalInterest+0.02))
            answer = input("Issue debt? ")
            if answer == 'y' or answer == 'Y':
                self.debt += amount
                bond = Bond('bond',amount,1,(self.globalInterest/4+0.005),20)
                self.capital += amount
                self.debts.append(bond)
        elif D2E < 2:
            print("Your debt rating will be BB.")
            print("You can issue debt for %.3f per year and a 5 year maturity." %(self.globalInterest+0.03))
            answer = input("Issue debt? ")
            if answer == 'y' or answer == 'Y':
                self.debt += amount
                bond = Bond('bond',amount,1,(self.globalInterest/4+0.0075),20)
                self.capital += amount
                self.debts.append(bond)
        elif D2E < 2.5:
            print("Your debt rating will be B.")
            print("You can issue debt for %.3f per year and a 5 year maturity." %(self.globalInterest+0.04))
            answer = input("Issue debt? ")
            if answer == 'y' or answer == 'Y':
                self.debt += amount
                bond = Bond('bond',amount,1,(self.globalInterest/4+0.01),20)
                self.capital += amount
                self.debts.append(bond)
        else:
            print("Your debt rating will be C.")
            print("You can issue debt for %.3f per year and a 5 year maturity." %(self.globalInterest+0.08))
            answer = input("Issue debt? ")
            if answer == 'y' or answer == 'Y':
                self.debt += amount
                bond = Bond('bond',amount,1,(self.globalInterest/4+0.02),20)
                self.capital += amount
                self.debts.append(bond)


    def stats(self):
        print("Bank " + self.name)
        print("%.1f" % (self.capital) + " in cash.")
        print("%.1f" %(self.equity) + " in equity.")
        print("%.1f" %(self.debt) + " in debt.")
        print("%.2f" %self.risk + " is the deposit risk level.")
        print("Your debt is rated " + self.firmRating)
        print("The bank made " + "%.2f" %(self.profits) + " in profits last quarter.\n")
        
        for desk in self.desks:
            if isinstance(desk,Teller):
                print("You have a teller counter with " + str(desk.employees[0]) + " employee(s).")
                print("It has " + "%.2f" % self.deposits + " in deposits.")
                print("These cost " + "%.2f" % (self.deposits*self.globalInterest/25) + " in interest per quarter.")
            elif isinstance(desk,MortgageDesk):
                print("You have a mortgage desk with " + str(desk.employees[0]) + " employee(s).")
                print("It has " + "%.2f" % (desk.capital) + " in mortgages.")
                print("It made " + "%.2f" % (desk.profits) + " in profits and returned " + "%.2f" % (desk.cashflow) + " in capital the past quarter.")
            elif isinstance(desk,EquityDesk):
                print("You have a equity trading desk with " + str(desk.employees[0]) + " employee(s).")
                print("It has a " + "%.1f" % (desk.portfolio) + " portfolio.")
                print("It made " + "%.2f" % (desk.profits) + " in profits and returned " + "%.2f" % (desk.cashflow) + " in capital the past quarter.")
            elif isinstance(desk,FixedIncomeDesk):
                print("You have a fixed income desk with " + str(desk.employees[0]) + " employee(s).")
                print("It has " + str(desk.capital) + " in bonds.")
                print("It made " + "%.2f" % (desk.profits) + " in profits and returned " + "%.2f" % (desk.cashflow) + " in capital the past quarter.")
            print("\n")

class Desk(object):
    def __init__(self):
        self.employees = [1,0,0,0]
        self.capital = 0
        self.assets = []
        self.profits = 0
        self.cashflow = 0
        self.RWA = 0
        self.lifeprofits = 0
        self.employeeCost = 1
        self.assetChange = 0
        self.maxAssets = 1000000

    def addEmployee(self):
        if self.employees[0] == 2*(self.employees[1]+1):
            if self.employees[1] == self.employees[2]+1:
                if self.employees[2] == 1:
                    self.addDirector()
                else:
                    self.addVP()
            else:
                self.addAssoc()
        else:
            self.addAnalyst()
            
    def runDesk(self,market):
        self.cashflow = 0
        self.profits = 0
        self.RWA = 0
        for i,asset in enumerate(self.assets):
            asset.step(market)
            self.cashflow += asset.cashflow
            self.profits += asset.profit
            if asset.paid == 1:
                self.assets.pop(i)
        
        self.profits = self.profits - self.employeeCost
        self.cashflow = self.cashflow - self.employeeCost
        self.cashflow = self.getCashflow()
        
        if self.capital < self.maxAssets:
            self.assetChange = -1*self.assetChanges()
            if (-self.assetChange) > 0:
                self.deployCapital(-self.assetChange)
        
        self.RWAcalc()
    
    def getProfits(self):
        return self.profits
    
    def getCashflow(self):
        return self.cashflow

    def RWAcalc(self):
        return

    def assetChanges(self):
        return 0

    def deployCapital(self,nothing):
        return

def answerYN():
    answer = input("Would you like to add one? Y or N: ")
    if answer == "Y" or answer == "y":
        return True
    else:
        return False

class Teller(Desk):
    name = "teller"
    def __init__(self):
        self.intlevel = 1
        self.deposits = 0
        Desk.__init__(self)

    def addAnalyst(self):
        print("A teller can bring in ~150 in deposits every quarter.")
        print("Tellers cost 1 every quarter and 10 to hire.")
        if answerYN():
            self.employees[0] += 1
            self.employeeCost += 1

    def addAssoc(self):
        print("A manager can bring in ~150 deposits every quarter,")
        print("and help the tellers bring in an extra 20%")
        print("Retail managers cost $2 every quarter.")
        if answerYN():
            self.employees[1] += 1
            self.employeeCost += 2
        
    def changeRisk(self, risk):
        self.intlevel = risk

    def assetChanges(self):
        changes = -150*(self.employees[0]+self.employees[1])*(1+self.employees[1]*0.2)
        return changes
    
    def deployCapital(self, assetAdd):
        self.deposits += assetAdd
    
    def getProfits(self):
        return -self.employeeCost
    
    def getCashflow(self):
        return -self.employeeCost
        
    def edit(self):
        print("The teller desk has one option.\n")
        answer = input("Would you like to add an employee? ")
        if answer == 'y' or answer == 'Y':
            self.addEmployee()
        

class MortgageDesk(Desk):
    name = "mortgage"
    def __init__(self):
        self.intlevel = 1
        Desk.__init__(self)

    def addAnalyst(self):
        print("A mortgage underwriters can write 100 in mortgages every quarter.")
        print("Mortgage underwriters cost 1 every quarter.")
        if answerYN():
            self.employees[0] += 1
            self.employeeCost += 1

    def addAssoc(self):
        print("A mortgage desk statistician can increase the expected return on mortgages.")
        print("All current mortgages become 20% less likely to default.")
        if answerYN():
            self.employees[1] += 1
            self.employeeCost += 2
    
    def assetChanges(self):
        changes = 100*self.employees[0]
        return changes
    
    def deployCapital(self,assetAdd):
        mortgage1 = Mortgage('mortgage',self.assetChanges(),self.intlevel,0.02+0.03*self.intlevel)
        self.assets.append(mortgage1)

    def RWAcalc(self):
        self.RWA = 0
        self.capital = 0
        for asset in self.assets:
            self.capital += asset.notional
            self.RWA += (10-asset.risk)*asset.notional/10
    
    def edit():
        print("Would you like to: ")
        print("1. Add an employee.")
        print("2. Change the risk level.")
        print("3. Change the max assets allowed.")
        print("4. Back.")
        answer = input("1,2,3,4: ")
        if answer == 1:
            self.addEmployee()
        elif answer == 2:
            answer = input("What level, high, med, low? ")
            if answer == 'high' or answer == 'High':
                self.intlevel = 3
            if answer == 'med' or answer == 'Med':
                self.intlevel = 2
            if answer == 'low' or answer == 'Low':
                self.intlevel = 1
        elif answer == 3:
            answer = input("How much capital max to deploy? ")
            self.maxAssets = int(answer)

class AnalysisDesk(Desk):
    def __init__(self):
        self.worklevel = 2
        self.project = None
        self.bonus = 0
        Desk.__init__(self)
        self.employeeCost = 3
    
    def addAnalyst(self):
        return
    
    def addAssoc(self):
        return

    def runDesk(self,market):
        self.profits = 0
        self.cashflow = 0
        if self.project is None:
            return
        else:
            if self.worklevel == 1:
                self.project.size -= self.employees[0]*50
            elif self.worklevel == 2:
                self.project.size -= self.employees[0]*100
                self.bonus += 2*self.employees[0]
            elif self.worklevel == 3:
                self.project.size -= self.employees[0]*133
                self.bonus += 3*self.employees[0]
            if self.project.size <= 0:
                self.profits += self.project.fee
                self.profits -= self.bonus
                self.bonus = 0
                self.cashflow = self.profits
                self.project = None
                self.profits -= self.employeeCost
                self.cashflow -= self.employeeCost
                return
            self.project.wait -= 1
            if self.project.wait <= 0:
                self.profits -= self.project.missfee
                self.cashflow -= self.project.missfee
                self.project = None
        self.profits -= self.employeeCost
        self.cashflow -= self.employeeCost
                
class AccountManagement(Desk):
    def __init__(self):
        self.setting = 1
        self.size = 1
        Desk.__init__(self)
        self.projects = []
    
    def addAnalyst(self):
        self.employees[0] += 1
    
    def addAssoc(self):
        self.employees[1] += 1
    
    def runDesk(self,market):
        if self.setting == 1:
            if randint(0,100) < (self.employees[0]-self.size)*17 + 33:
                newProject = Project(self.size)
                self.projects.append(newProject)
        elif self.setting == 2 and not (not self.projects):
            self.projects[0].wait += 0.5
        for i,project in enumerate(self.projects):
            project.wait -= 1
            if project.wait <= 0:
                self.projects.pop(i)
        
class EquityDesk(Desk):
    name = "equity"
    def __init__(self):
        self.maxAssets = 0
        self.portfolio = 0
        self.desirePortfolio = 0
        self.changed = 0
        Desk.__init__(self)
        self.employeeCost = 5
    
    def addAnalyst(self):
        self.employees[0] += 1
        self.employeeCost += 2
    
    def addAssoc(self):
        self.employees[1] += 1
        self.employeeCost += 5
    
    def runDesk(self,market):
        self.cashflow = 0
        self.profits = 0
        self.maxAssets = 10000*(self.employees[0]+self.employees[1])
        if self.changed == 1:
            if self.desirePortfolio != 0:
                self.changePortfolio(0)
            else:
                self.changed = 0
                self.assetChange = 0
        else:
            self.assetChange = 0
        if self.portfolio > self.maxAssets:
            self.portfolio = self.maxAssets
        if market == 3:
            self.profits = self.portfolio*0.05
            self.cashflow = self.portfolio*0.01
            self.portfolio = self.portfolio*1.04
            if self.portfolio > self.maxAssets:
                self.cashflow += self.portfolio - self.maxAssets
                self.portfolio = self.maxAssets
        elif market == 2:
            self.profits = self.portfolio*0.02
            self.cashflow = self.portfolio*0.005
            self.portfolio = self.portfolio*1.015
            if self.portfolio > self.maxAssets:
                self.cashflow += self.portfolio - self.maxAssets
                self.portfolio = self.maxAssets
        elif market == 1:
            self.profits = -self.portfolio*0.05
            self.cashflow = 0
            self.portfolio = self.portfolio*0.95
        
        self.RWAcalc()

    def RWAcalc(self):
        self.RWA = self.portfolio*0.5

    def changePortfolio(self,change):
        self.desirePortfolio += change
        if self.desirePortfolio >= 500*self.employees[0]:
            self.assetChange = -500*self.employees[0]
            self.portfolio += 500*self.employees[0]
            self.desirePortfolio -= 500*self.employees[0]
        else:
            self.assetChange = -self.desirePortfolio
            self.portfolio += self.desirePortfolio
            self.desirePortfolio = 0
        self.changed = 1
        
    def editPortfolio(self,change):
        self.desirePortfolio += change
        self.changed = 1
    
class FixedIncomeDesk(Desk):
    name = "fixed income"
    def __init__(self):
        Desk.__init__(self)
        self.employeeCost = 5
        self.changed = 0
        self.maxAssets = 1000000000
    
    def buy(self, notional):
        if self.changed == 1:
            print("Already bought.")
            return
        if notional > 10000*self.employees[0]:
            print("Cannot buy that much.")
            print("Can only buy " + str(10000*self.employees[0]))
            return
        answer = input("What risk level? ")
        if answer == '1':
            answer = input("What maturity? ")
            if float(answer) < 16:
                print("Can only buy bonds with higher than 4 year maturities.")
                return
            interest = (-1*exp(-float(answer)/20.0+2.0)+10)
            interest = interest/100
            bond = Bond('bond',notional,1,interest,float(answer))
            self.assets.append(bond)
            self.changed = 1
            self.assetChange = notional
        elif answer == '2':
            answer = input("What maturity? ")
            if float(answer) < 16:
                print("Can only buy bonds with higher than 4 year maturities.")
                return
            interest = (-1*exp(-float(answer)/20.0+2.0)+13)
            interest = interest/100
            bond = Bond('bond',notional,2,interest,float(answer))
            self.assets.append(bond)
            self.changed = 1
            self.assetChange = notional
        elif answer == '3':
            answer = input("What maturity? ")
            if float(answer) < 16:
                print("Can only buy bonds with higher than 4 year maturities.")
                return
            interest = (-1*exp(-float(answer)/20.0+2.0)+16)
            interest = interest/100
            bond = Bond('bond',notional,3,interest,float(answer))
            self.assets.append(bond)
            self.changed = 1
            self.assetChange = notional
    
    def assetChanges(self):
        if self.changed == 1:
            self.changed = 0
            track = self.assetChange
            self.assetChange = 0
            return track
        else:
            return 0
    
    def RWAcalc(self):
        self.RWA = 0
        self.capital = 0
        for asset in self.assets:
            self.capital += asset.notional
            self.RWA += (11-2*asset.risk)*asset.notional/10


def bankTest(scenario):
    box = Bank('box')
    desk1 = Teller()
    desk2 = MortgageDesk()
    box.desks.append(desk1)
    box.desks.append(desk2)
    box.desks[1].employees[0] = 2
    box.desks[1].employeeCost = 2
    for i in range(30):
        if scenario == 1:
            box.desks[1].intlevel = 3
        
        box.runGame()
        
        if scenario == 2:
            if box.market == 1:
                box.desks[1].intlevel = 3
            elif box.market == 3:
                box.desks[1].intlevel = 1
        
        if box.risk > 2:
            print("Too risky!")
        
        if box.capital < 500:
            print("Too little capital!")
    
    #eq = EquityDesk()
    #box.desks.append(eq)
    fi = FixedIncomeDesk()
    box.desks.append(fi)
    return box
    

def noDep():
    box = Bank()
    desk1 = MortgageDesk()
    box.desks.append(desk1)
    box.desks[0].maxAssets = 1000
    for i in range(40):
        box.runGame()
    return box
    
def ibTest():
    box = Bank()
    desk1 = AccountManagement()
    desk2 = AnalysisDesk()
    box.desks.append(desk1)
    box.desks.append(desk2)
    for i in range(20):
        box.runGame()
        if len(box.desks[0].projects) == 1:
            box.desks[0].setting = 2
        else:
            box.desks[0].setting = 1
    return box
    

def EQCheck():
    box = Bank('Box')
    box.desks.append(EquityDesk())
    box.desks[0].editPortfolio(1000)
    box.runGame()
    return box

def startGame():
    print("Hello and welcome to Bank Tycoon!")
    name = input("What would you like to name your bank? ")
    bank = Bank(name)
    print("Your bank starts with: ")
    bank.stats()
    print("There are many choices for you to make. Would you like to be: ")
    print("A retail bank with a teller that issues mortgages?")
    print("A pure mortgage lender with solely its own capital to worry about?")
    print("A trading firm which makes leveraged bets on the market direction?")
    print("Or any conceivable combination...")
    
    gameOver = 0
    while gameOver == 0:
        print("What would you like to do?")
        print("1. Go to next quarter.")
        print("2. Get your bank stats.")
        print("3. Start a desk.")
        i = 4
        for desk in bank.desks:
            print("%.0f. Edit your %s desk." %(i,desk.name))
            i += 1
        answer = input("What would you like to do? (1,2,3...) ")
        if answer == "1":
            bank.runGame()
        elif answer == "2":
            bank.stats()
        elif answer == "3":
            bank.startDesk()
        else:
            bank.desks[int(answer)-4].edit()
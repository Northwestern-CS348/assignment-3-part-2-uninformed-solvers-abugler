from game_master import GameMaster
from read import *
from util import *

class TowerOfHanoiGame(GameMaster):

    def __init__(self):
        super().__init__()
        
    def produceMovableQuery(self):
        """
        See overridden parent class method for more information.

        Returns:
             A Fact object that could be used to query the currently available moves
        """
        return parse_input('fact: (movable ?disk ?init ?target)')

    def getGameState(self):
        """
        Returns a representation of the game in the current state.
        The output should be a Tuple of three Tuples. Each inner tuple should
        represent a peg, and its content the disks on the peg. Disks
        should be represented by integers, with the smallest disk
        represented by 1, and the second smallest 2, etc.

        Within each inner Tuple, the integers should be sorted in ascending order,
        indicating the smallest disk stacked on top of the larger ones.

        For example, the output should adopt the following format:
        ((1,2,5),(),(3, 4))

        Returns:
            A Tuple of Tuples that represent the game state
        """

        peg1 = []
        for fact in self.kb.facts:
            if fact.statement.predicate.__str__().upper() == "ON" and fact.statement.terms[1].__str__() == "peg1":
                disknum = int(fact.statement.terms[0].__str__()[4:])
                peg1 = peg1 + [disknum]
        peg1 = self.sort(peg1)

        peg2 = []
        for fact in self.kb.facts:
            if fact.statement.predicate.__str__().upper() == "ON" and fact.statement.terms[1].__str__() == "peg2":
                disknum = int(fact.statement.terms[0].__str__()[4:])
                peg2 = peg2 + [disknum]
        peg2 = self.sort(peg2)

        peg3 = []
        for fact in self.kb.facts:
            if fact.statement.predicate.__str__().upper() == "ON" and fact.statement.terms[1].__str__() == "peg3":
                disknum = int(fact.statement.terms[0].__str__()[4:])
                peg3 = peg3 + [disknum]
        peg3 = self.sort(peg3)


        ### student code goes here
        result = ()
        result = (tuple(peg1),)
        result = result + (tuple(peg2),)
        result = result + (tuple(peg3),)
        return result

    @staticmethod
    def sort(lst):
        for x in range(0, len(lst)):
            for y in range(x+1, len(lst)):
                if lst[x] > lst[y]:
                    temp = lst[y]
                    lst[y] = lst[x]
                    lst[x] = temp
        return lst

    def makeMove(self, movable_statement):
        """
        Takes a MOVABLE statement and makes the corresponding move. This will
        result in a change of the game state, and therefore requires updating
        the KB in the Game Master.

        The statement should come directly from the result of the MOVABLE query
        issued to the KB, in the following format:
        (movable disk1 peg1 peg3)

        Args:
            movable_statement: A Statement object that contains one of the currently viable moves

        Returns:
            None
        """
        #First the destination top statement is removed
        #or is none exist, the empty statement is removed
        m = movable_statement
        dstTop = parse_input("fact: (TOP " + m.terms[2].__str__() + " ?x)")
        dstBindings = self.kb.kb_ask(dstTop)
        if (dstBindings):
            self.kb.kb_retract(Fact(instantiate(dstTop.statement, dstBindings[0])))
        else:
            self.kb.kb_retract(Fact(Statement(["EMPTY", m.terms[2]])))

        #The disk being moved has its TOP and ON statements retracted
        self.kb.kb_retract(Fact(Statement(["TOP", m.terms[1], m.terms[0]])))
        self.kb.kb_retract(Fact(Statement(["ON", m.terms[0], m.terms[1]])))

        #The disk under the disk that has been moved is now the top disk
        for fact in self.kb.facts:
            if fact.statement.predicate.__str__() == "ON" and fact.statement.terms[1] == m.terms[1]:
                overFact = parse_input("fact: (OVER ?y " + fact.statement.terms[0].__str__() + ")")
                if not self.kb.kb_ask(overFact):
                    self.kb.kb_add(Fact(Statement(["TOP", m.terms[1], fact.statement.terms[0]])))
                    break

        #if a disk cannot be found for the peg, the peg is empty
        if not self.kb.kb_ask(parse_input("fact: (TOP " + m.terms[1].__str__() + " ?x)")):
            self.kb.kb_add(Fact(Statement(["EMPTY", m.terms[1]])))

        #the dst of the disk has its top and on statements added
        self.kb.kb_add(Fact(Statement(["TOP", m.terms[2], m.terms[0]])))
        self.kb.kb_add(Fact(Statement(["ON", m.terms[0], m.terms[2]])))





    def reverseMove(self, movable_statement):
        """
        See overridden parent class method for more information.

        Args:
            movable_statement: A Statement object that contains one of the previously viable moves

        Returns:
            None
        """
        pred = movable_statement.predicate
        sl = movable_statement.terms
        newList = [pred, sl[0], sl[2], sl[1]]
        self.makeMove(Statement(newList))

class Puzzle8Game(GameMaster):

    def __init__(self):
        super().__init__()

    def produceMovableQuery(self):
        """
        Create the Fact object that could be used to query
        the KB of the presently available moves. This function
        is called once per game.

        Returns:
             A Fact object that could be used to query the currently available moves
        """
        return parse_input('fact: (movable ?piece ?initX ?initY ?targetX ?targetY)')

    def getGameState(self):
        """
        Returns a representation of the the game board in the current state.
        The output should be a Tuple of Three Tuples. Each inner tuple should
        represent a row of poss on the board. Each pos should be represented
        with an integer; the empty space should be represented with -1.

        For example, the output should adopt the following format:
        ((1, 2, 3), (4, 5, 6), (7, 8, -1))

        Returns:
            A Tuple of Tuples that represent the game state
        """
        state = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        for fact in self.kb.facts:
            if fact.statement.predicate.__str__() == "POSITION":
                posx = int(fact.statement.terms[1].__str__()[3:])
                posy = int(fact.statement.terms[2].__str__()[3:])
                state[posy-1][posx-1] = int(fact.statement.terms[0].__str__()[4:])

        state = (tuple(state[0]), tuple(state[1]), tuple(state[2]))
        return state

    def makeMove(self, movable_statement):
        """
        Takes a MOVABLE statement and makes the corresponding move. This will
        result in a change of the game state, and therefore requires updating
        the KB in the Game Master.

        The statement should come directly from the result of the MOVABLE query
        issued to the KB, in the following format:
        (movable tile3 pos1 pos3 pos2 pos3)

        Args:
            movable_statement: A Statement object that contains one of the currently viable moves

        Returns:
            None
        """
        m = movable_statement
        self.kb.kb_retract(Fact(Statement(["POSITION", "tile-1", m.terms[3], m.terms[4]])))
        self.kb.kb_retract(Fact(Statement(["POSITION", m.terms[0], m.terms[1], m.terms[2]])))
        retractedMovable = parse_input("fact: (movable ?x ?y ?z " + m.terms[3].__str__() + " " + m.terms[4].__str__()+")")
        bindings = self.kb.kb_ask(retractedMovable)
        for binding in bindings:
            self.kb.kb_retract(Fact(instantiate(retractedMovable.statement, binding)))
        self.kb.kb_add(Fact(Statement(["POSITION", m.terms[0], m.terms[3], m.terms[4]])))
        self.kb.kb_add(Fact(Statement(["POSITION", "tile-1", m.terms[1], m.terms[2]])))

        if m.terms[1].__str__() == "pos1" and m.terms[2].__str__() == "pos1":
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos2 pos1))"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact:(movable ?x pos2 pos1 pos1 pos1)").statement, binding[0])))
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos1 pos2)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos1 pos2 pos1 pos1)").statement, binding[0])))
        elif m.terms[1].__str__() == "pos3" and m.terms[2].__str__() == "pos1":
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos2 pos1)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos2 pos1 pos3 pos1)").statement, binding[0])))
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos3 pos2)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos3 pos2 pos3 pos1)").statement, binding[0])))
        elif m.terms[1].__str__() == "pos1" and m.terms[2].__str__() == "pos3":
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos1 pos2)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos1 pos2 pos1 pos3)").statement, binding[0])))
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos2 pos3)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos2 pos3 pos1 pos3)").statement, binding[0])))
        elif m.terms[1].__str__() == "pos3" and m.terms[2].__str__() == "pos3":
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos3 pos2)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos3 pos2 pos3 pos3)").statement, binding[0])))
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos2 pos3)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos2 pos3 pos3 pos3)").statement, binding[0])))
        elif m.terms[1].__str__() == "pos2" and m.terms[2].__str__() == "pos1":
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos1 pos1)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos1 pos1 pos2 pos1)").statement, binding[0])))
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos3 pos1)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos3 pos1 pos2 pos1)").statement, binding[0])))
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos2 pos2)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos2 pos2 pos2 pos1)").statement, binding[0])))
        elif m.terms[1].__str__() == "pos1" and m.terms[2].__str__() == "pos2":
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos1 pos1)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos1 pos1 pos1 pos2)").statement, binding[0])))
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos2 pos2)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos2 pos2 pos1 pos2)").statement, binding[0])))
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos1 pos3)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos1 pos3 pos1 pos2)").statement, binding[0])))
        elif m.terms[1].__str__() == "pos3" and m.terms[2].__str__() == "pos2":
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos2 pos2)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos2 pos2 pos3 pos2)").statement, binding[0])))
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos3 pos3)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos3 pos3 pos3 pos2)").statement, binding[0])))
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos3 pos1)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos3 pos1 pos3 pos2)").statement, binding[0])))
        elif m.terms[1].__str__() == "pos2" and m.terms[2].__str__() == "pos3":
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos1 pos3)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos1 pos3 pos2 pos3)").statement, binding[0])))
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos3 pos3)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos3 pos3 pos2 pos3)").statement, binding[0])))
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos2 pos2)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos2 pos2 pos2 pos3)").statement, binding[0])))
        elif m.terms[1].__str__() == "pos2" and m.terms[2].__str__() == "pos2":
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos1 pos2)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos1 pos2 pos2 pos2)").statement, binding[0])))
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos2 pos1)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos2 pos1 pos2 pos2)").statement, binding[0])))
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos2 pos3)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos2 pos3 pos2 pos2)").statement, binding[0])))
            binding = self.kb.kb_ask(parse_input("fact: (POSITION ?x pos3 pos2)"))
            self.kb.kb_add(Fact(instantiate(parse_input("fact: (movable ?x pos3 pos2 pos2 pos2)").statement, binding[0])))

        badMovable = self.kb.kb_ask(parse_input("fact: (movable tile-1 ?a ?b ?c ?d)"))
        if badMovable:
            self.kb.kb_retract(Fact(instantiate(parse_input("fact: (movable tile-1 ?a ?b ?c ?d)").statement, badMovable[0])))





    def reverseMove(self, movable_statement):
        """
        See overridden parent class method for more information.

        Args:
            movable_statement: A Statement object that contains one of the previously viable moves

        Returns:
            None
        """
        pred = movable_statement.predicate
        sl = movable_statement.terms
        newList = [pred, sl[0], sl[3], sl[4], sl[1], sl[2]]
        self.makeMove(Statement(newList))

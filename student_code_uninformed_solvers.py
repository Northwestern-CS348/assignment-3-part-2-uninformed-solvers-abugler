import cmd

from solver import *

class SolverDFS(UninformedSolver):
    def __init__(self, gameMaster, victoryCondition):
        super().__init__(gameMaster, victoryCondition)

    listOfStates = []
    listOfMovables = [];
    def solveOneStep(self):
        """
        Go to the next state that has not been explored. If a
        game state leads to more than one unexplored game states,
        explore in the order implied by the GameMaster.getMovables()
        function.
        If all game states reachable from a parent state has been explored,
        the next explored state should conform to the specifications of
        the Depth-First Search algorithm.

        Returns:
            True if the desired solution state is reached, False otherwise
        """
        if not self.gm.getGameState() == self.victoryCondition:
            self.listOfMovables.append(self.gm.getMovables())
            moves = self.gm.getMovables()
            #make a move
            self.gm.makeMove(moves[len(self.currentState.children)])
            self.currentState.children.append(GameState(self.gm.getGameState(), self.currentState.depth+1, moves[len(self.currentState.children)]))
            self.currentState.children[len(self.currentState.children)-1].parent = self.currentState
            self.currentState = self.currentState.children[len(self.currentState.children)-1]

            # find the root
            root = SolverDFS.getRootNote(self.currentState)
            # checks if this state is unique (if this is a dead end)
            if not SolverDFS.isUniqueState(self.currentState, root, self.listOfStates):
                self.findNearestNode()

        self.listOfStates.append(self.currentState.state)
        return self.gm.getGameState() == self.victoryCondition


    #find the nearest node
    def findNearestNode(self):
        #travels up to the parent
        self.gm.reverseMove(self.currentState.requiredMovable)
        self.currentState = self.currentState.parent

        moves = self.gm.getMovables()
        #checks if theres any children left
        if len(self.currentState.children) < len(moves):
            #moves to the next child
            self.gm.makeMove(moves[len(self.currentState.children)])
            self.currentState.children.append(GameState(self.gm.getGameState(), self.currentState.depth+1, moves[len(self.currentState.children)]))
            self.currentState.children[len(self.currentState.children) - 1].parent = self.currentState
            self.currentState = self.currentState.children[len(self.currentState.children) - 1]

            #checks if the child is unique
            if SolverDFS.isUniqueState(self.currentState, SolverDFS.getRootNote(self.currentState), []):
                return
            #if it ain't, travel back up the tree
            else:
                self.findNearestNode()
        else:
            self.findNearestNode()

    # checks if the game state is unique in the tree
    # Precondition: the "grandfather node" must be the root node of the tree
    @staticmethod
    def isUniqueState(gameState, grandFatherNode, listOfStates):
        if gameState.depth > 200:
            return not gameState.state in listOfStates
        #checks if the states are the same, and checks if they aren't at the same location at the tree
        if gameState.state == grandFatherNode.state and not SolverDFS.sameParents(gameState, grandFatherNode):
            return False
        if not grandFatherNode.children:
            return True
        #calls isUnique state on all children of grandFatherNode, and stores the results in results
        results = [SolverDFS.isUniqueState(gameState, child, listOfStates) for child in grandFatherNode.children]
        #if a False exists in results, return false
        return False not in results

    #checks if all parents are the same is two game states
    @staticmethod
    def sameParents(state1, state2):
        if state1.parent and state2.parent:
            return state1.parent == state2.parent and SolverDFS.sameParents(state1.parent, state2.parent)
        if (not state1.parent or not state2.parent) and (state1.parent or state2.parent):
            return False
        return True



    #gets root node of a tree
    @staticmethod
    def getRootNote(gameState):
        if (gameState.depth > 300):
            print("breakpoint!")
        if gameState.parent:
            return SolverDFS.getRootNote(gameState.parent)
        else:
            return gameState
class SolverBFS(UninformedSolver):
    def __init__(self, gameMaster, victoryCondition):
        super().__init__(gameMaster, victoryCondition)
        siblingList = []
        siblingIndex = []

    def solveOneStep(self):
        """
        Go to the next state that has not been explored. If a
        game state leads to more than one unexplored game states,
        explore in the order implied by the GameMaster.getMovables()
        function.
        If all game states reachable from a parent state has been explored,
        the next explored state should conform to the specifications of
        the Breadth-First Search algorithm.

        Returns:
            True if the desired solution state is reached, False otherwise
        """

        #checks if victory is found
        if self.currentState.state == self.victoryCondition:
            return

        #if the parent exists, and the parent has children (aka, the parent has the current state as a child)
        if self.currentState.parent and self.currentState.parent.children.__len__():
            self.gm.reverseMove(self.currentState.requiredMovable)
            self.currentState = self.currentState.parent
        moves = self.gm.getMovables()

        #if all moves have been expended...
        if len(moves) <= self.currentState.nextChildToVisit:
            #find a new parent node to expand on
            newParent = SolverBFS.findSibling(self, self.currentState.depth, self.currentState)
            if newParent:
                SolverBFS.relocateGM(self, newParent)
                self.currentState = newParent
                moves = self.gm.getMovables()
            else:#if a new parent cannot be found, DIG DEEPER
                newParent = SolverBFS.findFirstChild(self, self.currentState.depth + 1)
                SolverBFS.relocateGM(self, newParent)
                self.currentState = newParent
                moves = self.gm.getMovables()

        #make the move
        self.gm.makeMove(moves[self.currentState.nextChildToVisit])
        newChild = GameState(self.gm.getGameState(), self.currentState.depth+1,
                                                    moves[self.currentState.nextChildToVisit])
        self.currentState.children.append(newChild)
        self.currentState.children[self.currentState.nextChildToVisit].parent = self.currentState
        self.currentState.nextChildToVisit += 1
        self.currentState = self.currentState.children[self.currentState.nextChildToVisit - 1]
        #if unique, return
        if SolverDFS.isUniqueState(newChild, SolverDFS.getRootNote(self.currentState), []):
            return self.gm.getGameState() == self.victoryCondition
        else:#if it is not unique, set to "dead end", and find the next node
            self.currentState.state = "Dead End"
            return SolverBFS.solveOneStep(self)

    #finds a sibling that has no children
    def findSibling(self, depth, root):
        if depth == 0:
            return False
        root = root.parent
        dst = depth - root.depth
        siblingList = self.listOfSiblings(dst, root)
        for sibling in siblingList:
            if len(sibling.children) == 0 and sibling.state != "Dead End":
                return sibling

        if isinstance(root.parent, GameState):
            return self.findSibling(depth, root)
        return False

    #helper for findSibling
    def listOfSiblings(self, dst, root):
        if dst > 1:
            siblinglist = []
            for child in root.children:
                siblinglist = siblinglist + self.listOfSiblings(dst - 1, child)
            return siblinglist
        elif dst == 1:
            return root.children
        else:
            return []

    #relocates the GM to a new location
    def relocateGM(self, dst):
        reverseMoves = []
        while self.currentState.parent:
            reverseMoves.append(self.currentState.requiredMovable)
            self.currentState = self.currentState.parent
        movesToMake = []
        while dst.parent:
            movesToMake.insert(0, dst.requiredMovable)
            dst = dst.parent
        for move in reverseMoves:
            self.gm.reverseMove(move)
        for move in movesToMake:
            self.gm.makeMove(move)


    def findFirstChild(self, depth):
        root = SolverDFS.getRootNote(self.currentState)
        while root.depth != depth:
            root = SolverBFS.findSiblingWithChildren(self, root.depth + 1, root)
        return SolverBFS.findSibling(self, depth, root)

    def findSiblingWithChildren(self, depth, root):
        if depth == 1:
            return root.children[0]
        root = root.parent
        dst = depth - root.depth
        siblingList = self.listOfSiblings(dst, root)
        for sibling in siblingList:
            if sibling.state != "Dead End":
                return sibling

        if isinstance(root.parent, GameState):
            return self.findSibling(depth, root)
        return False

# The hex AI agent was a project I worked on with 3 other students. The goal of the project was to implement an Agent that can find the shortest path to a winning stage, in a game of Hex 11x11. The project is uploaded from my personal Gitlab.

We used Minimax with alpha-beta pruning:
Why use α-β Pruning?  
Hex has a large branching factor (Chess branch factor < Hex branch factor)
So we employ Minimax with α-β Pruning to improve performance 
Reduces branching factor by ignoring branches that will not give an improved result 
Further Addition:
Use arrays of optimal board states to reduce branch factor during minimax

And heurustics:
The heuristic utilises a shortest path algorithm to analyse how many stones the AI and the opponent need to place to complete their chains, returning the difference of the two values.
This is a value we want to minimise as moves that increase the agent’s influence over the board while decreasing the opponents are moves’ which decrease the number of stones the agent needs to complete a chain while increasing the number of stones the opponent needs.
Return Value = Number of Stones Agents Must Place - Number of Stones Opponent Must Place


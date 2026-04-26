import { GameState, Player, CellValue } from './Game';

/**
 * Checks if there is a winner on the board.
 * @param cells The array representing the cells of the board.
 * @returns The winning player ('X' or 'O') or null if no winner.
 */
export function checkWinner(cells: CellValue[]): Player | null {
    const lines = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6],
    ];

    for (const [a, b, c] of lines) {
        const valA = cells[a];
        const valB = cells[b];
        const valC = cells[c];

        if (valA !== null && valA === valB && valA === valC) {
            return valA;
        }
    }
    return null;
}

/**
 * Checks if the game is a draw (no empty cells left and no winner).
 * @param cells The array representing the cells of the board.
 * @returns True if the game is a draw, false otherwise.
 */
export function checkDraw(cells: CellValue[]): boolean {
    return !cells.includes(null);
}

/**
 * Makes a move on the board.
 * @param currentState The current game state.
 * @param index The index of the cell to play in.
 * @returns A new GameState object after the move, or null if the move is invalid.
 */
export function makeMove(currentState: GameState, index: number): GameState | null {
    const { board, currentPlayer, status } = currentState;

    if (status !== 'playing' || board.cells[index] !== null) {
        return null; // Game is over or cell is already taken
    }

    // 1. Create a new state immutably
    const newCells = [...board.cells];
    newCells[index] = currentPlayer;

    let newStatus: 'playing' | 'win' | 'draw' = 'playing';
    let newWinner: Player | null = null;

    // 2. Check for winner
    const winner = checkWinner(newCells);
    if (winner) {
        newStatus = 'win';
        newWinner = winner;
    }
    // 3. Check for draw if no winner
    else if (checkDraw(newCells)) {
        newStatus = 'draw';
    }

    // 4. Determine next player
    const nextPlayer: Player = currentPlayer === 'X' ? 'O' : 'X';

    const nextState: GameState = {
        board: {
            cells: newCells,
        },
        currentPlayer: newStatus === 'playing' ? nextPlayer : currentPlayer, // Keep current player if game ended
        status: newStatus,
        winner: newWinner,
    };

    return nextState;
}
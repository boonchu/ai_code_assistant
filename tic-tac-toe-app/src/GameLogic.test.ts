import { checkWinner, checkDraw, makeMove } from './GameLogic';
import { GameState, Player, CellValue } from './Game';

describe('Game Logic Tests', () => {
    const initialCells: [Player | null, Player | null, Player | null, Player | null, Player | null, Player | null, Player | null, Player | null, Player | null] = [null, null, null, null, null, null, null, null, null];
    let initialState: GameState;

    beforeEach(() => {
        initialState = {
            board: { cells: [...initialCells] },
            currentPlayer: 'X',
            status: 'playing',
            winner: null,
        };
    });

    describe('checkWinner', () => {
        test('should return X when X wins horizontally (0, 1, 2)', () => {
            const cells: CellValue[] = ['X', 'X', 'X', null, null, null, null, null, null];
            expect(checkWinner(cells)).toBe('X');
        });

        test('should return O when O wins vertically (0, 3, 6)', () => {
            const cells: CellValue[] = ['O', null, null, 'O', null, null, 'O', null, null];
            expect(checkWinner(cells)).toBe('O');
        });

        test('should return X when X wins diagonally (0, 4, 8)', () => {
            const cells: CellValue[] = ['X', null, null, null, 'X', null, null, null, 'X'];
            expect(checkWinner(cells)).toBe('X');
        });

        test('should return null when there is no winner', () => {
            const cells: CellValue[] = ['X', 'O', 'X', 'O', null, null, null, null, null];
            expect(checkWinner(cells)).toBeNull();
        });
    });

    describe('checkDraw', () => {
        test('should return true when all cells are filled and no winner', () => {
            const cells: CellValue[] = ['X', 'O', 'X', 'X', 'O', 'O', null, null, null];
            const filledCells: CellValue[] = ['X', 'O', 'X', 'X', 'O', 'O', 'X', 'O', 'X'];
            expect(checkDraw(filledCells)).toBe(true);
        });

        test('should return false when there are empty cells', () => {
            const cells: CellValue[] = ['X', 'O', null, null, null, null, null, null, null];
            expect(checkDraw(cells)).toBe(false);
        });
    });

    describe('makeMove', () => {
        test('should return new state with correct player and cell filled', () => {
            const nextState = makeMove(initialState, 4); // Center move
            expect(nextState).not.toBeNull();
            expect(nextState!.board.cells[4]).toBe('X');
            expect(nextState!.currentPlayer).toBe('O');
            expect(nextState!.status).toBe('playing');
        });

        test('should transition to win state correctly', () => {
            // Setup for X win at (0, 1, 2)
            initialState.board.cells = ['X', 'X', null, null, null, null, null, null, null];
            initialState.currentPlayer = 'O'; // Next turn is O, but we are testing X's winning move

            const winningStateSetup: GameState = {
                board: { cells: ['X', 'X', null, null, null, null, null, null, null] },
                currentPlayer: 'X',
                status: 'playing',
                winner: null,
            };

            const finalState = makeMove(winningStateSetup, 2); // X plays at index 2

            expect(finalState).not.toBeNull();
            expect(finalState!.winner).toBe('X');
            expect(finalState!.status).toBe('win');
        });

        test('should transition to draw state correctly', () => {
            // Setup for a full board draw (simplified for testing)
            const drawCells: CellValue[] = ['X', 'O', 'X', 'O', 'X', 'O', 'O', 'X', 'O'];
            const drawState: GameState = {
                board: { cells: drawCells },
                currentPlayer: 'X',
                status: 'playing',
                winner: null,
            };

            // Attempting to make a move on a full board
            const finalState = makeMove(drawState, 0);

            expect(finalState).not.toBeNull();
            expect(finalState!.status).toBe('draw');
            expect(finalState!.winner).toBeNull();
        });

        test('should return null for invalid move (already taken cell)', () => {
            const filledState: GameState = {
                board: { cells: ['X', 'O', null, null, null, null, null, null, null] },
                currentPlayer: 'X',
                status: 'playing',
                winner: null,
            };
            // Try to play on cell 0 which is 'X'
            const result = makeMove(filledState, 0);
            expect(result).toBeNull();
        });
    });
});
export type Player = 'X' | 'O';
export type CellValue = Player | null;
import { makeMove } from './GameLogic';

export interface Board {
    cells: CellValue[];
}

export interface GameState {
    board: Board;
    currentPlayer: Player;
    status: 'playing' | 'win' | 'draw';
    winner: Player | null;
}

export const INITIAL_STATE: GameState = {
    board: {
        cells: Array(9).fill(null),
    },
    currentPlayer: 'X',
    status: 'playing',
    winner: null,
};

export function getNextState(currentState: GameState, index: number): GameState | null {
    const nextState = makeMove(currentState, index);
    return nextState;
}

export function resetGame(): GameState {
    return INITIAL_STATE;
}
import React, { useState, useCallback } from 'react';
import { GameState, INITIAL_STATE, getNextState, resetGame, CellValue } from './Game';

// Define props interface for clarity
interface TicTacToeProps {
    // Future props if needed (e.g., onGameEnd)
}

const TicTacToe: React.FC<TicTacToeProps> = () => {
    const [gameState, setGameState] = useState<GameState>(INITIAL_STATE);

// Handler for a user making a move
const handleCellClick = useCallback((index: number) => {
    if (gameState.status !== 'playing' || gameState.board.cells[index] !== null) {
        return;
    }

    // Only allow the current player to move
    if (gameState.currentPlayer !== 'X' && gameState.currentPlayer !== 'O') {
        return;
    }

    const nextState = getNextState(gameState, index);

    if (nextState) {
        setGameState(nextState);
    }
}, [gameState]);

    // Handler to restart the game
    const handleReset = useCallback(() => {
        setGameState(resetGame());
    }, []);

    // Helper function to render the content of a cell
    const renderCellContent = (cellValue: CellValue): string | null => {
        if (cellValue === 'X') return 'X';
        if (cellValue === 'O') return 'O';
        return null;
    };

// Component to render a single cell
const Cell: React.FC<{ value: CellValue, onClick: () => void }> = ({ value, onClick }) => {
    let style = styles.cellButton;
    if (value === 'O') {
        style = { ...styles.cellButton, color: 'lightgreen' }; // Custom style for O
    } else if (value === 'X') {
        style = { ...styles.cellButton, color: 'red' }; // Custom style for X
    }
    return (
        <button
            onClick={onClick}
            style={style}
            disabled={value !== null}
        >
            {renderCellContent(value)}
        </button>
    );
};

    // --- Game Status Display ---
    const getStatusMessage = () => {
        if (gameState.status === 'win') {
            return `Player ${gameState.winner} wins!`;
        } else if (gameState.status === 'draw') {
            return 'Game is a Draw!';
        } else {
            return `Current turn: Player ${gameState.currentPlayer}`;
        }
    };

    return (
        <div style={styles.container}>
            <h1>Tic-Tac-Toe</h1>
            <p style={styles.statusText}>{getStatusMessage()}</p>

            <div style={styles.board}>
                {gameState.board.cells.map((cellValue, index) => (
                    <Cell
                        key={index}
                        value={cellValue}
                        onClick={() => handleCellClick(index)}
                    />
                ))}
            </div>

            <button onClick={handleReset} style={styles.resetButton}>
                Reset Game
            </button>
        </div>
    );
};

// Basic inline styles for demonstration purposes
const styles: { [key: string]: React.CSSProperties } = {
    container: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '20px',
        fontFamily: 'sans-serif',
    },
    board: {
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 100px)',
        gridTemplateRows: 'repeat(3, 100px)',
        gap: '5px',
        margin: '20px 0',
    },
    cellButton: {
        fontSize: '48px',
        fontWeight: 'bold',
        width: '100px',
        height: '100px',
        border: '1px solid #ccc',
        cursor: 'pointer',
        backgroundColor: '#f9f9f9',
        transition: 'background-color 0.2s',
    },
    statusText: {
        fontSize: '1.2em',
        marginBottom: '15px',
        fontWeight: 'bold',
    },
    resetButton: {
        padding: '10px 20px',
        fontSize: '1em',
        cursor: 'pointer',
        backgroundColor: '#007bff',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
        marginTop: '20px',
    }
};

export default TicTacToe;
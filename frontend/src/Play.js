import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams } from 'react-router-dom';

function Play() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialGameCode = searchParams.get('code') || '';
  const initialName = searchParams.get('name') || '';

  const [gameCode, setGameCode] = useState(initialGameCode);
  const [name, setName] = useState(initialName);
  const [codeEntered, setCodeEntered] = useState(!!initialGameCode);
  const [gameDetails, setGameDetails] = useState(null);
  const [joined, setJoined] = useState(!!initialGameCode && !!initialName);
  const [prompt, setPrompt] = useState('');
  const [guess, setGuess] = useState('');

  const handleCodeChange = (e) => {
    const newGameCode = e.target.value.slice(0, 4);
    setGameCode(newGameCode);

    if (newGameCode.length === 4) {
      setCodeEntered(true);
      setSearchParams({ code: newGameCode, name });
    }
  };

  const handleNameChange = (e) => {
    setName(e.target.value);
  };

  const handleJoinGame = () => {
    const formData = new FormData();
    formData.append('game_code', gameCode);
    formData.append('name', name);

    axios.post('http://localhost:8000/game/join_game', formData)
      .then(response => {
        setGameDetails(response.data);
        setJoined(true);
        setSearchParams({ code: gameCode, name });
        console.log(response.data); // Handle game state response here
      })
      .catch(error => {
        console.log(error);
      });
  };

  const handleLetsGo = () => {
    const formData = new FormData();
    formData.append('game_code', gameCode);
    formData.append('name', name);

    axios.post('http://localhost:8000/game/lets_go', formData)
      .then(response => {
        setGameDetails(response.data);
        console.log(response.data); // Handle game state response here
      })
      .catch(error => {
        console.log(error);
      });
  };

  const handleSubmitPrompt = () => {
    const formData = new FormData();
    formData.append('game_code', gameCode);
    formData.append('name', name);
    formData.append('prompt', prompt);

    axios.post('http://localhost:8000/game/submit_prompt', formData)
      .then(response => {
        setGameDetails(response.data);
        setPrompt(''); // Clear the prompt textarea
        console.log(response.data); // Handle game state response here
      })
      .catch(error => {
        console.log(error);
      });
  };

  const handleSubmitGuess = () => {
    const formData = new FormData();
    formData.append('game_code', gameCode);
    formData.append('name', name);
    formData.append('guess', guess);

    axios.post('http://localhost:8000/game/submit_guess', formData)
      .then(response => {
        setGameDetails(response.data);
        setGuess(''); // Clear the guess textarea
        console.log(response.data); // Handle game state response here
      })
      .catch(error => {
        console.log(error);
      });
  };

  const handleImageClick = (imageId) => {
    const formData = new FormData();
    formData.append('game_code', gameCode);
    formData.append('image_id', imageId);

    axios.post('http://localhost:8000/game/change_display_image', formData)
      .then(response => {
        setGameDetails(response.data);
        console.log(response.data); // Handle game state response here
      })
      .catch(error => {
        console.log(error);
      });
  };

  const handleNextRound = () => {
    const formData = new FormData();
    formData.append('game_code', gameCode);

    axios.post('http://localhost:8000/game/next_round', formData)
      .then(response => {
        setGameDetails(response.data);
        console.log(response.data); // Handle game state response here
      })
      .catch(error => {
        console.log(error);
      });
  };

  useEffect(() => {
    let interval;
    if (joined) {
      const fetchGameDetails = () => {
        axios.get(`http://localhost:8000/game/state/${gameCode}`)
          .then(response => {
            setGameDetails(response.data);
            console.log(response.data);
          })
          .catch(error => {
            console.log(error);
          });
      };

      fetchGameDetails();
      interval = setInterval(fetchGameDetails, 1000); // Poll every 1 second
    }

    return () => clearInterval(interval); // Clear interval on cleanup
  }, [joined, gameCode]);

  return (
    <div style={styles.container}>
      {!codeEntered ? (
        <div style={styles.inputContainer}>
          <input
            type="text"
            value={gameCode}
            onChange={handleCodeChange}
            style={styles.input}
            placeholder="Enter game code"
            maxLength="4"
          />
        </div>
      ) : !joined ? (
        <div style={styles.inputContainer}>
          <input
            type="text"
            value={name}
            onChange={handleNameChange}
            style={styles.input}
            placeholder="Enter your name"
          />
          <button onClick={handleJoinGame} style={styles.button}>Join</button>
        </div>
      ) : (
        <div style={styles.inputContainer}>
          <h2>Welcome, {name}!</h2>
          {gameDetails && gameDetails.state === 'WAITING' && gameDetails.has_sufficient_players && (
            <button onClick={handleLetsGo} style={styles.button}>Let's Go</button>
          )}
          {gameDetails && gameDetails.state === 'PLAYING' && (
            <div>
              {gameDetails.round_state === 'PROMPT' && gameDetails.current_player === name ? (
                <div>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    style={styles.textarea}
                    placeholder="Enter your prompt"
                  />
                  <button onClick={handleSubmitPrompt} style={styles.button}>Submit Prompt</button>
                </div>
              ) : gameDetails.round_state === 'PROMPT' ? (
                <p style={styles.highlightedText}>{gameDetails.current_player}'s turn...</p>
              ) : gameDetails.round_state === 'IMAGE_GENERATION' ? (
                <p style={styles.highlightedText}>Generating...</p>
              ) : gameDetails.round_state === 'GUESSING' && gameDetails.current_player !== name ? (
                <div>
                  <div style={styles.polaroid}>
                    <img
                      src={gameDetails.images.find(image => image.round === gameDetails.current_round).selection}
                      alt="Generated"
                      style={styles.largeImage}
                    />
                    <div style={styles.caption}></div>
                  </div>
                  <textarea
                    value={guess}
                    onChange={(e) => setGuess(e.target.value)}
                    style={styles.textarea}
                    placeholder="Enter your guess"
                  />
                  <button onClick={handleSubmitGuess} style={styles.button}>Submit Guess</button>
                </div>
              ) : gameDetails.round_state === 'PRESENTING' && gameDetails.current_player === name ? (
                <div>
                  <div style={styles.imagesContainer}>
                    {gameDetails.images.filter(image => image.round === gameDetails.current_round).map(image => (
                      <div key={image.id} style={styles.polaroid} onClick={() => handleImageClick(image.id)}>
                        <img
                          src={image.selection}
                          alt={image.prompt}
                          style={styles.largeImage}
                        />
                        <div style={styles.caption}>
                          {image.prompt}
                        </div>
                      </div>
                    ))}
                  </div>
                  <button onClick={handleNextRound} style={styles.button}>Next Round</button>
                </div>
              ) : (
                <p style={styles.highlightedText}>Relax...</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    backgroundColor: '#f7f0f0',
    fontFamily: 'Arial, sans-serif',
    padding: '2rem',
  },
  inputContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: '2rem',
    borderRadius: '8px',
    border: '2px solid #ddd',
  },
  input: {
    fontSize: '1.5rem',
    padding: '0.5rem',
    marginBottom: '1rem',
    borderRadius: '4px',
    border: '1px solid #ccc',
    width: '100%',
    maxWidth: '300px',
    textAlign: 'center',
  },
  button: {
    fontSize: '1.5rem',
    padding: '0.5rem 1rem',
    borderRadius: '4px',
    border: 'none',
    backgroundColor: '#007bff',
    color: '#fff',
    cursor: 'pointer',
    width: '100%',
    maxWidth: '300px',
    marginTop: '1rem',
  },
  textarea: {
    fontSize: '1.5rem',
    padding: '0.5rem',
    marginBottom: '1rem',
    borderRadius: '4px',
    border: '1px solid #ccc',
    width: '100%',
    maxWidth: '300px',
    height: '100px',
  },
  highlightedText: {
    fontSize: '3rem',
    color: '#fff',
    textShadow: '1px 1px 3px #000',
    marginBottom: '2rem',
  },
  polaroid: {
    backgroundColor: 'white',
    padding: '1rem',
    border: '2px solid #ddd',
    borderRadius: '10px',
    display: 'inline-block',
    textAlign: 'center',
    width: '80%',
    maxWidth: '800px',
    marginTop: '2rem',
    cursor: 'pointer',
  },
  largeImage: {
    width: '100%',
    height: 'auto',
  },
  caption: {
    marginTop: '1rem',
    fontSize: '1.5rem',
    color: '#555',
    minHeight: '50px',
    maxHeight: '100px',
    overflowY: 'auto',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '0.5rem',
  },
  imagesContainer: {
    display: 'flex',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: '1rem',
  },
};

export default Play;

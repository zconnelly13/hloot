import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams } from 'react-router-dom';
import Cookies from 'js-cookie';
import promptOptions from './promptOptions';
import styles from './playStyles';

const csrftoken = Cookies.get('csrftoken');
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

axios.defaults.baseURL = API_BASE_URL;
axios.defaults.headers.common['X-CSRFToken'] = csrftoken;


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

  let lastTap = 0;

  const handleDoubleClick = () => {
    if (gameDetails && gameDetails.state === 'PLAYING' && gameDetails.round_state === 'PROMPT' && gameDetails.current_player === name) {
      const randomPrompt = promptOptions[Math.floor(Math.random() * promptOptions.length)];
      setPrompt(randomPrompt);
    }
  };

  const handleTouchEnd = () => {
    const currentTime = new Date().getTime();
    const tapLength = currentTime - lastTap;
    if (tapLength < 500 && tapLength > 0) {
      handleDoubleClick();
    }
    lastTap = currentTime;
  };

  const handleFullscreen = () => {
    const elem = document.documentElement; // Fullscreen for the entire document
    if (elem.requestFullscreen) {
      elem.requestFullscreen();
    } else if (elem.mozRequestFullScreen) { // Firefox
      elem.mozRequestFullScreen();
    } else if (elem.webkitRequestFullscreen) { // Chrome, Safari, and Opera
      elem.webkitRequestFullscreen();
    } else if (elem.msRequestFullscreen) { // IE/Edge
      elem.msRequestFullscreen();
    }
  };

  useEffect(() => {
    document.addEventListener('touchend', handleTouchEnd);
    return () => {
      document.removeEventListener('touchend', handleTouchEnd);
    };
  }, [gameDetails, name]);

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

    axios.post(`/game/join_game`, formData)
      .then(response => {
        setGameDetails(response.data);
        setJoined(true);
        setSearchParams({ code: gameCode, name });
      })
      .catch(error => {
        console.log(error);
      });
  };

  const handleLetsGo = () => {
    const formData = new FormData();
    formData.append('game_code', gameCode);
    formData.append('name', name);

    axios.post(`/game/lets_go`, formData)
      .then(response => {
        setGameDetails(response.data);
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

    axios.post(`/game/submit_prompt`, formData)
      .then(response => {
        setGameDetails(response.data);
        setPrompt(''); // Clear the prompt textarea
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

    axios.post(`/game/submit_guess`, formData)
      .then(response => {
        setGameDetails(response.data);
        setGuess(''); // Clear the guess textarea
      })
      .catch(error => {
        console.log(error);
      });
  };

  const handleImageClick = (imageId) => {
    const formData = new FormData();
    formData.append('game_code', gameCode);
    formData.append('image_id', imageId);

    axios.post(`/game/change_display_image`, formData)
      .then(response => {
        setGameDetails(response.data);
      })
      .catch(error => {
        console.log(error);
      });
  };

  const handleNextRound = () => {
    const formData = new FormData();
    formData.append('game_code', gameCode);

    axios.post(`/game/next_round`, formData)
      .then(response => {
        setGameDetails(response.data);
      })
      .catch(error => {
        console.log(error);
      });
  };

  useEffect(() => {
    let interval;
    if (joined) {
      const fetchGameDetails = () => {
        axios.get(`/game/state/${gameCode}`)
          .then(response => {
            setGameDetails(response.data);
          })
          .catch(error => {
            console.log(error);
          });
      };

      fetchGameDetails();
      interval = setInterval(fetchGameDetails, 5000); // Poll every 1 second
    }

    return () => clearInterval(interval); // Clear interval on cleanup
  }, [joined, gameCode]);

  return (
    <div style={styles.container} onDoubleClick={handleDoubleClick}>
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
          <h2 style={styles.waitingMessage} onClick={handleFullscreen}>Hloot</h2>
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
                    placeholder="What'll it be?"
                  />
                  <button onClick={handleSubmitPrompt} style={styles.button}>Submit Prompt</button>
                </div>
              ) : gameDetails.round_state === 'PROMPT' ? (
                <p style={styles.highlightedText}>{gameDetails.current_player}'s turn...</p>
              ) : gameDetails.round_state === 'IMAGE_GENERATION' ? (
                <p style={styles.highlightedText}>Generating...</p>
              ) : gameDetails.round_state === 'GUESSING' && gameDetails.images.find(image => image.round === gameDetails.current_round && image.player === name) ? (
                <p></p>
              ) : gameDetails.round_state === 'GUESSING' && gameDetails.current_player !== name ? (
                <div>
                  <textarea
                    value={guess}
                    onChange={(e) => setGuess(e.target.value)}
                    style={styles.textarea}
                    placeholder="What's that?"
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
                <p></p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Play;

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useSearchParams } from 'react-router-dom';
import QRCodeSVG from 'qrcode.react';
import Cookies from 'js-cookie';
import styles from './hostStyles';

const csrftoken = Cookies.get('csrftoken');
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

axios.defaults.baseURL = API_BASE_URL;
axios.defaults.headers.common['X-CSRFToken'] = csrftoken;

function Host() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialGameCode = searchParams.get('code') || '';
  const [gameCode, setGameCode] = useState(initialGameCode);
  const [gameDetails, setGameDetails] = useState(null);
  const [dotCounter, setDotCounter] = useState(0); // State to keep track of counter
  const effectRan = useRef(false);

  useEffect(() => {
    if (!gameCode && effectRan.current === false) {
      axios.post(`/game/create`)
        .then(response => {
          const newGameCode = response.data.game_code;
          setGameCode(newGameCode);
          setSearchParams({ code: newGameCode });
        })
        .catch(error => {
          console.log(error);
        });

      effectRan.current = true;
    }

    return () => {
      effectRan.current = false;
    };
  }, [gameCode, setSearchParams]);

  useEffect(() => {
    let interval;
    if (gameCode) {
      let currentIntervalTime = 1000; // Update every 1 second
      let quickIntervalTime = 250;

      const fetchGameDetails = () => {
        axios.get(`/game/state/${gameCode}`)
          .then(response => {
            setGameDetails(response.data);
            setDotCounter(prev => prev + 1); // Increment counter

            if (response.data.round_state === 'PRESENTING') {
              if (currentIntervalTime !== quickIntervalTime) {
                clearInterval(interval);
                interval = setInterval(fetchGameDetails, quickIntervalTime); // Poll quickly while presenting
                currentIntervalTime = quickIntervalTime;
              }
              response.data.images.sort((a, b) => a.id - b.id).forEach(image => {
                if (image.round === response.data.current_round) {
                  let img = new Image();
                  img.src = image.selection;
                }
              });
            } else if (response.data.round_state === 'PROMPT') {
              if (currentIntervalTime !== 1000) {
                clearInterval(interval);
                interval = setInterval(fetchGameDetails, 1000); // Poll every 1 second while not presenting
                currentIntervalTime = 1000;
              }
            }
          })
          .catch(error => {
            console.log(error);
          });
      };

      fetchGameDetails();
      interval = setInterval(fetchGameDetails, 1000); // Poll every second
    }

    return () => clearInterval(interval); // Clear interval on cleanup
  }, [gameCode]);

  const getSpinner = () => {
    const spinnerChars = ['|', '/', '-', '\\'];
    const spinnerChar = spinnerChars[dotCounter % spinnerChars.length];
    return spinnerChar;
  };

  const getPlayersStillGuessing = () => {
    if (!gameDetails || !gameDetails.images) return '';

    const playersStillGuessing = gameDetails.players.filter(player => {
      return !gameDetails.images.some(image => image.round === gameDetails.current_round && image.player === player);
    });

    if (playersStillGuessing.length === 1) {
      return `${playersStillGuessing[0]} is still guessing...`;
    } else if (playersStillGuessing.length === 2) {
      return `${playersStillGuessing[0]} and ${playersStillGuessing[1]} are still guessing...`;
    } else if (playersStillGuessing.length > 2) {
      const lastPlayer = playersStillGuessing.pop();
      return `${playersStillGuessing.join(', ')}, and ${lastPlayer} are still guessing...`;
    } else {
      return `Generating ${getSpinner()}`;
    }
  };

  return (
    <div style={styles.container}>
      <center>
        {gameDetails && gameDetails.state === 'WAITING' && (
          <>
            <QRCodeSVG size="128" value={`${window.location.origin}${window.location.pathname}#/play?code=${gameCode}`} style={styles.qrCode} />
            <h1 style={styles.gameCode}>Hloot</h1>
            <div style={styles.waitingContainer}>
              <h2 style={styles.waitingText}>Waiting for players {getSpinner()}</h2>
              <ul style={styles.playersList}>
                {gameDetails.players.map((player, index) => (
                  <li key={index} style={styles.playerItem}>
                    {player}
                  </li>
                ))}
              </ul>
            </div>
          </>
        )}
        {gameDetails && gameDetails.state === 'PLAYING' && (
          <div>
            {gameDetails.round_state === 'PROMPT' && (
              <div style={styles.messageContainer}>
                <h2 style={styles.highlightedText}>{gameDetails.current_player}'s turn...</h2>
              </div>
            )}
            {gameDetails.round_state === 'IMAGE_GENERATION' && (
              <div style={styles.messageContainer}>
                <h2 style={styles.highlightedText}>Generating {getSpinner()}</h2>
              </div>
            )}
            {gameDetails.round_state === 'GUESSING' && (
              <div style={styles.polaroid}>
                {gameDetails.images.sort((a, b) => a.id - b.id).find(image => image.round === gameDetails.current_round) && (
                  <div style={styles.polaroidInner}>
                    <img
                      src={gameDetails.images.sort((a, b) => a.id - b.id).find(image => image.round === gameDetails.current_round).selection}
                      alt="Generated"
                      style={styles.largeImage}
                    />
                    <div style={styles.caption}>{getPlayersStillGuessing()}</div>
                  </div>
                )}
              </div>
            )}
            {gameDetails.round_state === 'PRESENTING' && (
              <div>
                {gameDetails.display_image ? (
                  <div style={styles.polaroid}>
                    <img
                      src={gameDetails.display_image.selection}
                      alt={gameDetails.display_image.prompt}
                      style={styles.largeImage}
                    />
                    <div style={styles.caption}>
                      {gameDetails.display_image.prompt}
                    </div>
                  </div>
                ) : (
                  <h2 style={styles.highlightedText}>Waiting for {gameDetails.current_player} to pick an image...</h2>
                )}
              </div>
            )}
          </div>
        )}
      </center>
    </div>
  );
}

export default Host;

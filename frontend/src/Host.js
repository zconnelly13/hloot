import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useSearchParams } from 'react-router-dom';
import QRCodeSVG from 'qrcode.react';
import Cookies from 'js-cookie';

const csrftoken = Cookies.get('csrftoken');
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

axios.defaults.baseURL = API_BASE_URL;
axios.defaults.headers.common['X-CSRFToken'] = csrftoken;

function Host() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialGameCode = searchParams.get('code') || '';
  const [gameCode, setGameCode] = useState(initialGameCode);
  const [gameDetails, setGameDetails] = useState(null);
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
      let currentIntervalTime = 5000;
      let intervalTime = 5000;
      let quickIntervalTime = 250;

      const fetchGameDetails = () => {
        axios.get(`/game/state/${gameCode}`)
          .then(response => {
            setGameDetails(response.data);
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
              if (currentIntervalTime !== intervalTime) {
                clearInterval(interval);
                interval = setInterval(fetchGameDetails, intervalTime); // Poll every 5 seconds while not presenting
                currentIntervalTime = intervalTime;
              }
            }
          })
          .catch(error => {
            console.log(error);
          });
      };

      fetchGameDetails();
      interval = setInterval(fetchGameDetails, intervalTime); // Poll every quarter second
    }

    return () => clearInterval(interval); // Clear interval on cleanup
  }, [gameCode]);

  return (
    <div style={styles.container}>
      <center>
        {gameDetails && gameDetails.state === 'WAITING' && (
          <>
          <QRCodeSVG size="128" value={`${window.location.origin}${window.location.pathname}#/play?code=${gameCode}`} style={styles.qrCode} />
            <h1 style={styles.gameCode}>Hloot</h1>
            <div style={styles.waitingContainer}>
              <h2 style={styles.waitingText}>Waiting for players...</h2>
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
                <h2 style={styles.highlightedText}>{gameDetails.current_player}'s turn</h2>
              </div>
            )}
            {gameDetails.round_state === 'IMAGE_GENERATION' && (
              <div style={styles.messageContainer}>
                <h2 style={styles.highlightedText}>Generating...</h2>
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
                    <div style={styles.caption}></div>
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

const styles = {
  container: {
    background: "url('https://cl.imagineapi.dev/assets/7ca88a00-35e3-4b39-81c1-c76c6e204e36.png') no-repeat center center fixed",
    backgroundSize: 'cover',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    backgroundColor: '#f7f0f0',
    fontFamily: 'Arial, sans-serif',
  },
  gameCodeLabel: {
    fontSize: '2rem',
    color: '#555',
    marginBottom: '1rem',
  },
  gameCode: {
    fontSize: '4rem',
    color: 'white',
    WebkitTextStroke: '1.5px black',
    marginBottom: '2rem',
  },
  waitingContainer: {
    backdropFilter: 'blur(15px)',
    padding: '2rem',
    borderRadius: '8px',
    border: '2px',
  },
  waitingText: {
    fontSize: '1rem',
    color: 'white',
    marginBottom: '2rem',
  },
  playersList: {
    listStyleType: 'none',
    padding: 0,
  },
  playerItem: {
    fontSize: '2rem',
    color: 'white',
    padding: '0',
  },
  messageContainer: {
    backdropFilter: 'blur(15px)',
    paddingTop: '1vh',
    paddingBottom: '1vh',
    paddingLeft: '7vw',
    paddingRight: '7vw',
    borderRadius: '8px',
    textAlign: 'center',
    WebkitTextStroke: '1px #ccc',
  },
  highlightedText: {
    fontSize: '3rem',
    color: '#fff',
    marginBottom: '2rem',
    backdropFilter: 'blur(15px)',
  },
  polaroid: {
    backgroundColor: 'white',
    padding: '1rem',
    border: '2px solid #ddd',
    borderRadius: '10px',
    display: 'inline-block',
    textAlign: 'center',
    width: '100%',
    maxWidth: '800px',
    marginTop: '2rem',
  },
  largeImage: {
    width: '100%',
    height: 'auto',
  },
  caption: {
    marginTop: '1rem',
    fontSize: '1rem',
    color: '#555',
    minHeight: '50px',
    maxHeight: '100px',
    overflowY: 'auto',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '0.5rem',
  },
  qrCode: {
    padding: '0.8rem',
    backgroundColor: 'white',
    backdropFilter: 'blur(15px)',
    borderRadius: '10px',
    marginBottom: '0rem',
  },
};

export default Host;

import React, { useState, useEffect, useRef, useCallback } from 'react';
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
  const [dotCounter, setDotCounter] = useState(0);
  const effectRan = useRef(false);
  const intervalRef = useRef(null);

  const createGame = useCallback(async () => {
    try {
      const response = await axios.post(`/game/create`);
      const newGameCode = response.data.game_code;
      setGameCode(newGameCode);
      setSearchParams({ code: newGameCode });
    } catch (error) {
      console.error('Error creating game:', error);
    }
  }, [setSearchParams]);

  useEffect(() => {
    if (!gameCode && !effectRan.current) {
      createGame();
      effectRan.current = true;
    }
    return () => {
      effectRan.current = false;
    };
  }, [gameCode, createGame]);

  const setupGameDetailsInterval = useCallback(() => {
    let intervalTime = 1000;

    const fetchGameDetails = async () => {
      try {
        const response = await axios.get(`/game/state/${gameCode}`);
        setGameDetails(response.data);
        setDotCounter(prev => prev + 1);
        adjustFetchInterval(response.data, intervalTime);
      } catch (error) {
        console.error('Error fetching game details:', error);
      }
    };

    const adjustFetchInterval = (data, intervalTime) => {
      if (data.round_state === 'PRESENTING' && intervalTime !== 250) {
        clearInterval(intervalRef.current);
        intervalRef.current = setInterval(fetchGameDetails, 250);
        intervalTime = 250;
        prefetchImages(data.images, data.current_round);
      } else if (data.round_state === 'PROMPT' && intervalTime !== 1000) {
        clearInterval(intervalRef.current);
        intervalRef.current = setInterval(fetchGameDetails, 1000);
        intervalTime = 1000;
      }
    };

    fetchGameDetails();
    return setInterval(fetchGameDetails, intervalTime);
  }, [gameCode]);

  useEffect(() => {
    if (gameCode) {
      intervalRef.current = setupGameDetailsInterval();
      return () => clearInterval(intervalRef.current);
    }
  }, [gameCode, setupGameDetailsInterval]);

  const prefetchImages = (images, currentRound) => {
    images
      .filter(image => image.round === currentRound)
      .forEach(image => {
        const img = new Image();
        img.src = image.selection;
      });
  };

  const getSpinner = () => {
    const spinnerChars = ['|', '/', '|', '\\'];
    return spinnerChars[dotCounter % spinnerChars.length];
  };

  const getPlayersStillGuessing = () => {
    if (!gameDetails || !gameDetails.images) return '';

    const playersStillGuessing = gameDetails.players.filter(player =>
      !gameDetails.images.some(image => image.round === gameDetails.current_round && image.player === player)
    );

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

  const renderWaitingState = () => (
    <div style={styles.centeredContent}>
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
    </div>
  );

  const renderPlayingState = () => (
    <div style={styles.centeredContent}>
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
      {gameDetails.round_state === 'GUESSING' && renderGuessingState()}
      {gameDetails.round_state === 'PRESENTING' && renderPresentingState()}
    </div>
  );

  const renderGuessingState = () => {
    const currentImage = gameDetails.images.find(image => image.round === gameDetails.current_round);
    return (
      <div style={styles.polaroid}>
        {currentImage && (
          <div style={styles.polaroidInner}>
            <img src={currentImage.selection} alt="Generated" style={styles.largeImage} />
            <div style={styles.caption}>{getPlayersStillGuessing()}</div>
          </div>
        )}
      </div>
    );
  };

  const renderPresentingState = () => {
    const displayImage = gameDetails.display_image;
    return (
      displayImage ? (
        <div style={styles.polaroid}>
          <div style={styles.polaroidInner}>
            <img src={displayImage.selection} alt={displayImage.prompt} style={styles.largeImage} />
            <div style={styles.caption}>{displayImage.prompt}</div>
          </div>
        </div>
      ) : (
        <div style={styles.messageContainer}>
          <h2 style={styles.highlightedText}>Waiting for {gameDetails.current_player} to pick an image...</h2>
        </div>
      )
    );
  };

  const renderGameDetails = () => {
    if (!gameDetails) return null;

    switch (gameDetails.state) {
      case 'WAITING':
        return renderWaitingState();
      case 'PLAYING':
        return renderPlayingState();
      default:
        return null;
    }
  };

  return (
    <div style={styles.container}>
      {renderGameDetails()}
    </div>
  );
}

export default Host;

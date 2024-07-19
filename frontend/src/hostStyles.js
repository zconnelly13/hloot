const styles = {
  container: {
    background: "url('https://cl.imagineapi.dev/assets/7ca88a00-35e3-4b39-81c1-c76c6e204e36.png') no-repeat center center fixed",
    backgroundSize: 'cover',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    fontFamily: 'Arial, sans-serif',
  },
  centeredContent: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    textAlign: 'center',
    width: '100%',
    height: '100%', // Ensure it takes the full height of the container
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
    padding: '2rem 2rem 1rem 2rem',
    border: '2px solid #ddd',
    borderRadius: '10px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    width: '90%',
    maxWidth: '1000px', // Increased from 800px
    maxHeight: '90vh', // Increased from 80vh
    boxSizing: 'border-box',
  },
  polaroidInner: {
    width: '100%',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
  },
  largeImage: {
    width: '100%',
    height: 'auto',
    objectFit: 'contain', // Ensure image maintains aspect ratio
    maxHeight: 'calc(100% - 50px)', // Subtracting some height for the caption
    borderRadius: '10px',
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
    width: '100%',
    boxSizing: 'border-box',
  },
  qrCode: {
    padding: '0.8rem',
    backgroundColor: 'white',
    backdropFilter: 'blur(15px)',
    borderRadius: '10px',
    marginBottom: '0rem',
  },
};

export default styles;

import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [fens, setFens] = useState('');
  const [diagramsPerPage, setDiagramsPerPage] = useState(6);
  const [padding, setPadding] = useState(5);
  const [lightSquares, setLightSquares] = useState('#f0d9b5');
  const [darkSquares, setDarkSquares] = useState('#b58863');
  const [borderColor, setBorderColor] = useState('#ffffffff');
  const [singleColumn, setSingleColumn] = useState(1);
  const [twoColumnMax, setTwoColumnMax] = useState(8);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGeneratePdf = async () => {
    const fenList = fens.split('\n').filter(fen => fen.trim() !== '');
    if (fenList.length === 0) {
      setError('Please enter at least one FEN string.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        '/api/generate-pdf/',
        {
          fens: fenList,
          diagrams_per_page: diagramsPerPage,
          padding: {
            top: padding,
            bottom: padding,
            left: padding,
            right: padding,
          },
          board_colors: {
            light_squares: lightSquares,
            dark_squares: darkSquares,
            border_color: borderColor,
          },
          columns_for_diagrams_per_page: {
            single_column: singleColumn,
            two_column_max: twoColumnMax,
          },
        },
        {
          responseType: 'blob',
        }
      );

      const file = new Blob([response.data], { type: 'application/pdf' });
      const fileURL = URL.createObjectURL(file);

      const link = document.createElement('a');
      link.href = fileURL;
      link.setAttribute('download', 'chess_diagrams.pdf');
      document.body.appendChild(link);
      link.click();

      link.parentNode.removeChild(link);
      URL.revokeObjectURL(fileURL);

    } catch (err) {
      setError('An error occurred while generating the PDF.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Chess Diagram PDF Generator</h1>
      </header>
      <main>
        <div className="form-container">
          <div className="form-group">
            <label htmlFor="fen-input">Enter FEN strings (one per line):</label>
            <textarea
              id="fen-input"
              value={fens}
              onChange={(e) => setFens(e.target.value)}
              rows="10"
              placeholder="e.g., rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            />
          </div>
          <div className="form-group">
            <label htmlFor="diagrams-per-page">Diagrams per page:</label>
            <input
              type="number"
              id="diagrams-per-page"
              value={diagramsPerPage}
              onChange={(e) => setDiagramsPerPage(Number(e.target.value))}
              min="1"
            />
          </div>
          <div className="form-group">
            <label htmlFor="padding">Space between diagrams (points):</label>
            <input
              type="number"
              id="padding"
              value={padding}
              onChange={(e) => setPadding(Number(e.target.value))}
              min="0"
            />
          </div>
          <div className="form-group">
            <label htmlFor="light-squares">Light square color:</label>
            <input
              type="color"
              id="light-squares"
              value={lightSquares}
              onChange={(e) => setLightSquares(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="dark-squares">Dark square color:</label>
            <input
              type="color"
              id="dark-squares"
              value={darkSquares}
              onChange={(e) => setDarkSquares(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="border-color">Border color:</label>
            <input
              type="color"
              id="border-color"
              value={borderColor}
              onChange={(e) => setBorderColor(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Column Layout Rules:</label>
            <div>
              <label htmlFor="single-column" style={{ marginRight: '10px' }}>Single column if diagrams ≤</label>
              <input
                type="number"
                id="single-column"
                value={singleColumn}
                onChange={(e) => setSingleColumn(Number(e.target.value))}
                min="1"
                style={{ width: '60px' }}
              />
            </div>
            <div>
              <label htmlFor="two-column-max" style={{ marginRight: '10px' }}>Two columns if diagrams ≤</label>
              <input
                type="number"
                id="two-column-max"
                value={twoColumnMax}
                onChange={(e) => setTwoColumnMax(Number(e.target.value))}
                min="1"
                style={{ width: '60px' }}
              />
            </div>
            <small>Otherwise, three columns will be used.</small>
          </div>
          <button onClick={handleGeneratePdf} className="generate-btn" disabled={loading}>
            {loading ? 'Generating...' : 'Generate PDF'}
          </button>
          {error && <p className="error-message">{error}</p>}
        </div>
      </main>
    </div>
  );
}

export default App;

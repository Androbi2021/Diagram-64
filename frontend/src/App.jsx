import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [fens, setFens] = useState('');
  const [diagramsPerPage, setDiagramsPerPage] = useState(1);
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
        },
        {
          responseType: 'blob',
        }
      );

      // Create a URL for the PDF blob
      const file = new Blob([response.data], { type: 'application/pdf' });
      const fileURL = URL.createObjectURL(file);

      // Create a link and trigger the download
      const link = document.createElement('a');
      link.href = fileURL;
      link.setAttribute('download', 'chess_diagrams.pdf');
      document.body.appendChild(link);
      link.click();

      // Clean up
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
            <select
              id="diagrams-per-page"
              value={diagramsPerPage}
              onChange={(e) => setDiagramsPerPage(Number(e.target.value))}
            >
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="4">4</option>
              <option value="6">6</option>
              <option value="8">8</option>
              <option value="9">9</option>
            </select>
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

import { useEffect, useState } from "react";

const BACKEND_URL = "http://127.0.0.1:8000";

function App() {
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${BACKEND_URL}/acceptance`)
      .then(res => res.json())
      .then(setData)
      .catch(err => setError(err.message));
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h2>INTAX Audit Portal V2</h2>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}

export default App;

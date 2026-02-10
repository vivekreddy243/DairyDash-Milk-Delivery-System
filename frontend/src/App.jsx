import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { useEffect } from "react";

function App() {
  const [apartments, setApartments] = useState([]);
  const [name, setName] = useState("");

  const loadApartments = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/apartments");
      const data = await res.json();
      setApartments(data);
    } catch (err) {
      console.error("Failed to load apartments:", err);
    }
  };

  useEffect(() => {
    loadApartments();
  }, []);

  const createApartment = async () => {
    if (!name.trim()) return;

    try {
      await fetch("http://127.0.0.1:8000/apartments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name.trim() }),
      });

      setName("");
      loadApartments();
    } catch (err) {
      console.error("Failed to create apartment:", err);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>DairyDash Admin</h1>

      <h2>Apartments</h2>
      {apartments.length === 0 ? (
        <p>No apartments yet.</p>
      ) : (
        <ul>
          {apartments.map((apt) => (
            <li key={apt.id}>
              #{apt.id} — {apt.name}
            </li>
          ))}
        </ul>
      )}

      <h3>Add Apartment</h3>
      <div style={{ display: "flex", gap: "8px", maxWidth: "400px" }}>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Apartment name (e.g., Vasudha Apex)"
          style={{ flex: 1, padding: "8px" }}
        />
        <button onClick={createApartment} style={{ padding: "8px 12px" }}>
          Add
        </button>
      </div>
    </div>
  );
}

export default App;

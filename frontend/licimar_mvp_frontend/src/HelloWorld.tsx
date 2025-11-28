export default function HelloWorld() {
  return (
    <div style={{ 
      padding: '40px', 
      backgroundColor: '#f0f0f0',
      fontFamily: 'Arial, sans-serif',
      minHeight: '100vh'
    }}>
      <h1 style={{ color: '#333' }}>Hello World - React is Working!</h1>
      <p style={{ color: '#666', fontSize: '16px' }}>
        If you see this, React and Vite are properly configured.
      </p>
      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#fff', border: '1px solid #ccc' }}>
        <strong>Debug Info:</strong>
        <ul style={{ color: '#333' }}>
          <li>Time: {new Date().toLocaleTimeString()}</li>
          <li>Node Env: {import.meta.env.MODE}</li>
          <li>React Loaded: Yes</li>
        </ul>
      </div>
    </div>
  );
}

import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';

function App() {
  const [mergedData, setMergedData] = useState([]);
  const [currentPage, setCurrentPage] = useState('home'); // 'home' or 'analyze'

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/get_merged_data');
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const result = await response.json();
        setMergedData(result);
      } catch (error) {
        console.error('Error fetching merged data:', error);
      }
    };
  
    fetchData();
  }, []);

  const renderContent = () => {
    switch (currentPage) {
      case 'home':
        return (
          <div>
            <h1>Weather Data</h1>
              <table style={{ borderCollapse: 'collapse', width: '100%' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #ddd' }}>
                    <th style={{ padding: '8px', textAlign: 'left' }}>Date</th>
                    <th style={{ padding: '8px', textAlign: 'left' }}>Produk</th>
                    <th style={{ padding: '8px', textAlign: 'left' }}>Sales</th>
                    <th style={{ padding: '8px', textAlign: 'left' }}>Temperature at 2m</th>
                  </tr>
                </thead>
                <tbody>
                  {mergedData.map((data, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #ddd' }}>
                      <td style={{ padding: '8px', textAlign: 'left' }}>
                        {new Date(data.date).toLocaleDateString()}
                      </td>
                      <td style={{ padding: '8px', textAlign: 'left' }}>{data.Produk}</td>
                      <td style={{ padding: '8px', textAlign: 'left' }}>{data.Sales}</td>
                      <td style={{ padding: '8px', textAlign: 'left' }}>{data['Temperature At 10 AM']}</td>
                  </tr>
                  ))}
                </tbody>
              </table>
          </div>
        );
        case 'analyze':
          return (
            <div>
              <h1>Data Analysis</h1>
              <Line
                data={{
                  labels: mergedData.map((data) => new Date(data.date).toLocaleDateString()),
                  datasets: [
                    {
                      label: 'Sales',
                      data: mergedData.map((data) => data.Sales),
                      borderColor: 'rgba(75,192,192,1)',
                      borderWidth: 2,
                      fill: false,
                    },
                    {
                      label: 'Temperature at 10 AM',
                      data: mergedData.map((data) => data['Temperature At 10 AM']),
                      borderColor: 'rgba(255,99,132,1)',
                      borderWidth: 2,
                      fill: false,
                    },
                  ],
                }}
                options={{
                  scales: {
                    x: {
                      type: 'linear',
                      position: 'bottom',
                    },
                    y: {
                      beginAtZero: true,
                    },
                  },
                }}
              />
            </div>
          );
        default:
          return null;
      }
    };
  
    return (
      <div>
        <nav style={{ marginBottom: '20px' }}>
          <ul style={{ listStyleType: 'none', padding: '0' }}>
            <li style={{ display: 'inline', marginRight: '10px' }}>
              <button onClick={() => setCurrentPage('home')}>Home</button>
            </li>
            <li style={{ display: 'inline' }}>
              <button onClick={() => setCurrentPage('analyze')}>Analyze</button>
            </li>
          </ul>
        </nav>
  
        {renderContent()}
      </div>
    );  
  }
  
  export default App;
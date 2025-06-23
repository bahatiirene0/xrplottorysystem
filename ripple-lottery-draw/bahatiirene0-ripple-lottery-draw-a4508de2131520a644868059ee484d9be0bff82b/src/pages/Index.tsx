import { useEffect, useState } from 'react';
import { getDrawStatus } from '../api';

export default function Index() {
  const [drawStatus, setDrawStatus] = useState(null);
  useEffect(() => {
    getDrawStatus().then(setDrawStatus).catch(console.error);
  }, []);
  return (
    <div>
      <h1>XRP Lottery Draw Status</h1>
      <pre>{drawStatus ? JSON.stringify(drawStatus, null, 2) : 'Loading draw status...'}</pre>
    </div>
  );
}

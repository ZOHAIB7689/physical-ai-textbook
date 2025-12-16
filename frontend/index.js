// /src/pages/index.js

import { useEffect } from 'react';
import { useRouter } from 'next/router';

const Home = () => {
  const router = useRouter();

  useEffect(() => {
    // Redirects the root path to your main content page
    router.push('/textbook');
  }, [router]);

  return <div>Redirecting to Textbook...</div>;
};

export default Home;

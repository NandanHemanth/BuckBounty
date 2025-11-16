"use client";

import { useEffect, useRef, useState } from 'react';

export default function VantaBackground() {
  const vantaRef = useRef<HTMLDivElement>(null);
  const [vantaEffect, setVantaEffect] = useState<any>(null);

  useEffect(() => {
    if (!vantaEffect && vantaRef.current) {
      // Dynamically import Vanta and Three.js
      Promise.all([
        import('vanta/dist/vanta.net.min'),
        import('three')
      ]).then(([VANTA, THREE]) => {
        const effect = VANTA.default({
          el: vantaRef.current,
          THREE: THREE,
          mouseControls: true,
          touchControls: true,
          gyroControls: false,
          minHeight: 200.00,
          minWidth: 200.00,
          scale: 1.00,
          scaleMobile: 1.00,
          color: 0x10b981, // Green
          backgroundColor: 0x000000, // Black
          points: 10.00,
          maxDistance: 20.00,
          spacing: 15.00,
          showDots: true
        });
        setVantaEffect(effect);
      }).catch(err => {
        console.error('Vanta.js failed to load:', err);
      });
    }

    return () => {
      if (vantaEffect && typeof vantaEffect.destroy === 'function') {
        vantaEffect.destroy();
      }
    };
  }, [vantaEffect]);

  return (
    <div
      ref={vantaRef}
      className="fixed inset-0 z-0"
      style={{ width: '100vw', height: '100vh' }}
    />
  );
}

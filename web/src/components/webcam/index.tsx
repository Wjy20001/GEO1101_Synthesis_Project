import { Container } from '@mantine/core';
import { useCallback, useRef, useState } from 'react';

import WebcamComp from 'react-webcam';

type WebcamProps = {
  onCapture: (imageSrc: string) => void;
};

const Webcam = () => {
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const webcamRef = useRef<WebcamComp | null>(null);

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    setImageSrc(imageSrc);
  }, [webcamRef]);

  return (
    <Container style={{ width: '100vw', height: '100vh', padding: 0 }}>
      <WebcamComp
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
        // videoConstraints={{
        //   facingMode: "environment",
        // }}
        onUserMediaError={(error) => console.error(error)}
      />
    </Container>
  );
};

export default Webcam;

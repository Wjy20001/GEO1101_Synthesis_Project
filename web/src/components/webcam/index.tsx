import { useCallback, useRef, useState } from "react";

import WebcamComp from "react-webcam";

const Webcam = () => {
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const webcamRef = useRef<WebcamComp | null>(null);

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    setImageSrc(imageSrc);
  }, [webcamRef]);

  return (
    <div style={{ width: "100%", height: "100%" }}>
      <WebcamComp
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        width="100%"
        height="100%"
        onUserMediaError={(error) => console.error(error)}
      />
    </div>
  );
};

export default Webcam;

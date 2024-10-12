import { useCallback, useRef, useState } from "react";

import React from "react";
import WebcamComp from "react-webcam";

const Webcam = () => {
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const webcamRef = useRef(null);

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    setImageSrc(imageSrc);
  }, [webcamRef]);

  return (
    <div>
      <WebcamComp
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        width={640}
        height={480}
      />
      <button onClick={capture}>Capture photo</button>
      {imageSrc && <img src={imageSrc} />}
    </div>
  );
};

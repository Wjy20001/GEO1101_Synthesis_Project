import {
  Button,
  Container,
  Stack,
  Text,
  RingProgress,
  Center,
  Overlay,
  ActionIcon,
  Transition,
} from '@mantine/core';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import { IconCamera, IconCheck } from '@tabler/icons-react';
import { useCallback, useRef, useState } from 'react';
import WebcamComp from 'react-webcam';

const instructions = [
  'Please take a photo of your surroundings.',
  'Please take a photo of your environment on the right-hand side.',
  'Please take a photo of your environment behind you.',
  'Please take a photo of your environment on the left-hand side.',
];

const Camera: React.FC = () => {
  const [photos, setPhotos] = useState<File[]>([]);
  const [finished, setFinished] = useState(false);

  const webcamRef = useRef<WebcamComp | null>(null);

  const capture = useCallback(() => {
    console.log('capture');
    const imageSrc = webcamRef.current?.getScreenshot();
    if (!imageSrc) return;

    // Convert base64 image to blob and then to File
    fetch(imageSrc)
      .then((res) => res.blob())
      .then((blob) => {
        const file = new File([blob], `photo_${photos.length + 1}.jpg`, {
          type: 'image/jpeg',
        });
        setPhotos((prevPhotos) => {
          const newPhotos = [...prevPhotos, file];
          if (newPhotos.length >= 4) {
            setFinished(true);
          }
          return newPhotos;
        });
      });
  }, [photos.length]);

  const handleSubmit = () => {
    const formData = new FormData();
    photos.forEach((photo) => {
      formData.append('photos', photo);
    });

    // Send formData to the server
    fetch('/upload', {
      method: 'POST',
      body: formData,
    })
      .then((response) => {
        // Handle the server response
      })
      .catch((error) => {
        // Handle errors
      });
  };

  return (
    <Container size="sm" m={0} p={0}>
      {/* Camera and Progress Ring */}
      <Transition
        mounted={!finished}
        transition="fade"
        duration={500}
        timingFunction="ease"
      >
        {(styles) => (
          <div style={{ ...styles, position: 'relative' }}>
            <Container style={{ width: '100vw', height: '100vh', padding: 0 }}>
              <WebcamComp
                audio={false}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                onUserMediaError={(error) => console.error(error)}
              />
            </Container>
            <Overlay zIndex={1000} opacity={0.9}>
              <Stack>
                {/* Animated Progress Ring */}
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    height: '100vh',
                    width: '100vw',
                    position: 'fixed',
                    top: 0,
                    left: 0,
                  }}
                >
                  <CircularProgressbar
                    value={(photos.length / 4) * 100}
                    text={`${photos.length}/4`}
                    styles={buildStyles({
                      pathColor: 'teal',
                      textColor: 'teal',
                      trailColor: '#d6d6d6',
                    })}
                    strokeWidth={10}
                    animate={true}
                  />
                </div>
                {/* Capture Button */}
                <div
                  style={{
                    position: 'fixed',
                    left: '50%',
                    bottom: '20px',
                    transform: 'translateX(-50%)',
                    zIndex: 1001,
                  }}
                >
                  <Button
                    variant="filled"
                    color="gray"
                    style={{
                      width: '75px',
                      height: '75px',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                    onClick={capture}
                  >
                    <IconCamera size={30} />
                  </Button>
                </div>
              </Stack>
            </Overlay>
          </div>
        )}
      </Transition>

      {/* Completion Message */}
      <Transition
        mounted={finished}
        transition="slide-up"
        duration={500}
        timingFunction="ease"
      >
        {(styles) => (
          <div style={{ ...styles, position: 'relative', height: '100vh' }}>
            <Stack align="center" justify="center" style={{ height: '100%' }}>
              <ActionIcon color="teal" radius="xl" size={100}>
                <IconCheck size={80} />
              </ActionIcon>
              <Text size="xl">Thank you! All photos have been taken.</Text>
              <Button onClick={handleSubmit}>Submit Photos</Button>
            </Stack>
          </div>
        )}
      </Transition>
    </Container>
  );
};

export default Camera;

import {
  Button,
  Container,
  Stack,
  Text,
  Overlay,
  ActionIcon,
  Transition,
  useMantineTheme,
  LoadingOverlay,
  Box,
} from '@mantine/core';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import { IconCamera, IconCheck } from '@tabler/icons-react';
import { useCallback, useRef, useState } from 'react';
import WebcamComp from 'react-webcam';
import { useLoading, useUserLocation } from '../../state';
import { useAPI } from '../../api';

type CameraProps = {
  onToggleMode: () => void;
};

const instructions = [
  'Please take a photo of your environment on the right-hand side.',
  'Please take a photo of your environment on the front.',
  'Please take a photo of your environment on the left-hand side.',
];

const Camera = ({ onToggleMode }: CameraProps) => {
  const [photos, setPhotos] = useState<File[]>([]);
  const [finished, setFinished] = useState(false);
  const theme = useMantineTheme();
  const webcamRef = useRef<WebcamComp | null>(null);
  const setUserLocation = useUserLocation((state) => state.setLocation);
  const loading = useLoading((state) => state.loading);
  const setLoading = useLoading((state) => state.setLoading);
  const { uploadPhotos } = useAPI();

  const capture = useCallback(() => {
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
          if (newPhotos.length >= 3) {
            setFinished(true);
          }
          return newPhotos;
        });
      });
  }, [photos.length]);

  const handleSubmit = async () => {
    setLoading(true);

    try {
      const data = await uploadPhotos(photos);
      setUserLocation({
        lat: data.user_coordinate[1],
        lng: data.user_coordinate[0],
        room: data.user_room,
      });
      onToggleMode();
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return loading ? (
    <Box
      pos="relative"
      style={{
        width: '100vw',
        height: '100vh',
        background: theme.colors.dark[6],
      }}
    >
      <LoadingOverlay
        visible={true}
        zIndex={1000}
        overlayProps={{ radius: 'sm', blur: 2 }}
      />
    </Box>
  ) : (
    <Container
      size="sm"
      m={0}
      p={0}
      style={{ backgroundColor: theme.colors.dark[6], height: '100vh' }}
    >
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
                videoConstraints={{
                  facingMode: 'environment',
                }}
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
                    padding: '50px',
                    top: 0,
                    left: 0,
                  }}
                >
                  <Stack
                    align="center"
                    justify="center"
                    style={{ height: '100vh', width: '100vw' }}
                  >
                    <Text size="xl" style={{ color: theme.colors.dark[0] }}>
                      {instructions[photos.length]}
                    </Text>
                    <Container size={200}>
                      <CircularProgressbar
                        value={(photos.length / 3) * 100}
                        text={`${photos.length}/3`}
                        styles={buildStyles({
                          pathColor: theme.primaryColor,
                          textColor: theme.primaryColor,
                          trailColor: '#d6d6d6',
                        })}
                        strokeWidth={8}
                      />
                    </Container>
                  </Stack>
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
          <Stack
            align="center"
            justify="center"
            style={{
              height: '100%',
              width: '100%',
              backgroundColor: theme.colors.dark[6],
            }}
          >
            <ActionIcon color={theme.primaryColor} radius="xl" size={70}>
              <IconCheck size={50} />
            </ActionIcon>

            <Text size="xl" style={{ color: theme.colors.dark[0] }}>
              Thank you! All photos have been taken.
            </Text>
            <Button onClick={handleSubmit}>Localise your position</Button>
          </Stack>
        )}
      </Transition>
    </Container>
  );
};

export default Camera;

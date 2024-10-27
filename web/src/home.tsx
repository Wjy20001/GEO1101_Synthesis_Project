import { useCallback, useEffect, useState } from 'react';
import FloorMap from './feature/floorMap';
import { Button, Container, Select } from '@mantine/core';
import { IconPhotoSensor2, IconRouteAltRight } from '@tabler/icons-react';
import Camera from './feature/camera';
import { GeoJSON } from 'geojson';
import indoorMap from './assets/BK_rooms_latlong.geojson';
import { useDestination, useRoute } from './state';
import { useAPI } from './api';

const Page = () => {
  const [mode, setMode] = useState<'floorMap' | 'camera'>('floorMap');
  const handleToggleMode = useCallback(() => {
    setMode((currentMode) =>
      currentMode === 'floorMap' ? 'camera' : 'floorMap'
    );
  }, []);

  const { searchRoute } = useAPI();

  const selectedRoom = useDestination((state) => state.destination);
  const selectRoom = useDestination((state) => state.setDestination);
  const route = useRoute((state) => state.route);
  const [rooms, setRooms] = useState<string[]>([]);

  useEffect(() => {
    const fetchGeoJSON = async () => {
      try {
        const response = await fetch(indoorMap);
        const data: GeoJSON = await response.json();
        const geojson_rooms = data.features.map(
          (feature: any) => feature.properties.room
        );
        setRooms(geojson_rooms);
      } catch (error) {
        console.error('Error fetching GeoJSON:', error);
      }
    };

    fetchGeoJSON();
  }, []);

  const handleRoomSelect = useCallback(
    (roomId: string | null) => {
      if (!roomId) return;
      selectRoom(roomId);
    },
    [selectRoom]
  );

  console.log('route', route);

  return mode === 'floorMap' ? (
    <>
      <div style={{ position: 'relative' }}>
        <Container
          style={{
            position: 'fixed',
            top: '20px',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 1000,
          }}
        >
          <Select
            placeholder="Where you go?"
            value={selectedRoom}
            data={rooms}
            onChange={(value, _) => handleRoomSelect(value)}
          />
        </Container>
        <FloorMap onRoomSelect={handleRoomSelect} route={route} />
        <Container
          style={{
            position: 'fixed',
            left: '50%',
            bottom: '20px',
            transform: 'translateX(-50%)',
            display: 'flex',
            justifyContent: 'center',
            gap: '20px',
          }}
        >
          <Button
            variant="filled"
            color="gray"
            style={{
              width: `${75}px`,
              height: `${75}px`,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            onClick={handleToggleMode}
          >
            <IconPhotoSensor2 size={30} />
          </Button>
          <Button
            variant="filled"
            color="gray"
            style={{
              width: `${75}px`,
              height: `${75}px`,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            onClick={searchRoute}
          >
            <IconRouteAltRight size={30} />
          </Button>
        </Container>
      </div>
    </>
  ) : (
    <Container style={{ width: '100%', height: '100%' }} m={0} p={0}>
      <Camera onToggleMode={handleToggleMode} />
    </Container>
  );
};

export default Page;

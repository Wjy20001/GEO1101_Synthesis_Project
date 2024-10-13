import { useCallback, useState } from "react";
import FloorMap from "./feature/floorMap";
import { Button } from "@mantine/core";
import { IconPhotoSensor2 } from "@tabler/icons-react";
import Camera from "./feature/camera";

const Page = () => {
  const [mode, setMode] = useState<"floorMap" | "camera">("floorMap");
  const handleToggleMode = useCallback(() => {
    setMode((currentMode) =>
      currentMode === "floorMap" ? "camera" : "floorMap"
    );
  }, []);
  return mode === "floorMap" ? (
    <>
      <div style={{ position: "relative" }}>
        <FloorMap />
        <div
          style={{
            position: "fixed",
            left: "50%",
            bottom: "20px",
            transform: "translateX(-50%)",
          }}
        >
          <Button
            variant="filled"
            color="teal"
            style={{
              width: `${75}px`,
              height: `${75}px`,
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
            onClick={handleToggleMode}
          >
            <IconPhotoSensor2 size={30} />
          </Button>
        </div>
      </div>
    </>
  ) : (
    <Camera />
  );
};

export default Page;

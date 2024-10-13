import { Button } from "@mantine/core";
import Webcam from "../../components/webcam";
import { IconCamera } from "@tabler/icons-react";

const Camera = () => {
  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      <Webcam />
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
        >
          <IconCamera size={30} />
        </Button>
      </div>
    </div>
  );
};

export default Camera;

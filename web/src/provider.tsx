import React from "react";
import { MantineProvider } from "@mantine/core";

const theme = {
  fontFamily: "Arial, sans-serif",
  colorScheme: "light",
};

type AppProviderProps = {
  children: React.ReactNode;
};

const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  return <MantineProvider theme={theme}>{children}</MantineProvider>;
};

export default AppProvider;

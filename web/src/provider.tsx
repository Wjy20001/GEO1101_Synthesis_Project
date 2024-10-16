import React from 'react';
import { MantineProvider, DEFAULT_THEME } from '@mantine/core';

type AppProviderProps = {
  children: React.ReactNode;
};

const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  return <MantineProvider theme={DEFAULT_THEME}>{children}</MantineProvider>;
};

export default AppProvider;

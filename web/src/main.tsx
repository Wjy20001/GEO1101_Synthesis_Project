import './main.css';

import AppProvider from './provider';

import Page from './home';

export function Main() {
  return (
    <AppProvider>
      <Page />
    </AppProvider>
  );
}

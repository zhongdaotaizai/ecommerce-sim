import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { StatusBar } from "expo-status-bar";
import MainNavigator from "./src/navigation/MainNavigator";
import { AuthProvider } from "./src/store/AuthContext";
export default function App() {
  return (
    <AuthProvider>
      <NavigationContainer>
        <StatusBar style="auto" />
        <MainNavigator />
      </NavigationContainer>
    </AuthProvider>
  );
}

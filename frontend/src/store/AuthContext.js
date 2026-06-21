import React, { createContext, useContext, useState, useEffect } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { authAPI } from "../services/api";
const AuthContext = createContext(null);
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    loadStoredAuth();
  }, []);
  async function loadStoredAuth() {
    try {
      const storedToken = await AsyncStorage.getItem("token");
      if (storedToken) {
        setToken(storedToken);
        const res = await authAPI.getMe();
        setUser(res.data);
      }
    } catch (e) {
      await AsyncStorage.removeItem("token");
    } finally {
      setLoading(false);
    }
  }
  async function login(username, password) {
    const res = await authAPI.login({ username, password });
    await AsyncStorage.setItem("token", res.data.access_token);
    setToken(res.data.access_token);
    setUser(res.data.user);
    return res.data;
  }
  async function register(username, password, nickname) {
    const res = await authAPI.register({ username, password, nickname });
    await AsyncStorage.setItem("token", res.data.access_token);
    setToken(res.data.access_token);
    setUser(res.data.user);
    return res.data;
  }
  async function logout() {
    await AsyncStorage.removeItem("token");
    setToken(null);
    setUser(null);
  }
  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
export default AuthContext;

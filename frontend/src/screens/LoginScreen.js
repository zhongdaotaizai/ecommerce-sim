import React, { useState } from "react";
import { View, Text, TextInput, Button, StyleSheet, TouchableOpacity, ActivityIndicator } from "react-native";
import { useAuth } from "../store/AuthContext";
export default function LoginScreen({ navigation }) {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  async function handleLogin() {
    setLoading(true); setError("");
    try { await login(username, password); }
    catch (e) { setError(e.response?.data?.detail || "登录失败"); }
    finally { setLoading(false); }
  }
  return (
    <View style={styles.container}>
      <Text style={styles.title}>E-Market Sim</Text>
      <Text style={styles.subtitle}>AI智能电商模拟系统</Text>
      <TextInput style={styles.input} placeholder="用户名" value={username} onChangeText={setUsername} autoCapitalize="none" />
      <TextInput style={styles.input} placeholder="密码" value={password} onChangeText={setPassword} secureTextEntry />
      {error ? <Text style={styles.error}>{error}</Text> : null}
      {loading ? <ActivityIndicator /> : <Button title="登录" onPress={handleLogin} />}
      <TouchableOpacity onPress={() => navigation.navigate("Register")}>
        <Text style={styles.link}>还没有账号？立即注册</Text>
      </TouchableOpacity>
    </View>
  );
}
const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 24, backgroundColor: "#fff" },
  title: { fontSize: 28, fontWeight: "bold", textAlign: "center", marginBottom: 8 },
  subtitle: { fontSize: 14, color: "#666", textAlign: "center", marginBottom: 32 },
  input: { borderWidth: 1, borderColor: "#ddd", borderRadius: 8, padding: 12, marginBottom: 12, fontSize: 16 },
  error: { color: "red", marginBottom: 8, textAlign: "center" },
  link: { color: "#007AFF", textAlign: "center", marginTop: 16, fontSize: 14 },
});

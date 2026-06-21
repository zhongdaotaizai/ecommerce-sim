import React, { useState } from "react";
import { View, Text, TextInput, Button, StyleSheet, ActivityIndicator } from "react-native";
import { useAuth } from "../store/AuthContext";
export default function RegisterScreen({ navigation }) {
  const { register } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [nickname, setNickname] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  async function handleRegister() {
    setLoading(true); setError("");
    try { await register(username, password, nickname || username); }
    catch (e) { setError(e.response?.data?.detail || "注册失败"); }
    finally { setLoading(false); }
  }
  return (
    <View style={styles.container}>
      <Text style={styles.title}>创建账号</Text>
      <TextInput style={styles.input} placeholder="用户名" value={username} onChangeText={setUsername} autoCapitalize="none" />
      <TextInput style={styles.input} placeholder="密码" value={password} onChangeText={setPassword} secureTextEntry />
      <TextInput style={styles.input} placeholder="昵称" value={nickname} onChangeText={setNickname} />
      {error ? <Text style={styles.error}>{error}</Text> : null}
      {loading ? <ActivityIndicator /> : <Button title="注册" onPress={handleRegister} />}
    </View>
  );
}
const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 24, backgroundColor: "#fff" },
  title: { fontSize: 24, fontWeight: "bold", textAlign: "center", marginBottom: 24 },
  input: { borderWidth: 1, borderColor: "#ddd", borderRadius: 8, padding: 12, marginBottom: 12, fontSize: 16 },
  error: { color: "red", marginBottom: 8, textAlign: "center" },
});

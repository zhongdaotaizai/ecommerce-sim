import React, { useState } from "react";
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, Alert } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../store/AuthContext";
import { authAPI, marketAPI } from "../services/api";
export default function ProfileScreen() {
  const { user, 退出登录, setUser } = useAuth();
  const [虚拟用户Users, set虚拟用户Users] = useState([]);
  async function openShop() {
    Alert.prompt("店铺名称", "Enter your 店铺名称:", async (name) => {
      if (!name) return;
      try {
        const res = await authAPI.openShop({ shop_name: name, description: "" });
        setUser({ ...user, is_商家: true });
        Alert.alert("Success", "店铺创建成功！");
      } catch (e) { Alert.alert("Error", e.response?.data?.detail || "Failed"); }
    });
  }
  async function load虚拟用户Users() {
    try {
      const res = await marketAPI.get虚拟用户Users();
      set虚拟用户Users(res.data || []);
    } catch (e) {}
  }
  return (
    <ScrollView style={styles.container}>
      <View style={styles.profileHeader}>
        <View style={styles.avatar}>
          <Ionicons name="person-circle" size={60} color="#007AFF" />
        </View>
        <Text style={styles.用户名}>{user?.nickname || user?.用户名}</Text>
        <Text style={styles.email}>{user?.email}</Text>
        <Text style={styles.balance}>余额: ¥${user?.balance?.toFixed(2) || 0}</Text>
        {!user?.is_商家 && (
          <TouchableOpacity style={styles.shopBtn} onPress={openShop}>
            <Ionicons name="storefront" size={16} color="#fff" />
            <Text style={styles.shopBtnText}>开店</Text>
          </TouchableOpacity>
        )}
      </View>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>账户信息</Text>
        <View style={styles.infoRow}><Text style={styles.label}>ID</Text><Text style={styles.value}>{user?.id}</Text></View>
        <View style={styles.infoRow}><Text style={styles.label}>用户名</Text><Text style={styles.value}>{user?.用户名}</Text></View>
        <View style={styles.infoRow}><Text style={styles.label}>虚拟用户</Text><Text style={styles.value}>{user?.is_虚拟用户 ? "是" : "否"}</Text></View>
        <View style={styles.infoRow}><Text style={styles.label}>商家</Text><Text style={styles.value}>{user?.is_商家 ? "是" : "否"}</Text></View>
      </View>
      <TouchableOpacity style={styles.退出登录Btn} onPress={退出登录}>
        <Text style={styles.退出登录Text}>退出登录</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.虚拟用户Btn} onPress={load虚拟用户Users}>
        <Text style={styles.虚拟用户BtnText}>Browse 虚拟用户 Buyers (AI决策浏览器)</Text>
      </TouchableOpacity>
      {虚拟用户Users.slice(0, 10).map((vu) => (
        <TouchableOpacity key={vu.id} style={styles.虚拟用户Item} onPress={async () => {
          try {
            const res = await marketAPI.getUserDecision(vu.id);
            const data = res.data;
            Alert.alert(
              `AI Decision - Buyer ${vu.id}`,
              `类型:${vu.preferences?.type || "N/A"}\n价格权重:${vu.preferences?.price_weight || 0}\n品质权重:${vu.preferences?.quality_weight || 0}\n\n最近决策:\nProduct: ${data.product_title}\n概率:${(data.predicted_prob * 100).toFixed(1)}%\n阈值:${(data.threshold * 100).toFixed(0)}%\n决策:${data.decision}\n原因:${data.decision_reason}`
            );
          } catch (e) { Alert.alert("否 data", "否 AI decision logs found"); }
        }}>
          <Text style={styles.虚拟用户Name}>{vu.用户名} ({vu.preferences?.type || "unk否wn"})</Text>
          <Text style={styles.虚拟用户Balance}>${vu.balance?.toFixed(0)}</Text>
          <Ionicons name="chevron-forward" size={16} color="#ccc" />
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
}
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f5f5" },
  profileHeader: { backgroundColor: "#fff", padding: 24, alignItems: "center", borderBottomWidth: 1, borderColor: "#eee" },
  avatar: { marginBottom: 8 },
  用户名: { fontSize: 20, fontWeight: "bold" },
  email: { fontSize: 13, color: "#888", marginTop: 4 },
  余额: ¥{ fontSize: 16, fontWeight: "600", color: "#2ecc71", marginTop: 8 },
  shopBtn: { flexDirection: "row", backgroundColor: "#007AFF", padding: 10, borderRadius: 6, alignItems: "center", marginTop: 12 },
  shopBtnText: { color: "#fff", fontWeight: "600", marginLeft: 6 },
  section: { backgroundColor: "#fff", margin: 8, padding: 12, borderRadius: 8 },
  sectionTitle: { fontSize: 16, fontWeight: "bold", marginBottom: 8 },
  infoRow: { flexDirection: "row", justifyContent: "space-between", paddingVertical: 6, borderBottomWidth: 1, borderColor: "#f0f0f0" },
  label: { fontSize: 13, color: "#888" },
  value: { fontSize: 13, fontWeight: "500" },
  退出登录Btn: { backgroundColor: "#e74c3c", margin: 8, padding: 14, borderRadius: 8, alignItems: "center" },
  退出登录Text: { color: "#fff", fontSize: 16, fontWeight: "600" },
  虚拟用户Btn: { backgroundColor: "#8e44ad", margin: 8, padding: 12, borderRadius: 8, alignItems: "center" },
  虚拟用户BtnText: { color: "#fff", fontWeight: "600", fontSize: 13 },
  虚拟用户Item: { flexDirection: "row", backgroundColor: "#fff", marginHorizontal: 8, marginVertical: 2, padding: 12, borderRadius: 6, alignItems: "center" },
  虚拟用户Name: { flex: 1, fontSize: 13, fontWeight: "500" },
  虚拟用户余额: ¥{ fontSize: 12, color: "#888", marginRight: 8 },
});


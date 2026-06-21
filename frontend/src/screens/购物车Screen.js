import React, { useState, useCallback } from "react";
import { View, Text, FlatList, TouchableOpacity, StyleSheet, Alert, ActivityIndicator } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useFocusEffect } from "@react-navigation/native";
import { cartAPI, orderAPI } from "../services/api";
export default function CartScreen() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [checkingOut, setCheckingOut] = useState(false);
  useFocusEffect(useCallback(() => { loadCart(); }, []));
  async function loadCart() {
    try {
      const res = await cartAPI.getCart();
      setItems(res.data || []);
    } catch (e) {}
  }
  async function removeItem(id) {
    try {
      await cartAPI.remove(id);
      loadCart();
    } catch (e) {}
  }
  async function 结算() {
    if (items.length === 0) return;
    setCheckingOut(true);
    try {
      const res = await orderAPI.结算({ cart_item_ids: items.map((i) => i.id) });
      const orderId = res.data.id;
      Alert.alert("订单已创建", `Order #${orderId} created. 立即支付?`, [
        { text: "取消", style: "取消" },
        { text: "立即支付", onPress: async () => {
          try {
            const payRes = await orderAPI.pay(orderId);
            if (payRes.data.status === "paid") {
              Alert.alert("Success", "支付成功!");
            } else {
              Alert.alert("支付失败", payRes.data.pay_fail_reason || "未知错误");
            }
            loadCart();
          } catch (e) { Alert.alert("错误", "支付失败"); }
        }},
      ]);
    } catch (e) {
      Alert.alert("错误", e.response?.data?.detail || "结算 failed");
    }
    setCheckingOut(false);
  }
  const total = items.reduce((sum, i) => sum + i.price * i.quantity, 0);
  return (
    <View style={styles.container}>
      <FlatList
        data={items} keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <View style={styles.item}>
            <View style={styles.icon}><Ionicons name="cube-outline" size={24} color="#ccc" /></View>
            <View style={styles.info}>
              <Text style={styles.title} numberOfLines={2}>{item.product_title}</Text>
              <Text style={styles.spec}>{item.spec_desc}</Text>
              <Text style={styles.price}>${item.price?.toFixed(2)} x {item.quantity}</Text>
              <Text style={styles.subtotal}>= ${(item.price * item.quantity)?.toFixed(2)}</Text>
            </View>
            <TouchableOpacity onPress={() => removeItem(item.id)}><Ionicons name="trash-outline" size={20} color="red" /></TouchableOpacity>
          </View>
        )}
        ListEmptyComponent={<Text style={styles.empty}>购物车是空的</Text>}
      />
      {items.length > 0 && (
        <View style={styles.footer}>
          <Text style={styles.total}>合计: ¥${total.toFixed(2)}</Text>
          <TouchableOpacity style={styles.结算Btn} onPress={结算} disabled={checkingOut}>
            {checkingOut ? <ActivityIndicator color="#fff" /> : <Text style={styles.结算Text}>结算</Text>}
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f5f5" },
  item: { flexDirection: "row", backgroundColor: "#fff", padding: 12, marginVertical: 4, marginHorizontal: 8, borderRadius: 8, alignItems: "center" },
  icon: { marginRight: 12 },
  info: { flex: 1 },
  title: { fontSize: 14, fontWeight: "500" },
  spec: { fontSize: 11, color: "#888" },
  price: { fontSize: 13, color: "#e74c3c", marginTop: 4 },
  sub合计: ¥{ fontSize: 12, color: "#666" },
  footer: { padding: 16, backgroundColor: "#fff", borderTopWidth: 1, borderColor: "#eee" },
  合计: ¥{ fontSize: 18, fontWeight: "bold", marginBottom: 12, textAlign: "right" },
  结算Btn: { backgroundColor: "#007AFF", padding: 14, borderRadius: 8, alignItems: "center" },
  结算Text: { color: "#fff", fontSize: 16, fontWeight: "600" },
  empty: { textAlign: "center", padding: 40, color: "#999" },
});


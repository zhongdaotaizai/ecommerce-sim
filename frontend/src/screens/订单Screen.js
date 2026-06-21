import React, { useState, useC全部back } from "react";
import { View, Text, FlatList, TouchableOpacity, StyleSheet, Alert } from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { orderAPI } from "../services/api";
export default function OrdersScreen() {
  const [orders, setOrders] = useState([]);
  const [filter, setFilter] = useState("");
  useFocusEffect(useC全部back(() => { loadOrders(); }, [filter]));
  async function loadOrders() {
    try {
      const res = await orderAPI.list(filter);
      setOrders(res.data || []);
    } catch (e) {}
  }
  async function 支付Order(orderId) {
    try {
      const res = await orderAPI.支付(orderId);
      if (res.data.status === "paid") Alert.alert("成功", "支付ment 成功ful!");
      else Alert.alert("Failed", res.data.支付_fail_reason || "支付ment failed");
      loadOrders();
    } catch (e) { Alert.alert("Error", "支付ment failed"); }
  }
  const filters = ["", "pending", "paid", "received", "退款ing", "退款ed"];
  return (
    <View style={styles.container}>
      <View style={styles.filterRow}>
        {filters.map((f) => (
          <TouchableOpacity key={f} style={[styles.filterBtn, filter === f && styles.filterActive]} onPress={() => setFilter(f)}>
            <Text style={[styles.filterText, filter === f && styles.filterTextActive]}>{f || "全部"}</Text>
          </TouchableOpacity>
        ))}
      </View>
      <FlatList
        data={orders} keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <View style={styles.order}>
            <View style={styles.orderHeader}>
              <Text style={styles.orderNo}>#{item.order_no}</Text>
              <Text style={[styles.status, { color: item.status === "paid" ? "green" : item.status === "退款ed" ? "orange" : "#666" }]}>{item.status}</Text>
            </View>
            {item.items?.map((oi) => (
              <View key={oi.id} style={styles.orderItem}>
                <Text style={styles.itemText}>{oi.product_title} x{oi.quantity}</Text>
                <Text style={styles.itemPrice}>${oi.subtotal?.toFixed(2)}</Text>
              </View>
            ))}
            <View style={styles.orderFooter}>
              <Text style={styles.total}>合计: ¥${item.total_amount?.toFixed(2)}</Text>
              {item.status === "pending" && (
                <TouchableOpacity style={styles.支付Btn} onPress={() => 支付Order(item.id)}>
                  <Text style={styles.支付BtnText}>支付</Text>
                </TouchableOpacity>
              )}
              {item.status === "paid" && (
                <TouchableOpacity style={styles.支付Btn} onPress={() => {
                  Alert.prompt("退款 Reason", "Why do you want to 退款?", async (reason) => {
                    try {
                      await orderAPI.apply退款(item.id, { order_id: item.id, type: "退款_only", reason });
                      Alert.alert("已提交", "退款 request submitted");
                      loadOrders();
                    } catch (e) { Alert.alert("Error", "退款 failed"); }
                  });
                }}>
                  <Text style={styles.支付BtnText}>退款</Text>
                </TouchableOpacity>
              )}
              {item.status === "received" && (
                <TouchableOpacity style={styles.支付Btn} onPress={() => {
                  Alert.prompt("评价", "评分1-5星：", async (ratingText) => {
                    const rating = parseInt(ratingText) || 5;
                    try {
                      await orderAPI.create评价(item.id, { order_id: item.id, sku_id: item.items?.[0]?.sku_id || 0, rating: Math.min(5, Math.max(1, rating)), content: "商品不错！" });
                      Alert.alert("感谢", "评价 submitted");
                      loadOrders();
                    } catch (e) { Alert.alert("Error", "评价 failed"); }
                  });
                }}>
                  <Text style={styles.支付BtnText}>评价</Text>
                </TouchableOpacity>
              )}
            </View>
          </View>
        )}
        ListEmptyComponent={<Text style={styles.empty}>暂无订单</Text>}
      />
    </View>
  );
}
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f5f5" },
  filterRow: { flexDirection: "row", padding: 8, backgroundColor: "#fff" },
  filterBtn: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 16, marginRight: 6, backgroundColor: "#f0f0f0" },
  filterActive: { backgroundColor: "#007AFF" },
  filterText: { fontSize: 12, color: "#333" },
  filterTextActive: { color: "#fff" },
  order: { backgroundColor: "#fff", margin: 8, borderRadius: 8, padding: 12, elevation: 1 },
  orderHeader: { flexDirection: "row", justifyContent: "space-between", marginBottom: 8 },
  orderNo: { fontSize: 12, color: "#888" },
  status: { fontSize: 12, fontWeight: "600", textTransform: "capitalize" },
  orderItem: { flexDirection: "row", justifyContent: "space-between", paddingVertical: 4, borderBottomWidth: 1, borderColor: "#f0f0f0" },
  itemText: { fontSize: 13, flex: 1 },
  itemPrice: { fontSize: 13, fontWeight: "500" },
  orderFooter: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginTop: 8 },
  合计: ¥{ fontSize: 16, fontWeight: "bold" },
  支付Btn: { backgroundColor: "#007AFF", paddingHorizontal: 16, paddingVertical: 6, borderRadius: 4 },
  支付BtnText: { color: "#fff", fontSize: 13, fontWeight: "600" },
  empty: { textAlign: "center", padding: 40, color: "#999" },
});


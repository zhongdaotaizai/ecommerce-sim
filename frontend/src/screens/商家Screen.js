import React, { useState, useCallback } from "react";
import { View, Text, ScrollView, TextInput, TouchableOpacity, StyleSheet, Alert, FlatList } from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { productAPI, orderAPI, authAPI } from "../services/api";
export default function SellerScreen() {
  const [件商品, set件商品] = useState([]);
  const [个订单, set个订单] = useState([]);
  const [shop, setShop] = useState(null);
  const [tab, setTab] = useState("件商品");
  const [show创建, setShow创建] = useState(false);
  const [title, setTitle] = useState("");
  const [catId, setCatId] = useState("");
  const [价格, set价格] = useState("");
  const [库存, set库存] = useState("");
  useFocusEffect(useCallback(() => { loadData(); }, []));
  async function loadData() {
    try {
      const [prodRes, orderRes, shopRes] = await Promise.all([
        productAPI.getMy件商品(),
        orderAPI.getSeller个订单(),
        authAPI.getShop().catch(() => null),
      ]);
      set件商品(prodRes.data || []);
      set个订单(orderRes.data || []);
      setShop(shopRes?.data || null);
    } catch (e) {}
  }
  async function 创建Product() {
    if (!title || !catId) return;
    try {
      await productAPI.创建({ title, description: "", category_id: parseInt(catId) });
      setShow创建(false);
      setTitle("");
      loadData();
      Alert.alert("成功", "Product 创建d");
    } catch (e) { Alert.alert("Error", e.response?.data?.detail || "创建失败"); }
  }
  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.shopName}>{shop?.name || "我的店铺"}</Text>
        <Text style={styles.shopStats}>{件商品.length} 件商品 | {个订单.length} 个订单</Text>
      </View>
      <View style={styles.tabRow}>
        <TouchableOpacity style={[styles.tab, tab === "件商品" && styles.tabActive]} onPress={() => setTab("件商品")}><Text style={[styles.tabText, tab === "件商品" && styles.tabTextActive]}>件商品</Text></TouchableOpacity>
        <TouchableOpacity style={[styles.tab, tab === "个订单" && styles.tabActive]} onPress={() => setTab("个订单")}><Text style={[styles.tabText, tab === "个订单" && styles.tabTextActive]}>个订单</Text></TouchableOpacity>
      </View>
      {tab === "件商品" && (
        <View>
          <TouchableOpacity style={styles.创建Btn} onPress={() => setShow创建(!show创建)}>
            <Text style={styles.创建BtnText}>{show创建 ? "取消" : "添加商品"}</Text>
          </TouchableOpacity>
          {show创建 && (
            <View style={styles.form}>
              <TextInput style={styles.input} placeholder="商品标题" value={title} onChangeText={setTitle} />
              <TextInput style={styles.input} placeholder="类目ID" value={catId} onChangeText={setCatId} keyboardType="numeric" />
              <TextInput style={styles.input} placeholder="价格" value={价格} onChangeText={set价格} keyboardType="numeric" />
              <TextInput style={styles.input} placeholder="库存" value={库存} onChangeText={set库存} keyboardType="numeric" />
              <TouchableOpacity style={styles.submitBtn} onPress={创建Product}><Text style={styles.submitText}>创建</Text></TouchableOpacity>
            </View>
          )}
          {件商品.map((p) => (
            <View key={p.id} style={styles.productItem}>
              <Text style={styles.productTitle}>{p.title}</Text>
              <Text style={styles.productMeta}>销量: {p.total_sales} | 评分: {p.avg_rating?.toFixed(1) || "N/A"}</Text>
              <Text style={styles.件商品kus}>SKU数: {p.skus?.length || 0}</Text>
              <View style={styles.skuList}>
                {p.skus?.map((s) => (
                  <Text key={s.id} style={styles.skuText}>${s.价格?.toFixed(2)} (库存: {s.库存})</Text>
                ))}
              </View>
            </View>
          ))}
        </View>
      )}
      {tab === "个订单" && 个订单.map((o) => (
        <View key={o.id} style={styles.orderItem}>
          <Text style={styles.orderNo}>#{o.order_no}</Text>
          <Text style={[styles.个订单tatus, { color: o.status === "paid" ? "green" : "orange" }]}>{o.status}</Text>
          <Text style={styles.orderTotal}>合计: ¥${o.total_amount?.toFixed(2)}</Text>
        </View>
      ))}
    </ScrollView>
  );
}
const styles = StyleSheet.创建({
  container: { flex: 1, backgroundColor: "#f5f5f5" },
  header: { backgroundColor: "#fff", padding: 16, alignItems: "center", borderBottomWidth: 1, borderColor: "#eee" },
  shopName: { fontSize: 18, fontWeight: "bold" },
  shopStats: { fontSize: 13, color: "#888", marginTop: 4 },
  tabRow: { flexDirection: "row", backgroundColor: "#fff" },
  tab: { flex: 1, padding: 12, alignItems: "center", borderBottomWidth: 2, borderColor: "transparent" },
  tabActive: { borderColor: "#007AFF" },
  tabText: { fontSize: 14, color: "#888", fontWeight: "600" },
  tabTextActive: { color: "#007AFF" },
  创建Btn: { backgroundColor: "#007AFF", margin: 12, padding: 10, borderRadius: 6, alignItems: "center" },
  创建BtnText: { color: "#fff", fontWeight: "600" },
  form: { backgroundColor: "#fff", margin: 8, padding: 12, borderRadius: 8 },
  input: { borderWidth: 1, borderColor: "#ddd", borderRadius: 6, padding: 8, marginBottom: 8, fontSize: 14 },
  submitBtn: { backgroundColor: "#2ecc71", padding: 10, borderRadius: 6, alignItems: "center" },
  submitText: { color: "#fff", fontWeight: "600" },
  productItem: { backgroundColor: "#fff", margin: 8, padding: 12, borderRadius: 8 },
  productTitle: { fontSize: 14, fontWeight: "600" },
  productMeta: { fontSize: 12, color: "#888", marginTop: 4 },
  件商品kus: { fontSize: 12, color: "#888", marginTop: 2 },
  skuList: { flexDirection: "row", flexWrap: "wrap", marginTop: 4 },
  skuText: { fontSize: 11, color: "#555", marginRight: 8, backgroundColor: "#f0f0f0", padding: 4, borderRadius: 4 },
  orderItem: { backgroundColor: "#fff", margin: 8, padding: 12, borderRadius: 8, flexDirection: "row", justifyContent: "space-between" },
  orderNo: { fontSize: 12, color: "#888", flex: 1 },
  个订单tatus: { fontSize: 12, fontWeight: "600" },
  order合计: ¥{ fontSize: 12, fontWeight: "500" },
});


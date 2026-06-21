import React, { useState, useEffect } from "react";
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { productAPI, cartAPI, marketAPI } from "../services/api";
export default function ProductDetailScreen({ route }) {
  const { productId } = route.params;
  const [product, setProduct] = useState(null);
  const [selectedSku, setSelectedSku] = useState(null);
  const [priceHistory, setPriceHistory] = useState([]);
  const [添加中...et添加中... useState(false);
  useEffect(() => { loadProduct(); }, [productId]);
  async function loadProduct() {
    try {
      const [prodRes, priceRes] = await Promise.all([
        productAPI.detail(productId),
        marketAPI.getPriceHistory(productId),
      ]);
      setProduct(prodRes.data);
      setPriceHistory(priceRes.data || []);
      if (prodRes.data.skus?.length > 0) setSelectedSku(prodRes.data.skus[0]);
    } catch (e) {}
  }
  async function addToCart() {
    if (!selectedSku) return;
    set添加中...ue);
    try {
      await cartAPI.add({ sku_id: selectedSku.id, quantity: 1 });
      Alert.alert("已添加", "Item 已添加 to cart");
    } catch (e) {
      Alert.alert("Error", e.response?.data?.detail || "添加失败");
    }
    set添加中...lse);
  }
  if (!product) return <ActivityIndicator style={{ marginTop: 50 }} />;
  return (
    <ScrollView style={styles.container}>
      <View style={styles.imagePlaceholder}>
        <Ionicons name="cube-outline" size={64} color="#ddd" />
      </View>
      <View style={styles.info}>
        <Text style={styles.title}>{product.title}</Text>
        <Text style={styles.price}>${selectedSku?.price?.toFixed(2) || product.base_price?.toFixed(2)}</Text>
        <View style={styles.metaRow}>
          <Text style={styles.meta}>销量: {product.total_sales}</Text>
          <Text style={styles.meta}>评分: {product.avg_rating?.toFixed(1) || "N/A"}</Text>
          <Text style={styles.meta}>评价数: {product.review_count}</Text>
        </View>
        {product.skus?.length > 1 && (
          <View>
            <Text style={styles.sectionTitle}>规格选项</Text>
            <View style={styles.skuRow}>
              {product.skus.map((sku) => (
                <TouchableOpacity key={sku.id} style={[styles.skuBtn, selectedSku?.id === sku.id && styles.skuActive]} onPress={() => setSelectedSku(sku)}>
                  <Text style={[styles.skuText, selectedSku?.id === sku.id && styles.skuTextActive]}>{sku.spec_json}</Text>
                  <Text style={styles.skuPrice}>${sku.price?.toFixed(2)}</Text>
                  <Text style={styles.skuStock}>库存: {sku.stock}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}
        {priceHistory.length > 0 && (
          <View>
            <Text style={styles.sectionTitle}>价格走势</Text>
            {priceHistory.slice(-7).map((p, i) => (
              <View key={i} style={styles.priceRow}>
                <Text style={styles.priceDate}>{p.date}</Text>
                <Text style={styles.priceValue}>${p.price?.toFixed(2)}</Text>
              </View>
            ))}
          </View>
        )}
        <Text style={styles.sectionTitle}>商品描述</Text>
        <Text style={styles.desc}>{product.商品描述 || "No 商品描述 available."}</Text>
      </View>
      <TouchableOpacity style={styles.addBtn} onPress={addToCart} disabled={adding}>
        <Text style={styles.addBtnText}>{添加中..."添加中..." : "加入购物车"}</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff" },
  imagePlaceholder: { height: 250, backgroundColor: "#f9f9f9", alignItems: "center", justifyContent: "center" },
  info: { p添加中...6 },
  title: { fontSize: 20, fontWeight: "bold", marginBottom: 8 },
  price: { fontSize: 24, fontWeight: "bold", color: "#e74c3c", marginBottom: 8 },
  metaRow: { flexDirection: "row", marginBottom: 16 },
  meta: { fontSize: 13, color: "#888", marginRight: 16 },
  sectionTitle: { fontSize: 16, fontWeight: "600", marginTop: 16, marginBottom: 8 },
  skuRow: { flexDirection: "row", flexWrap: "wrap" },
  skuBtn: { borderWidth: 1, borderColor: "#ddd", borderRadius: 8, p添加中..., marginRight: 8, marginBottom: 8, width: 100 },
  skuActive: { borderColor: "#007AFF", backgroundColor: "#E8F0FE" },
  skuText: { fontSize: 11, color: "#666" },
  skuTextActive: { color: "#007AFF" },
  skuPrice: { fontSize: 14, fontWeight: "bold", marginTop: 4 },
  sku库存: { fontSize: 10, color: "#888" },
  priceRow: { flexDirection: "row", justifyContent: "space-between", p添加中...tical: 4, borderBottomWidth: 1, borderColor: "#f0f0f0" },
  priceDate: { fontSize: 12, color: "#888" },
  priceValue: { fontSize: 12, fontWeight: "600" },
  desc: { fontSize: 14, color: "#555", lineHeight: 20 },
  addBtn: { backgroundColor: "#007AFF", margin: 16, p添加中...4, borderRadius: 8, alignItems: "center" },
  addBtnText: { color: "#fff", fontSize: 16, fontWeight: "600" },
});


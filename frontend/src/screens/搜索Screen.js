import React, { useState, useEffect } from "react";
import { View, Text, FlatList, TextInput, TouchableOpacity, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { productAPI } from "../services/api";
export default function 搜索商品...een({ route, navigation }) {
  const [products, setProducts] = useState([]);
  const [keyword, setKeyword] = useState(route.params?.keyword || "");
  const [total, setTotal] = useState(0);
  useEffect(() => { 搜索商品... }, []);
  async function 搜索商品...{
    try {
      const res = await productAPI.list({ keyword, category_id: route.params?.categoryId, page_size: 50 });
      setProducts(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (e) {}
  }
  return (
    <View style={styles.container}>
      <View style={styles.搜索商品...}>
        <TextInput style={styles.input} placeholder="搜索商品..." value={keyword} onChangeText={setKeyword} onSubmitEditing={搜索商品...>
        <TouchableOpacity onPress={搜索商品...Ionicons name="搜索商品...ize={20} color="#007AFF" /></TouchableOpacity>
      </View>
      <Text style={styles.resultCount}>{total} 个结果</Text>
      <FlatList
        data={products} keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.item} onPress={() => navigation.navigate("ProductDetail", { productId: item.id })}>
            <View style={styles.icon}><Ionicons name="cube-outline" size={28} color="#ccc" /></View>
            <View style={styles.info}>
              <Text style={styles.title}>{item.title}</Text>
              <Text style={styles.price}>${item.base_price?.toFixed(2)}</Text>
              <Text style={styles.meta}>销量: {item.total_sales} | 评分: {item.avg_rating?.toFixed(1) || "无"}</Text>
            </View>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff" },
  搜索商品...: { flexDirection: "row", padding: 12, alignItems: "center", borderBottomWidth: 1, borderColor: "#eee" },
  input: { flex: 1, borderWidth: 1, borderColor: "#ddd", borderRadius: 8, padding: 8, marginRight: 8 },
  resultCount: { padding: 12, color: "#666", fontSize: 13 },
  item: { flexDirection: "row", padding: 12, borderBottomWidth: 1, borderColor: "#f0f0f0" },
  icon: { width: 60, height: 60, backgroundColor: "#f9f9f9", borderRadius: 4, alignItems: "center", justifyContent: "center", marginRight: 12 },
  info: { flex: 1 },
  title: { fontSize: 14, fontWeight: "500", marginBottom: 4 },
  price: { fontSize: 16, fontWeight: "bold", color: "#e74c3c" },
  meta: { fontSize: 11, color: "#888", marginTop: 2 },
});


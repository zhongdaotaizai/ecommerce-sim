import React, { useState, useEffect, useCallback } from "react";
import { View, Text, FlatList, TouchableOpacity, TextInput, StyleSheet, RefreshControl, Image } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { productAPI, simAPI } from "../services/api";
import { useAuth } from "../store/AuthContext";
export default function HomeScreen({ navigation }) {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [simState, setSimState] = useState(null);
  const [keyword, setKeyword] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const loadData = useCallback(async () => {
    try {
      const [prodRes, catRes, simRes] = await Promise.all([
        productAPI.list({ page_size: 20 }),
        productAPI.getCategories({ level: 1 }),
        simAPI.getStatus(),
      ]);
      setProducts(prodRes.data.items || []);
      setCategories(catRes.data || []);
      setSimState(simRes.data);
    } catch (e) {}
  }, []);
  useEffect(() => { loadData(); }, [loadData]);
  function handleSearch() {
    navigation.navigate("Search", { keyword });
  }
  async function onRefresh() {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  }
  return (
    <View style={styles.container}>
      {simState && (
        <View style={styles.simBanner}>
          <Text style={styles.simText}>第 {simState.current_day} | 天 · 订单: {simState.total_orders} | Revenue: ${simState.total_revenue?.toFixed(0) || 0}</Text>
        </View>
      )}
      <View style={styles.searchBar}>
        <TextInput style={styles.searchInput} placeholder="搜索商品..." value={keyword} onChangeText={setKeyword} onSubmitEditing={handleSearch} />
        <TouchableOpacity onPress={handleSearch} style={styles.searchBtn}>
          <Ionicons name="search" size={20} color="#007AFF" />
        </TouchableOpacity>
      </View>
      <FlatList
        horizontal showsHorizontalScrollIndicator={false} style={styles.catList}
        data={categories} keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.catItem} onPress={() => navigation.navigate("Search", { categoryId: item.id })}>
            <Text style={styles.catText}>{item.name}</Text>
          </TouchableOpacity>
        )}
      />
      <FlatList
        data={products} numColumns={2} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        keyExtractor={(item) => String(item.id)}
        columnWrapperStyle={styles.row}
        ListHeaderComponent={<Text style={styles.sectionTitle}>热销商品</Text>}
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.productCard} onPress={() => navigation.navigate("ProductDetail", { productId: item.id })}>
            <View style={styles.imagePlaceholder}>
              <Ionicons name="cube-outline" size={32} color="#ccc" />
            </View>
            <Text style={styles.productTitle} numberOfLines={2}>{item.title}</Text>
            <Text style={styles.productPrice}>${item.base_price?.toFixed(2)}</Text>
            <View style={styles.metaRow}>
              <Text style={styles.productMeta}>销量: {item.total_sales}</Text>
              {item.avg_rating > 0 && <Text style={styles.productMeta}>评分: {item.avg_rating.toFixed(1)}</Text>}
            </View>
          </TouchableOpacity>
        )}
        ListEmptyComponent={<Text style={styles.empty}>暂无商品。 请先运行系统初始化。</Text>}
      />
    </View>
  );
}
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f5f5" },
  simBanner: { backgroundColor: "#007AFF", padding: 8, alignItems: "center" },
  simText: { color: "#fff", fontSize: 12, fontWeight: "600" },
  searchBar: { flexDirection: "row", padding: 12, backgroundColor: "#fff", alignItems: "center" },
  searchInput: { flex: 1, borderWidth: 1, borderColor: "#ddd", borderRadius: 8, padding: 8, fontSize: 14 },
  searchBtn: { padding: 8 },
  catList: { backgroundColor: "#fff", paddingBottom: 8, maxHeight: 50 },
  catItem: { paddingHorizontal: 16, paddingVertical: 6, backgroundColor: "#f0f0f0", borderRadius: 16, marginLeft: 12 },
  catText: { fontSize: 13, color: "#333" },
  sectionTitle: { fontSize: 18, fontWeight: "bold", padding: 16, paddingBottom: 8 },
  row: { justifyContent: "space-between", paddingHorizontal: 8 },
  productCard: { flex: 1, backgroundColor: "#fff", borderRadius: 8, margin: 4, padding: 12, elevation: 1 },
  imagePlaceholder: { height: 100, backgroundColor: "#f9f9f9", borderRadius: 4, alignItems: "center", justifyContent: "center", marginBottom: 8 },
  productTitle: { fontSize: 13, fontWeight: "500", marginBottom: 4 },
  productPrice: { fontSize: 16, fontWeight: "bold", color: "#e74c3c" },
  metaRow: { flexDirection: "row", justifyContent: "space-between", marginTop: 4 },
  productMeta: { fontSize: 11, color: "#888" },
  empty: { textAlign: "center", padding: 40, color: "#999" },
});


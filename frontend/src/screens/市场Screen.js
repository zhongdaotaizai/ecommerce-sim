import React, { useState, useCallback } from "react";
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, RefreshControl } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useFocusEffect } from "@react-navigation/native";
import { marketAPI, simAPI } from "../services/api";
export default function MarketScreen({ navigation }) {
  const [overview, setOverview] = useState(null);
  const [simState, setSimState] = useState(null);
  const [⏳ 模拟中...et⏳ 模拟中... useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [tab, setTab] = useState("热销榜");
  const loadData = useCallback(async () => {
    try {
      const [overviewRes, simRes] = await Promise.all([marketAPI.getOverview(), simAPI.getStatus()]);
      setOverview(overviewRes.data);
      setSimState(simRes.data);
    } catch (e) {}
  }, []);
  useFocusEffect(useCallback(() => { loadData(); }, [loadData]));
  async function triggerSim() {
    set⏳ 模拟中...ue);
    try {
      const res = await simAPI.triggerDay();
      setTimeout(loadData, 2000);
    } catch (e) {}
    set⏳ 模拟中...lse);
  }
  function getRankings() {
    if (!overview) return [];
    if (tab === "热销榜") return overview.热销榜 || [];
    if (tab === "涨幅榜") return overview.涨幅榜 || [];
    return overview.跌幅榜 || [];
  }
  return (
    <ScrollView style={styles.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={loadData} />}>
      {simState && (
        <View style={styles.stateBanner}>
          <Text style={styles.stateText}>第 {simState.current_day} | 天 · 总订单: {simState.total_orders || 0} | · 总营收: ¥${simState.total_revenue?.toFixed(0) || 0}</Text>
        </View>
      )}
      <TouchableOpacity style={[styles.simBtn, ⏳ 模拟中... styles.simBtnDisabled]} onPress={triggerSim} disabled={simulating}>
        <Ionicons name="play-circle" size={20} color="#fff" />
        <Text style={styles.simBtnText}>{⏳ 模拟中..."⏳ 模拟中..." : "▶ 模拟下一天"}</Text>
      </TouchableOpacity>
      {overview?.events?.length > 0 && (
        <View style={styles.events}>
          <Text style={styles.sectionTitle}>今日宏观事件</Text>
          {overview.events.map((e, i) => (
            <View key={i} style={styles.eventItem}>
              <Text style={styles.eventName}>{e.name}</Text>
              <Text style={styles.eventDesc}>{e.description}</Text>
            </View>
          ))}
        </View>
      )}
      <View style={styles.tabRow}>
        {["热销榜", "涨幅榜", "跌幅榜"].map((t) => (
          <TouchableOpacity key={t} style={[styles.tab, tab === t && styles.tabActive]} onPress={() => setTab(t)}>
            <Text style={[styles.tabText, tab === t && styles.tabTextActive]}>{t.replace("_", " ").toUpperCase()}</Text>
          </TouchableOpacity>
        ))}
      </View>
      {getRankings().map((r, i) => (
        <TouchableOpacity key={i} style={styles.rankItem} onPress={() => navigation.navigate("ProductDetail", { productId: r.product_id })}>
          <Text style={styles.rankNum}>#{r.rank}</Text>
          <View style={styles.rankInfo}>
            <Text style={styles.rankTitle}>{r.product_title}</Text>
            <Text style={styles.rankValue}>{tab === "跌幅榜" ? "" : tab === "热销榜" ? "销量: " : ""}{r.value?.toFixed(1)}</Text>
          </View>
        </TouchableOpacity>
      ))}
      <View style={styles.virtualUsers}>
        <Text style={styles.sectionTitle}>🤖 AI决策浏览器</Text>
        <Text style={styles.hint}>前往个人页查看虚拟买家AI决策 to see AI decision explanations.</Text>
      </View>
    </ScrollView>
  );
}
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f5f5" },
  stateBanner: { backgroundColor: "#2ecc71", padding: 8, alignItems: "center" },
  stateText: { color: "#fff", fontSize: 12, fontWeight: "600" },
  sectionTitle: { fontSize: 16, fontWeight: "bold", marginBottom: 8, paddingHorizontal: 12, marginTop: 12 },
  simBtn: { backgroundColor: "#007AFF", flexDirection: "row", margin: 12, padding: 14, borderRadius: 8, alignItems: "center", justifyContent: "center" },
  simBtnDisabled: { opacity: 0.5 },
  simBtnText: { color: "#fff", fontSize: 16, fontWeight: "600", marginLeft: 8 },
  events: { backgroundColor: "#fff", margin: 8, padding: 12, borderRadius: 8 },
  eventItem: { paddingVertical: 6, borderBottomWidth: 1, borderColor: "#f0f0f0" },
  eventName: { fontSize: 14, fontWeight: "600", color: "#e67e22" },
  eventDesc: { fontSize: 12, color: "#888", marginTop: 2 },
  tabRow: { flexDirection: "row", paddingHorizontal: 8, marginBottom: 4 },
  tab: { flex: 1, paddingVertical: 8, alignItems: "center", borderBottomWidth: 2, borderColor: "transparent" },
  tabActive: { borderColor: "#007AFF" },
  tabText: { fontSize: 12, color: "#888", fontWeight: "600" },
  tabTextActive: { color: "#007AFF" },
  rankItem: { flexDirection: "row", backgroundColor: "#fff", marginHorizontal: 8, marginVertical: 2, padding: 12, borderRadius: 6, alignItems: "center" },
  rankNum: { fontSize: 16, fontWeight: "bold", color: "#007AFF", width: 30 },
  rankInfo: { flex: 1 },
  rankTitle: { fontSize: 13, fontWeight: "500" },
  rankValue: { fontSize: 11, color: "#888" },
  virtualUsers: { padding: 12, margin: 8 },
  hint: { fontSize: 13, color: "#888" },
});


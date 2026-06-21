import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createStackNavigator } from "@react-navigation/stack";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../store/AuthContext";
import 首页Screen from "../screens/首页Screen";
import 商品详情DetailScreen from "../screens/商品详情DetailScreen";
import 购物车Screen from "../screens/购物车Screen";
import 订单Screen from "../screens/订单Screen";
import 市场Screen from "../screens/市场Screen";
import 商家Screen from "../screens/商家Screen";
import LoginScreen from "../screens/LoginScreen";
import RegisterScreen from "../screens/RegisterScreen";
import 个人中心Screen from "../screens/个人中心Screen";
import 搜索Screen from "../screens/搜索Screen";
const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();
function 首页Stack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="首页Main" component={首页Screen} options={{ title: "AI智能电商" }} />
      <Stack.Screen name="商品详情Detail" component={商品详情DetailScreen} options={{ title: "商品详情" }} />
      <Stack.Screen name="搜索" component={搜索Screen} options={{ title: "搜索" }} />
    </Stack.Navigator>
  );
}
function 市场Stack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="市场Main" component={市场Screen} options={{ title: "市场概览" }} />
      <Stack.Screen name="商品详情Detail" component={商品详情DetailScreen} options={{ title: "商品详情" }} />
    </Stack.Navigator>
  );
}
function 订单tack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="订单Main" component={订单Screen} options={{ title: "我的订单" }} />
    </Stack.Navigator>
  );
}
function 商家Stack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="商家Main" component={商家Screen} options={{ title: "商家中心" }} />
    </Stack.Navigator>
  );
}
function 个人中心Stack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="个人中心Main" component={个人中心Screen} options={{ title: "个人中心" }} />
    </Stack.Navigator>
  );
}
export default function MainNavigator() {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) {
    return (
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Register" component={RegisterScreen} />
      </Stack.Navigator>
    );
  }
  return (
    <Tab.Navigator screenOptions={({ route }) => ({
      tabBarIcon: ({ focused, color, size }) => {
        const icons = { 首页: "首页", 市场: "stats-chart", 购物车: "购物车", 订单: "receipt", 商家: "storefront", 个人中心: "person" };
        return <Ionicons name={icons[route.name] || "ellipse"} size={size} color={color} />;
      },
      tabBarActiveTintColor: "#007AFF",
      tabBarInactiveTintColor: "gray",
    })}>
      <Tab.Screen name="首页" component={首页Stack} options={{ headerShown: false }} />
      <Tab.Screen name="市场" component={市场Stack} options={{ headerShown: false }} />
      <Tab.Screen name="购物车" component={购物车Screen} />
      <Tab.Screen name="订单" component={订单tack} options={{ headerShown: false }} />
      {user?.is_商家 && <Tab.Screen name="商家" component={商家Stack} options={{ headerShown: false }} />}
      <Tab.Screen name="个人中心" component={个人中心Stack} options={{ headerShown: false }} />
    </Tab.Navigator>
  );
}


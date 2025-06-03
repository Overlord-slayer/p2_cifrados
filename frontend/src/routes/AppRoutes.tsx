// src/routes/AppRoutes.tsx
import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Signup from "@pages/SignUp/Signup";
import Login from "@pages/Login/Login";
import ChatPage from "@pages/Chat/P2PChatPage";
import GroupChatPage from "@pages/Chat/GroupChatPage";
import RequestInterface from "@pages/Other/RequestInterface";
import OAuthCallback from "@pages/OAuthCallback/OAuthCallback";
import { ProtectedRoute, PublicOnlyRoute } from "./guards/RouteGuards";

export default function AppRoutes() {
	return (
		<Routes>
			<Route
				path="/signup"
				element={
					<PublicOnlyRoute>
						<Signup />
					</PublicOnlyRoute>
				}
			/>
			<Route
				path="/login"
				element={
					<PublicOnlyRoute>
						<Login />
					</PublicOnlyRoute>
				}
			/>
			<Route
				path="/chat"
				element={
					<ProtectedRoute>
						<ChatPage />
					</ProtectedRoute>
				}
			/>
			<Route
				path="/group-chat"
				element={
					<ProtectedRoute>
						<GroupChatPage />
					</ProtectedRoute>
				}
			/>
			<Route
				path="/verify"
				element={
					<ProtectedRoute>
						<RequestInterface />
					</ProtectedRoute>
				}
			/>
			<Route path="/oauth-callback" element={<OAuthCallback />} />
			<Route path="*" element={<Navigate to="/chat" replace />} />
		</Routes>
	);
}
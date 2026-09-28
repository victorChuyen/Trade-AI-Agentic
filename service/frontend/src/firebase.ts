import { initializeApp, getApps, getApp } from 'firebase/app'
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  type User
} from 'firebase/auth'

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyCbrDs10N1Qqb7kII9keLN7uEW3UzCgpxo",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "opc-ai-trader.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "opc-ai-trader",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "opc-ai-trader.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "371100655035",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:371100655035:web:8fa8662a7703036872f89e",
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-0CLRVZ5LVV"
}

// Initialize Firebase
export const app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig)
export const auth = getAuth(app)
export const googleProvider = new GoogleAuthProvider()

export {
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  type User
}

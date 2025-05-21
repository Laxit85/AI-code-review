import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyC28eg9K4KVQd9pNRcgBakXoNoxLFH6QbI",
  authDomain: "code-review-56fde.firebaseapp.com",
  projectId: "code-review-56fde",
  storageBucket: "code-review-56fde.firebasestorage.app",
  messagingSenderId: "349090246891",
  appId: "1:349090246891:web:bb887b7361fcc7238e8eae",
  measurementId: "G-8ZM1CTGLXE"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

export { app, analytics };

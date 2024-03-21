"use client"
import { Header } from "../components/Header";
import { Submit } from "../components/Submit";

export default function Home() {
  return (
    <div className="flex flex-col px-4 items-center justify-center min-h-screen bg-white-500 overflow-x-hidden">
      <Header />
      <Submit />
    </div>
  );
}

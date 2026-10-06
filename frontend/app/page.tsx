"use client";

import { useState } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    if (!input.trim() || loading) return;
    const question = input;
    setMessages((prev) => [
      ...prev,
      { role: "user", content: question },
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
        }),
      });

      const data = await response.json();

      // setMessages((prev) => [
      //   ...prev,
      //   {
      //     role: "assistant",
      //     content: data.answer,
      //   },
      // ]);

      const answer = data.results
        .map(
          (result: {
            source: string;
            page: number;
            score: number;
            text: string;
      }, index: number) =>
      `Result ${index + 1}\n${result.source}\nPage ${result.page}\n\n${result.text}`
  )
  .join("\n\n--------------------------------\n\n");

setMessages((prev) => [
  ...prev,
  {
    role: "assistant",
    content: answer || "No relevant information found.",
  },
]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Unable to connect to the server.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-white text-black">
      <div className="mx-auto flex min-h-screen max-w-3xl flex-col">

        <header className="border-b px-6 py-4">
          <h1 className="text-lg font-medium">
            Marma Research
          </h1>
          <p className="text-sm text-gray-500">
            Ask questions about your documents
          </p>
        </header>

        <div className="flex-1 space-y-6 overflow-y-auto px-6 py-8">

          {messages.length === 0 && (
            <div className="flex min-h-[60vh] items-center justify-center">
              <p className="text-gray-400">
                Ask a question about your documents
              </p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={
                message.role === "user"
                  ? "ml-auto max-w-[80%] rounded-2xl bg-black px-4 py-3 text-white"
                  : "max-w-[80%] whitespace-pre-wrap text-gray-800"
              }
            >
              {message.content}
            </div>
          ))}

          {loading && (
            <div className="text-sm text-gray-400">
              Searching documents...
            </div>
          )}

        </div>

        <div className="border-t p-4">
          <div className="flex gap-2">

            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  sendMessage();
                }
              }}
              placeholder="Ask a question..."
              className="flex-1 rounded-xl border px-4 py-3 outline-none focus:border-black"
            />

            <button
              onClick={sendMessage}
              disabled={loading}
              className="rounded-xl bg-black px-5 py-3 text-white disabled:opacity-40"
            >
              Send
            </button>

          </div>
        </div>

      </div>
    </main>
  );
}
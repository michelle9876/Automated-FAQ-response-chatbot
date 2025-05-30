"use client"
import { useState, useEffect, useRef } from "react"
import { Button } from "../components/ui/Button"
import { Input } from "../components/ui/Input"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card"
import { Badge } from "../components/ui/Badge"
import { Send, MessageCircle, User, Bot } from "lucide-react"

export default function ChatBot() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleInputChange = (e) => setInput(e.target.value)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const newMessages = [...messages, { role: "user", content: input }]
    setMessages(newMessages)
    setInput("")
    setIsLoading(true)

    try {
      
      const res = await fetch("http://localhost:8000/chat?question=" +
            encodeURIComponent(input) +
            "&user_id=test", {
        method: "GET",
      })
      const data = await res.text();
      if (data) {
        let displayedText = "";
        const assistantMessage = { role: "assistant", content: "" };
        setMessages([...newMessages, assistantMessage]);
        
        // 타이핑 효과를 위한 인터벌 설정
        const intervalId = setInterval(() => {
          if (displayedText.length < data.length) {
            displayedText = data.slice(0, displayedText.length + 1);
            setMessages([...newMessages, { role: "assistant", content: displayedText }]);
          } else {
            clearInterval(intervalId);
          }
        }, 20); // 20ms 간격으로 한 글자씩 표시
      }
    } catch (err) {
      console.error("Error fetching chat:", err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuickQuestion = (question) => {
    setInput(question)
    setTimeout(() => {
      document.querySelector("form")?.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }))
    }, 0)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      <header className="bg-white shadow-sm border-b border-blue-100">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">N</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-800">FAQ 응대 챗봇</h1>
            <Badge variant="secondary" className="bg-blue-100 text-blue-700">AI 챗봇</Badge>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex justify-center">
          <div className="w-full max-w-4xl">
            <Card className="h-[600px] flex flex-col">
              <CardHeader className="bg-blue-600 text-white rounded-t-lg">
                <CardTitle className="flex items-center space-x-2">
                  <MessageCircle className="w-5 h-5" />
                  <span>AI 상담사와 대화하기</span>
                </CardTitle>
                <p className="text-blue-100 text-sm">궁금한 점을 언제든 물어보세요!</p>
              </CardHeader>

              <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                  <div className="text-center py-8">
                    <Bot className="w-12 h-12 text-blue-600 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">안녕하세요! 👋</h3>
                    <p className="text-gray-600">000 AI 상담사입니다. 무엇을 도와드릴까요?</p>
                    <div className="mt-6 grid grid-cols-2 gap-2">
                      {["로그인이 안돼요", "결제가 안돼요", "배송 조회", "환불 신청"].map((q, idx) => (
                        <Button key={idx} variant="outline" size="sm" onClick={() => handleQuickQuestion(q)} className="text-xs">
                          {q}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                {messages.map((message, idx) => (
                  <div key={idx} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`flex items-start space-x-2 max-w-[80%] ${message.role === "user" ? "flex-row-reverse space-x-reverse" : ""}`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${message.role === "user" ? "bg-blue-500" : "bg-blue-600"}`}>
                        {message.role === "user" ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
                      </div>
                      <div className={`p-3 rounded-lg ${message.role === "user" ? "bg-blue-500 text-white" : "bg-gray-100 text-gray-800"}`}>
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      </div>
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="flex items-start space-x-2">
                      <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                      <div className="bg-gray-100 p-3 rounded-lg">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </CardContent>

              <div className="p-4 border-t">
                <form onSubmit={handleSubmit} className="flex space-x-2">
                  <Input
                    name="message"
                    value={input}
                    onChange={handleInputChange}
                    placeholder="궁금한 점을 입력해주세요..."
                    className="flex-1"
                    disabled={isLoading}
                  />
                  <Button type="submit" disabled={isLoading} className="bg-blue-600 hover:bg-blue-700">
                    <Send className="w-4 h-4" />
                  </Button>
                </form>
                <p className="text-xs text-gray-500 mt-2 text-center">
                  AI가 답변하므로 정확하지 않을 수 있습니다. 정확한 정보는 (kimbg9876@gmail.com)로 문의해주세요.
                </p>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

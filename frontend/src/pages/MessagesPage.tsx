import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { messagesApi } from '../api/messages'
import type { Conversation, Message } from '../api/messages'
import { useAuthStore } from '../store/authStore'
import Spinner from '../components/ui/Spinner'

export default function MessagesPage() {
  const { user } = useAuthStore()
  const queryClient = useQueryClient()
  const [activeConvo, setActiveConvo] = useState<string | null>(null)
  const [newMessage, setNewMessage] = useState('')

  const { data: conversations, isLoading } = useQuery({
    queryKey: ['conversations'],
    queryFn: () => messagesApi.getConversations().then((r) => r.data),
  })

  const { data: messages } = useQuery({
    queryKey: ['messages', activeConvo],
    queryFn: () => messagesApi.getMessages(activeConvo!).then((r) => r.data),
    enabled: !!activeConvo,
    refetchInterval: 5000,
  })

  const sendMutation = useMutation({
    mutationFn: (body: string) => messagesApi.sendMessage(activeConvo!, body),
    onSuccess: () => {
      setNewMessage('')
      queryClient.invalidateQueries({ queryKey: ['messages', activeConvo] })
    },
  })

  const { data: contactRequests } = useQuery({
    queryKey: ['contactRequests'],
    queryFn: () => messagesApi.getMyContactRequests().then((r) => r.data),
  })

  const respondMutation = useMutation({
    mutationFn: ({ id, action }: { id: string; action: 'accepted' | 'declined' }) =>
      messagesApi.respondToContactRequest(id, action),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contactRequests'] })
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
  })

  if (isLoading) return <Spinner />

  const pendingRequests = contactRequests?.filter((r) => r.status === 'pending' && r.tenant_id === user?.id) || []

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold mb-6">Messages</h1>

      {/* Pending contact requests */}
      {pendingRequests.length > 0 && (
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-3">Pending Contact Requests</h2>
          <div className="space-y-2">
            {pendingRequests.map((req) => (
              <div key={req.id} className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Someone wants to contact you about a property</p>
                  <p className="text-xs text-gray-500">Expires: {new Date(req.expires_at).toLocaleDateString()}</p>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => respondMutation.mutate({ id: req.id, action: 'accepted' })}
                    className="bg-green-600 text-white text-sm px-3 py-1 rounded-lg hover:bg-green-700">Accept</button>
                  <button onClick={() => respondMutation.mutate({ id: req.id, action: 'declined' })}
                    className="bg-red-100 text-red-600 text-sm px-3 py-1 rounded-lg hover:bg-red-200">Decline</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-3 gap-4 min-h-[500px]">
        {/* Conversation List */}
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="p-3 border-b border-gray-200 font-semibold text-sm">Conversations</div>
          {conversations?.length ? (
            <div className="divide-y divide-gray-100">
              {conversations.map((convo: Conversation) => (
                <button
                  key={convo.contact_request.id}
                  onClick={() => setActiveConvo(convo.contact_request.id)}
                  className={`w-full text-left p-3 hover:bg-gray-50 ${
                    activeConvo === convo.contact_request.id ? 'bg-blue-50' : ''
                  }`}
                >
                  <p className="font-medium text-sm">{convo.other_user.first_name} {convo.other_user.last_name}</p>
                  {convo.last_message && (
                    <p className="text-xs text-gray-500 truncate">{convo.last_message.body}</p>
                  )}
                  {convo.unread_count > 0 && (
                    <span className="inline-block mt-1 bg-blue-600 text-white text-xs px-2 py-0.5 rounded-full">
                      {convo.unread_count}
                    </span>
                  )}
                </button>
              ))}
            </div>
          ) : (
            <p className="p-3 text-sm text-gray-500">No conversations yet</p>
          )}
        </div>

        {/* Message Thread */}
        <div className="md:col-span-2 bg-white rounded-lg border border-gray-200 flex flex-col">
          {activeConvo ? (
            <>
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {messages?.map((msg: Message) => (
                  <div key={msg.id} className={`flex ${msg.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-xs px-4 py-2 rounded-lg text-sm ${
                      msg.sender_id === user?.id
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      {msg.body}
                      <div className={`text-xs mt-1 ${
                        msg.sender_id === user?.id ? 'text-blue-200' : 'text-gray-400'
                      }`}>
                        {new Date(msg.created_at).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="border-t border-gray-200 p-3 flex gap-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && newMessage.trim() && sendMutation.mutate(newMessage)}
                  placeholder="Type a message..."
                  className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={() => newMessage.trim() && sendMutation.mutate(newMessage)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm"
                >
                  Send
                </button>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
              Select a conversation to start messaging
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

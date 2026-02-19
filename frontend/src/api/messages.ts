import client from './client'

export interface ContactRequest {
  id: string
  requester_id: string
  tenant_id: string
  property_id: string
  review_id: string | null
  status: string
  expires_at: string
  created_at: string
}

export interface Message {
  id: string
  thread_id: string
  sender_id: string
  body: string
  created_at: string
}

export interface Conversation {
  contact_request: ContactRequest
  other_user: { id: string; first_name: string; last_name: string }
  last_message?: Message
  unread_count: number
}

export const messagesApi = {
  getMyContactRequests: () =>
    client.get<ContactRequest[]>('/messages/contact-requests/my'),

  respondToContactRequest: (id: string, action: 'accepted' | 'declined') =>
    client.patch<ContactRequest>(`/messages/contact-requests/${id}`, { status: action }),

  getConversations: () =>
    client.get<Conversation[]>('/messages/conversations'),

  getMessages: (contactRequestId: string) =>
    client.get<Message[]>(`/messages/conversations/${contactRequestId}`),

  sendMessage: (contactRequestId: string, body: string) =>
    client.post<Message>(`/messages/conversations/${contactRequestId}`, { body }),
}
